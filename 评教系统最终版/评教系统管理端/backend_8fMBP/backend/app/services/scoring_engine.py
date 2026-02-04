"""
自动评分引擎

负责调用 Deepseek API 进行评分，处理否决项检查、加分项计算和等级映射。
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    MaterialSubmission, ScoringRecord, ScoringTemplate, 
    BonusItem, ScoringLog, SystemScoringConfig
)
from app.services.deepseek_api_client import DeepseekAPIClient, create_deepseek_client
from app.services.template_manager import TemplateManager
from app.utils.file_parser import FileParser

logger = logging.getLogger(__name__)


class ScoringEngineError(Exception):
    """评分引擎异常基类"""
    pass


class FileNotFoundError(ScoringEngineError):
    """文件未找到异常"""
    pass


class UnsupportedFileTypeError(ScoringEngineError):
    """不支持的文件类型异常"""
    pass


class ScoringFailedError(ScoringEngineError):
    """评分失败异常"""
    pass


class ScoringEngine:
    """
    自动评分引擎
    
    负责文件评分的完整流程：
    1. 文件解析
    2. 模板获取和提示词构建
    3. API调用
    4. 否决项检查
    5. 加分项计算
    6. 等级映射
    7. 结果存储
    """
    
    def __init__(self, api_client: Optional[DeepseekAPIClient] = None):
        """
        初始化评分引擎
        
        Args:
            api_client: Deepseek API 客户端，如果不提供则使用默认配置
        """
        self.api_client = api_client or create_deepseek_client()
        # 注意：TemplateManager需要数据库会话，在实际使用时会通过get_db()获取
        self.template_manager = None  # 延迟初始化
        self.file_parser = FileParser()
        
        # 等级映射配置
        self.grade_mapping = [
            (90, 100, "优秀"),
            (80, 89, "良好"), 
            (60, 79, "合格"),
            (0, 59, "不合格")
        ]
        
        logger.info("评分引擎初始化完成")
    
    def score_file(self, submission_id: int, bonus_items: Optional[List[Dict]] = None) -> Dict:
        """
        对单个文件进行评分
        
        Args:
            submission_id: 材料提交ID
            bonus_items: 加分项列表
        
        Returns:
            dict: 评分结果
        
        Raises:
            FileNotFoundError: 文件未找到
            UnsupportedFileTypeError: 不支持的文件类型
            ScoringFailedError: 评分失败
        """
        db = next(get_db())
        
        try:
            # 1. 获取文件信息
            submission = db.query(MaterialSubmission).filter(
                MaterialSubmission.submission_id == str(submission_id)
            ).first()
            
            if not submission:
                raise FileNotFoundError(f"未找到提交记录: {submission_id}")
            
            logger.info(f"开始评分文件: {submission.submission_id} (ID: {submission_id})")
            
            # 2. 解析文件内容 - 从files JSON中获取第一个文件
            if not submission.files or len(submission.files) == 0:
                raise FileNotFoundError(f"提交记录中没有文件: {submission_id}")
            
            # 获取第一个文件信息
            first_file = submission.files[0]
            file_name = first_file.get('file_name', 'unknown')
            file_url = first_file.get('file_url', '')
            
            # 如果有加密路径，使用加密路径，否则使用file_url
            file_path = submission.encrypted_path or file_url
            
            file_content = self._parse_file_content(file_path)
            
            # 3. 确定文件类型
            file_type = self._determine_file_type(file_name, file_content)
            
            # 4. 获取提示词模板并构建提示词
            prompt = self._build_scoring_prompt(file_type, file_content, file_name)
            
            # 5. 调用 API 进行评分
            api_result = self.api_client.call_api(prompt)
            
            # 6. 解析 API 结果
            parsed_result = self._parse_api_result(api_result)
            
            # 7. 检查否决项
            if parsed_result['veto_triggered']:
                final_result = self._create_veto_result(
                    submission_id, parsed_result, file_type
                )
            else:
                # 8. 计算加分项和最终得分
                final_result = self._calculate_final_score(
                    submission_id, parsed_result, bonus_items or [], file_type
                )
            
            # 9. 存储评分结果
            scoring_record = self._save_scoring_result(db, final_result, file_name)
            
            # 10. 记录评分日志
            self._log_scoring_activity(db, submission_id, "评分完成", final_result)
            
            logger.info(f"文件评分完成: {file_name}, 得分: {final_result['final_score']}, 等级: {final_result['grade']}")
            
            return final_result
            
        except (FileNotFoundError, UnsupportedFileTypeError) as e:
            # 让特定异常直接传播，不记录为评分失败
            raise e
        except Exception as e:
            logger.error(f"文件评分失败: {str(e)}")
            # 记录失败日志
            self._log_scoring_activity(db, submission_id, "评分失败", {"error": str(e)})
            raise ScoringFailedError(f"评分失败: {str(e)}")
        finally:
            db.close()
    
    def batch_score(self, submission_ids: List[int], bonus_items: Optional[List[Dict]] = None) -> List[Dict]:
        """
        批量评分
        
        Args:
            submission_ids: 提交ID列表
            bonus_items: 加分项列表
        
        Returns:
            list: 评分结果列表
        """
        results = []
        failed_count = 0
        
        logger.info(f"开始批量评分，共 {len(submission_ids)} 个文件")
        
        for submission_id in submission_ids:
            try:
                result = self.score_file(submission_id, bonus_items)
                results.append(result)
            except Exception as e:
                logger.error(f"批量评分中文件 {submission_id} 失败: {str(e)}")
                failed_count += 1
                results.append({
                    'submission_id': submission_id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"批量评分完成，成功: {len(submission_ids) - failed_count}, 失败: {failed_count}")
        
        return results
    
    def _parse_file_content(self, file_path: str) -> str:
        """
        解析文件内容
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 文件内容
        """
        try:
            return self.file_parser.parse_file(file_path)
        except Exception as e:
            raise ScoringFailedError(f"文件解析失败: {str(e)}")
    
    def _determine_file_type(self, file_name: str, content: str) -> str:
        """
        确定文件类型
        
        Args:
            file_name: 文件名
            content: 文件内容
        
        Returns:
            str: 文件类型
        """
        # 基于文件名和内容特征判断文件类型
        file_name_lower = file_name.lower()
        content_lower = content.lower()
        
        # 教案类型判断
        if any(keyword in file_name_lower for keyword in ['教案', 'lesson', 'plan']):
            return 'lesson_plan'
        elif any(keyword in content_lower for keyword in ['教学目标', '教学重点', '教学难点', '教学过程']):
            return 'lesson_plan'
        
        # 教学反思类型判断
        elif any(keyword in file_name_lower for keyword in ['反思', 'reflection']):
            return 'teaching_reflection'
        elif any(keyword in content_lower for keyword in ['教学反思', '反思总结', '教学体会']):
            return 'teaching_reflection'
        
        # 教研/听课记录类型判断
        elif any(keyword in file_name_lower for keyword in ['听课', '教研', 'research']):
            return 'teaching_research'
        elif any(keyword in content_lower for keyword in ['听课记录', '教研活动', '课堂观察']):
            return 'teaching_research'
        
        # 成绩/学情分析类型判断
        elif any(keyword in file_name_lower for keyword in ['成绩', '学情', 'grade', 'analysis']):
            return 'grade_analysis'
        elif any(keyword in content_lower for keyword in ['成绩分析', '学情分析', '学习情况']):
            return 'grade_analysis'
        
        # 课件类型判断
        elif any(keyword in file_name_lower for keyword in ['课件', 'courseware', 'ppt']):
            return 'courseware'
        elif file_name_lower.endswith(('.ppt', '.pptx')):
            return 'courseware'
        
        # 默认返回教案类型
        logger.warning(f"无法确定文件类型，使用默认类型: lesson_plan, 文件: {file_name}")
        return 'lesson_plan'
    
    def _build_scoring_prompt(self, file_type: str, content: str, file_name: str) -> str:
        """
        构建评分提示词
        
        Args:
            file_type: 文件类型
            content: 文件内容
            file_name: 文件名
        
        Returns:
            str: 评分提示词
        """
        try:
            # 获取数据库会话并初始化TemplateManager
            db = next(get_db())
            if not self.template_manager:
                self.template_manager = TemplateManager(db)
            
            return self.template_manager.build_prompt(file_type, content, file_name)
        except Exception as e:
            raise ScoringFailedError(f"构建提示词失败: {str(e)}")
        finally:
            if 'db' in locals():
                db.close()
    
    def _parse_api_result(self, api_result: Dict) -> Dict:
        """
        解析 API 返回结果
        
        Args:
            api_result: API 返回结果
        
        Returns:
            dict: 解析后的结果
        """
        return {
            'veto_triggered': api_result['veto_check']['triggered'],
            'veto_reason': api_result['veto_check'].get('reason', ''),
            'base_score': float(api_result['base_score']),
            'grade_suggestion': api_result['grade_suggestion'],
            'summary': api_result['summary'],
            'score_details': api_result['score_details']
        }
    
    def _create_veto_result(self, submission_id: int, parsed_result: Dict, file_type: str) -> Dict:
        """
        创建否决项触发的结果
        
        Args:
            submission_id: 提交ID
            parsed_result: 解析后的API结果
            file_type: 文件类型
        
        Returns:
            dict: 否决结果
        """
        return {
            'submission_id': submission_id,
            'file_type': file_type,
            'base_score': 0.0,
            'bonus_score': 0.0,
            'final_score': 0.0,
            'grade': '不合格',
            'veto_triggered': True,
            'veto_reason': parsed_result['veto_reason'],
            'summary': parsed_result['summary'],
            'score_details': parsed_result['score_details'],
            'bonus_details': [],
            'status': 'completed',
            'scored_at': datetime.now()
        }
    
    def _calculate_final_score(self, submission_id: int, parsed_result: Dict, 
                              bonus_items: List[Dict], file_type: str) -> Dict:
        """
        计算最终得分（基础分+加分项）
        
        Args:
            submission_id: 提交ID
            parsed_result: 解析后的API结果
            bonus_items: 加分项列表
            file_type: 文件类型
        
        Returns:
            dict: 最终评分结果
        """
        base_score = parsed_result['base_score']
        
        # 计算加分项
        bonus_score, bonus_details = self._calculate_bonus_score(bonus_items)
        
        # 计算最终得分（限制在100分以内）
        final_score = min(base_score + bonus_score, 100.0)
        
        # 确定等级
        grade = self.determine_grade(final_score)
        
        return {
            'submission_id': submission_id,
            'file_type': file_type,
            'base_score': base_score,
            'bonus_score': bonus_score,
            'final_score': final_score,
            'grade': grade,
            'veto_triggered': False,
            'veto_reason': '',
            'summary': parsed_result['summary'],
            'score_details': parsed_result['score_details'],
            'bonus_details': bonus_details,
            'status': 'completed',
            'scored_at': datetime.now()
        }
    
    def _calculate_bonus_score(self, bonus_items: List[Dict]) -> tuple:
        """
        计算加分项得分
        
        Args:
            bonus_items: 加分项列表
        
        Returns:
            tuple: (总加分, 加分明细)
        """
        if not bonus_items:
            return 0.0, []
        
        total_bonus = 0.0
        bonus_details = []
        
        for item in bonus_items:
            item_name = item.get('name', '')
            item_score = float(item.get('score', 0))
            item_description = item.get('description', '')
            
            # 限制单项加分不超过5分
            item_score = min(item_score, 5.0)
            total_bonus += item_score
            
            bonus_details.append({
                'name': item_name,
                'score': item_score,
                'description': item_description
            })
        
        # 限制总加分不超过10分
        if total_bonus > 10.0:
            # 按比例缩放
            scale_factor = 10.0 / total_bonus
            total_bonus = 10.0
            for detail in bonus_details:
                detail['score'] = detail['score'] * scale_factor
        
        return total_bonus, bonus_details
    
    def determine_grade(self, final_score: float) -> str:
        """
        根据得分确定等级
        
        Args:
            final_score: 最终得分
        
        Returns:
            str: 等级
        """
        # 使用更精确的边界判断
        if final_score >= 90:
            return "优秀"
        elif final_score >= 80:
            return "良好"
        elif final_score >= 60:
            return "合格"
        else:
            return "不合格"
    
    def _save_scoring_result(self, db: Session, result: Dict, file_name: str = None) -> ScoringRecord:
        """
        保存评分结果到数据库
        
        Args:
            db: 数据库会话
            result: 评分结果
            file_name: 文件名
        
        Returns:
            ScoringRecord: 评分记录
        """
        scoring_record = ScoringRecord(
            submission_id=str(result['submission_id']),
            file_id=str(result['submission_id']),  # 临时使用submission_id作为file_id
            file_type=result['file_type'],
            file_name=file_name or f"file_{result['submission_id']}",
            base_score=result['base_score'],
            bonus_score=result['bonus_score'],
            final_score=result['final_score'],
            grade=result['grade'],
            score_details=str(result['score_details']),  # 转换为字符串
            veto_triggered=result['veto_triggered'],
            veto_reason=result['veto_reason'],
            scoring_type="auto",
            scored_at=result['scored_at']
        )
        
        db.add(scoring_record)
        db.commit()
        db.refresh(scoring_record)
        
        return scoring_record
    
    def _log_scoring_activity(self, db: Session, submission_id: int, 
                             activity: str, details: Dict):
        """
        记录评分活动日志
        
        Args:
            db: 数据库会话
            submission_id: 提交ID
            activity: 活动描述
            details: 详细信息
        """
        log_entry = ScoringLog(
            action=activity,
            action_details=str(details),  # Convert dict to string
            related_id=str(submission_id),
            related_type="submission",
            created_at=datetime.now()
        )
        
        db.add(log_entry)
        db.commit()
    
    def get_scoring_result(self, submission_id: int) -> Optional[Dict]:
        """
        获取评分结果
        
        Args:
            submission_id: 提交ID
        
        Returns:
            dict: 评分结果，如果不存在返回None
        """
        db = next(get_db())
        
        try:
            record = db.query(ScoringRecord).filter(
                ScoringRecord.submission_id == submission_id
            ).first()
            
            if not record:
                return None
            
            return {
                'id': record.id,
                'submission_id': record.submission_id,
                'file_type': record.file_type,
                'base_score': record.base_score,
                'bonus_score': record.bonus_score,
                'final_score': record.final_score,
                'grade': record.grade,
                'veto_triggered': record.veto_triggered,
                'veto_reason': record.veto_reason,
                'summary': record.summary,
                'score_details': record.score_details,
                'bonus_details': record.bonus_details,
                'status': record.status,
                'scored_at': record.scored_at,
                'created_at': record.created_at
            }
        finally:
            db.close()
    
    def get_api_info(self) -> Dict:
        """
        获取API客户端信息
        
        Returns:
            dict: API信息
        """
        return self.api_client.get_api_info()


# 便利函数
def create_scoring_engine(api_client: Optional[DeepseekAPIClient] = None) -> ScoringEngine:
    """
    创建评分引擎实例
    
    Args:
        api_client: API客户端，如果不提供则使用默认配置
    
    Returns:
        ScoringEngine: 评分引擎实例
    """
    return ScoringEngine(api_client)