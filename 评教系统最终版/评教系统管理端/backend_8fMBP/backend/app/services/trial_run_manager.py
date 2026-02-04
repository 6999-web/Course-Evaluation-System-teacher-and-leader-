"""
试运行模式管理器

负责试运行模式的配置和管理，包括：
- 试运行模式开关
- 自动评分与预设标准的差异记录
- 差异报告生成
- 一致性报告生成
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models import (
    ScoringRecord, ReviewRecord, SystemScoringConfig,
    MaterialSubmission, ScoringLog
)

logger = logging.getLogger(__name__)


class TrialRunManagerError(Exception):
    """试运行管理器异常基类"""
    pass


class TrialRunManager:
    """
    试运行模式管理器
    
    负责试运行模式的配置和差异记录
    """
    
    def __init__(self, db: Session):
        """
        初始化试运行管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        logger.info("试运行管理器初始化完成")
    
    def is_trial_mode_enabled(self) -> bool:
        """
        检查试运行模式是否启用
        
        Returns:
            bool: 是否启用试运行模式
        """
        try:
            config = self.db.query(SystemScoringConfig).filter(
                SystemScoringConfig.config_key == "trial_mode_enabled"
            ).first()
            
            if config:
                return config.config_value.lower() == "true"
            
            # 如果没有配置，检查is_trial_mode字段
            config = self.db.query(SystemScoringConfig).first()
            if config:
                return config.is_trial_mode
            
            return False
            
        except Exception as e:
            logger.error(f"检查试运行模式失败: {str(e)}")
            return False
    
    def enable_trial_mode(self, admin_id: int) -> bool:
        """
        启用试运行模式
        
        Args:
            admin_id: 管理员ID
        
        Returns:
            bool: 是否启用成功
        """
        try:
            # 查找或创建配置
            config = self.db.query(SystemScoringConfig).filter(
                SystemScoringConfig.config_key == "trial_mode_enabled"
            ).first()
            
            if not config:
                config = SystemScoringConfig(
                    config_key="trial_mode_enabled",
                    config_value="true",
                    description="试运行模式开关",
                    is_trial_mode=True,
                    updated_by=admin_id
                )
                self.db.add(config)
            else:
                config.config_value = "true"
                config.is_trial_mode = True
                config.updated_by = admin_id
                config.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录日志
            self._log_activity(
                action="trial_mode_enabled",
                details={"admin_id": admin_id}
            )
            
            logger.info(f"试运行模式已启用，管理员: {admin_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"启用试运行模式失败: {str(e)}")
            raise TrialRunManagerError(f"启用试运行模式失败: {str(e)}")
    
    def disable_trial_mode(self, admin_id: int) -> bool:
        """
        禁用试运行模式
        
        Args:
            admin_id: 管理员ID
        
        Returns:
            bool: 是否禁用成功
        """
        try:
            # 查找配置
            config = self.db.query(SystemScoringConfig).filter(
                SystemScoringConfig.config_key == "trial_mode_enabled"
            ).first()
            
            if config:
                config.config_value = "false"
                config.is_trial_mode = False
                config.updated_by = admin_id
                config.updated_at = datetime.utcnow()
            else:
                config = SystemScoringConfig(
                    config_key="trial_mode_enabled",
                    config_value="false",
                    description="试运行模式开关",
                    is_trial_mode=False,
                    updated_by=admin_id
                )
                self.db.add(config)
            
            self.db.commit()
            
            # 记录日志
            self._log_activity(
                action="trial_mode_disabled",
                details={"admin_id": admin_id}
            )
            
            logger.info(f"试运行模式已禁用，管理员: {admin_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"禁用试运行模式失败: {str(e)}")
            raise TrialRunManagerError(f"禁用试运行模式失败: {str(e)}")
    
    def record_trial_run_difference(self, scoring_record_id: int, 
                                   auto_score: float, preset_score: float,
                                   difference_reason: str = "") -> bool:
        """
        记录试运行期间自动评分与预设标准的差异
        
        在试运行模式下，自动记录自动评分与预设标准的差异（无需人工复核）
        
        Args:
            scoring_record_id: 评分记录ID
            auto_score: 自动评分得分
            preset_score: 预设标准得分
            difference_reason: 差异原因
        
        Returns:
            bool: 是否记录成功
        """
        try:
            # 检查是否启用试运行模式
            if not self.is_trial_mode_enabled():
                logger.warning("试运行模式未启用，无法记录差异")
                return False
            
            # 获取评分记录
            scoring_record = self.db.query(ScoringRecord).filter(
                ScoringRecord.id == scoring_record_id
            ).first()
            
            if not scoring_record:
                raise TrialRunManagerError(f"评分记录不存在: {scoring_record_id}")
            
            # 计算差异
            difference = abs(auto_score - preset_score)
            is_consistent = difference < 0.1  # 差异小于0.1分认为一致
            
            # 创建复核记录（标记为试运行模式）
            review_record = ReviewRecord(
                scoring_record_id=scoring_record_id,
                review_type="trial_run",  # 标记为试运行模式
                original_score=auto_score,
                reviewed_score=preset_score,
                is_consistent=is_consistent,
                difference_reason=difference_reason or f"自动评分: {auto_score}, 预设标准: {preset_score}",
                reviewed_by=0,  # 系统自动记录
                reviewed_at=datetime.utcnow()
            )
            
            self.db.add(review_record)
            self.db.commit()
            
            # 记录日志
            self._log_activity(
                action="trial_run_difference_recorded",
                scoring_record_id=scoring_record_id,
                details={
                    "auto_score": auto_score,
                    "preset_score": preset_score,
                    "difference": difference,
                    "is_consistent": is_consistent,
                    "reason": difference_reason
                }
            )
            
            logger.info(f"试运行差异已记录: 评分记录 {scoring_record_id}, 差异 {difference:.2f}")
            return True
            
        except TrialRunManagerError as e:
            raise e
        except Exception as e:
            self.db.rollback()
            logger.error(f"记录试运行差异失败: {str(e)}")
            raise TrialRunManagerError(f"记录试运行差异失败: {str(e)}")
    
    def generate_trial_run_diff_report(self, start_date: str = None, 
                                      end_date: str = None) -> Dict[str, Any]:
        """
        生成试运行差异报告
        
        生成差异报告并保存到项目根目录/test_reports/trial_run_diff_report.md
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)，如果为None则使用最早的记录
            end_date: 结束日期 (YYYY-MM-DD)，如果为None则使用最新的记录
        
        Returns:
            dict: 报告统计信息
        """
        try:
            # 查询试运行模式下的所有差异记录
            query = self.db.query(ReviewRecord).filter(
                ReviewRecord.review_type == "trial_run"
            )
            
            # 如果指定了日期范围，则过滤
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ReviewRecord.reviewed_at >= start_dt)
            
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(ReviewRecord.reviewed_at < end_dt)
            
            review_records = query.order_by(ReviewRecord.reviewed_at.desc()).all()
            
            if not review_records:
                logger.warning("没有找到试运行差异记录")
                return {
                    "total_records": 0,
                    "consistent_count": 0,
                    "inconsistent_count": 0,
                    "consistency_rate": 0.0,
                    "report_path": None
                }
            
            # 统计数据
            total_records = len(review_records)
            consistent_count = sum(1 for r in review_records if r.is_consistent)
            inconsistent_count = total_records - consistent_count
            consistency_rate = consistent_count / total_records if total_records > 0 else 0.0
            
            # 统计差异原因
            difference_reasons = {}
            score_differences = []
            
            for record in review_records:
                # 统计差异原因
                if record.difference_reason:
                    reason = record.difference_reason.strip()
                    if reason:
                        difference_reasons[reason] = difference_reasons.get(reason, 0) + 1
                
                # 记录分数差异
                score_diff = abs(record.original_score - record.reviewed_score)
                score_differences.append({
                    "scoring_record_id": record.scoring_record_id,
                    "auto_score": record.original_score,
                    "preset_score": record.reviewed_score,
                    "difference": score_diff,
                    "is_consistent": record.is_consistent,
                    "reason": record.difference_reason,
                    "reviewed_at": record.reviewed_at.isoformat() if record.reviewed_at else None
                })
            
            # 计算分数差异统计
            score_diff_stats = {
                "max_difference": max(d["difference"] for d in score_differences),
                "min_difference": min(d["difference"] for d in score_differences),
                "avg_difference": sum(d["difference"] for d in score_differences) / len(score_differences)
            }
            
            # 生成报告
            report_content = self._generate_report_markdown(
                total_records=total_records,
                consistent_count=consistent_count,
                inconsistent_count=inconsistent_count,
                consistency_rate=consistency_rate,
                difference_reasons=difference_reasons,
                score_diff_stats=score_diff_stats,
                score_differences=score_differences,
                start_date=start_date,
                end_date=end_date
            )
            
            # 保存报告
            report_path = self._save_report(report_content, "trial_run_diff_report.md")
            
            # 记录日志
            self._log_activity(
                action="trial_run_diff_report_generated",
                details={
                    "total_records": total_records,
                    "consistency_rate": consistency_rate,
                    "report_path": str(report_path)
                }
            )
            
            logger.info(f"试运行差异报告已生成: {report_path}")
            
            return {
                "total_records": total_records,
                "consistent_count": consistent_count,
                "inconsistent_count": inconsistent_count,
                "consistency_rate": round(consistency_rate, 4),
                "difference_reasons": difference_reasons,
                "score_diff_stats": {
                    "max_difference": round(score_diff_stats["max_difference"], 2),
                    "min_difference": round(score_diff_stats["min_difference"], 2),
                    "avg_difference": round(score_diff_stats["avg_difference"], 2)
                },
                "report_path": str(report_path),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成试运行差异报告失败: {str(e)}")
            raise TrialRunManagerError(f"生成试运行差异报告失败: {str(e)}")
    
    def generate_consistency_report(self, start_date: str = None,
                                   end_date: str = None) -> Dict[str, Any]:
        """
        生成一致性报告
        
        实现一致性统计功能、差异原因分析、生成试运行报告
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            dict: 报告统计信息
        """
        try:
            # 查询所有复核记录（包括试运行和其他复核）
            query = self.db.query(ReviewRecord)
            
            # 如果指定了日期范围，则过滤
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ReviewRecord.reviewed_at >= start_dt)
            
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ReviewRecord.reviewed_at <= end_dt)
            
            review_records = query.order_by(ReviewRecord.reviewed_at.desc()).all()
            
            if not review_records:
                logger.warning("没有找到复核记录")
                return {
                    "total_reviews": 0,
                    "consistent_count": 0,
                    "inconsistent_count": 0,
                    "consistency_rate": 0.0,
                    "report_path": None
                }
            
            # 按复核类型分类统计
            review_type_stats = {}
            total_records = len(review_records)
            consistent_count = sum(1 for r in review_records if r.is_consistent)
            inconsistent_count = total_records - consistent_count
            consistency_rate = consistent_count / total_records if total_records > 0 else 0.0
            
            # 统计差异原因
            difference_reasons = {}
            difference_reason_by_type = {}
            
            for record in review_records:
                # 统计复核类型
                review_type = record.review_type
                if review_type not in review_type_stats:
                    review_type_stats[review_type] = {
                        "total": 0,
                        "consistent": 0,
                        "inconsistent": 0,
                        "consistency_rate": 0.0
                    }
                
                review_type_stats[review_type]["total"] += 1
                if record.is_consistent:
                    review_type_stats[review_type]["consistent"] += 1
                else:
                    review_type_stats[review_type]["inconsistent"] += 1
                
                # 统计差异原因
                if record.difference_reason:
                    reason = record.difference_reason.strip()
                    if reason:
                        difference_reasons[reason] = difference_reasons.get(reason, 0) + 1
                        
                        # 按类型统计差异原因
                        if review_type not in difference_reason_by_type:
                            difference_reason_by_type[review_type] = {}
                        difference_reason_by_type[review_type][reason] = \
                            difference_reason_by_type[review_type].get(reason, 0) + 1
            
            # 计算各类型的一致性比例
            for review_type, stats in review_type_stats.items():
                if stats["total"] > 0:
                    stats["consistency_rate"] = round(stats["consistent"] / stats["total"], 4)
            
            # 生成报告
            report_content = self._generate_consistency_report_markdown(
                total_reviews=total_records,
                consistent_count=consistent_count,
                inconsistent_count=inconsistent_count,
                consistency_rate=consistency_rate,
                review_type_stats=review_type_stats,
                difference_reasons=difference_reasons,
                difference_reason_by_type=difference_reason_by_type,
                start_date=start_date,
                end_date=end_date
            )
            
            # 保存报告
            report_path = self._save_report(report_content, "consistency_report.md")
            
            # 记录日志
            self._log_activity(
                action="consistency_report_generated",
                details={
                    "total_reviews": total_records,
                    "consistency_rate": consistency_rate,
                    "report_path": str(report_path)
                }
            )
            
            logger.info(f"一致性报告已生成: {report_path}")
            
            return {
                "total_reviews": total_records,
                "consistent_count": consistent_count,
                "inconsistent_count": inconsistent_count,
                "consistency_rate": round(consistency_rate, 4),
                "review_type_stats": review_type_stats,
                "difference_reasons": difference_reasons,
                "report_path": str(report_path),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成一致性报告失败: {str(e)}")
            raise TrialRunManagerError(f"生成一致性报告失败: {str(e)}")
    
    def _generate_report_markdown(self, total_records: int, consistent_count: int,
                                 inconsistent_count: int, consistency_rate: float,
                                 difference_reasons: Dict, score_diff_stats: Dict,
                                 score_differences: List, start_date: str = None,
                                 end_date: str = None) -> str:
        """
        生成试运行差异报告的Markdown内容
        
        Args:
            total_records: 总记录数
            consistent_count: 一致数量
            inconsistent_count: 不一致数量
            consistency_rate: 一致性比例
            difference_reasons: 差异原因统计
            score_diff_stats: 分数差异统计
            score_differences: 分数差异详情列表
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            str: Markdown格式的报告内容
        """
        report = []
        report.append("# 试运行差异报告\n")
        report.append(f"生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if start_date or end_date:
            date_range = f"{start_date or '开始'} 至 {end_date or '现在'}"
            report.append(f"统计周期: {date_range}\n")
        
        report.append("\n## 概览\n")
        report.append(f"- 总记录数: {total_records}\n")
        report.append(f"- 一致数量: {consistent_count}\n")
        report.append(f"- 不一致数量: {inconsistent_count}\n")
        report.append(f"- 一致性比例: {consistency_rate:.2%}\n")
        
        report.append("\n## 分数差异统计\n")
        report.append(f"- 最大差异: {score_diff_stats['max_difference']:.2f}分\n")
        report.append(f"- 最小差异: {score_diff_stats['min_difference']:.2f}分\n")
        report.append(f"- 平均差异: {score_diff_stats['avg_difference']:.2f}分\n")
        
        if difference_reasons:
            report.append("\n## 差异原因分析\n")
            sorted_reasons = sorted(difference_reasons.items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons:
                percentage = (count / total_records) * 100
                report.append(f"- {reason}: {count}条 ({percentage:.1f}%)\n")
        
        report.append("\n## 详细差异列表\n")
        report.append("| 评分记录ID | 自动评分 | 预设标准 | 差异 | 一致性 | 原因 | 时间 |\n")
        report.append("|-----------|---------|---------|------|--------|------|------|\n")
        
        for diff in score_differences[:100]:  # 只显示前100条
            consistency = "✓" if diff["is_consistent"] else "✗"
            reason = diff["reason"][:30] if diff["reason"] else "-"
            report.append(
                f"| {diff['scoring_record_id']} | {diff['auto_score']:.2f} | "
                f"{diff['preset_score']:.2f} | {diff['difference']:.2f} | {consistency} | "
                f"{reason} | {diff['reviewed_at'][:10] if diff['reviewed_at'] else '-'} |\n"
            )
        
        if len(score_differences) > 100:
            report.append(f"\n*注: 共有 {len(score_differences)} 条记录，仅显示前100条*\n")
        
        return "".join(report)
    
    def _generate_consistency_report_markdown(self, total_reviews: int, consistent_count: int,
                                            inconsistent_count: int, consistency_rate: float,
                                            review_type_stats: Dict, difference_reasons: Dict,
                                            difference_reason_by_type: Dict,
                                            start_date: str = None, end_date: str = None) -> str:
        """
        生成一致性报告的Markdown内容
        
        Args:
            total_reviews: 总复核数
            consistent_count: 一致数量
            inconsistent_count: 不一致数量
            consistency_rate: 一致性比例
            review_type_stats: 按复核类型的统计
            difference_reasons: 差异原因统计
            difference_reason_by_type: 按类型的差异原因统计
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            str: Markdown格式的报告内容
        """
        report = []
        report.append("# 一致性报告\n")
        report.append(f"生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if start_date or end_date:
            date_range = f"{start_date or '开始'} 至 {end_date or '现在'}"
            report.append(f"统计周期: {date_range}\n")
        
        report.append("\n## 总体统计\n")
        report.append(f"- 总复核数: {total_reviews}\n")
        report.append(f"- 一致数量: {consistent_count}\n")
        report.append(f"- 不一致数量: {inconsistent_count}\n")
        report.append(f"- 一致性比例: {consistency_rate:.2%}\n")
        
        if review_type_stats:
            report.append("\n## 按复核类型统计\n")
            report.append("| 复核类型 | 总数 | 一致 | 不一致 | 一致性比例 |\n")
            report.append("|---------|------|------|--------|----------|\n")
            
            for review_type, stats in review_type_stats.items():
                report.append(
                    f"| {review_type} | {stats['total']} | {stats['consistent']} | "
                    f"{stats['inconsistent']} | {stats['consistency_rate']:.2%} |\n"
                )
        
        if difference_reasons:
            report.append("\n## 差异原因分析\n")
            sorted_reasons = sorted(difference_reasons.items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons:
                percentage = (count / total_reviews) * 100
                report.append(f"- {reason}: {count}条 ({percentage:.1f}%)\n")
        
        if difference_reason_by_type:
            report.append("\n## 按复核类型的差异原因\n")
            for review_type, reasons in difference_reason_by_type.items():
                report.append(f"\n### {review_type}\n")
                sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)
                for reason, count in sorted_reasons:
                    report.append(f"- {reason}: {count}条\n")
        
        report.append("\n## 建议\n")
        if consistency_rate >= 0.95:
            report.append("- ✓ 一致性达到95%以上，系统评分准确性高，可考虑切换到正式运行模式\n")
        else:
            report.append(f"- ⚠ 一致性为{consistency_rate:.2%}，低于95%目标，建议继续优化评分标准\n")
            if difference_reasons:
                top_reason = sorted_reasons[0][0]
                report.append(f"- 主要差异原因是: {top_reason}，建议重点关注\n")
        
        return "".join(report)
    
    def _save_report(self, content: str, filename: str) -> Path:
        """
        保存报告到文件
        
        Args:
            content: 报告内容
            filename: 文件名
        
        Returns:
            Path: 报告文件路径
        """
        try:
            # 创建test_reports目录
            report_dir = Path(__file__).parent.parent.parent / "test_reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存报告
            report_path = report_dir / filename
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"报告已保存: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"保存报告失败: {str(e)}")
            raise TrialRunManagerError(f"保存报告失败: {str(e)}")
    
    def _log_activity(self, action: str, scoring_record_id: Optional[int] = None,
                     details: Optional[Dict] = None) -> None:
        """
        记录活动日志
        
        Args:
            action: 操作类型
            scoring_record_id: 评分记录ID
            details: 详细信息
        """
        try:
            log_entry = ScoringLog(
                scoring_record_id=scoring_record_id,
                action=action,
                action_by=None,
                action_details=json.dumps(details, ensure_ascii=False) if details else None,
                created_at=datetime.utcnow()
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"记录活动日志失败: {str(e)}")
            # 日志记录失败不应该影响主流程


def create_trial_run_manager(db: Session) -> TrialRunManager:
    """
    创建试运行管理器实例
    
    Args:
        db: 数据库会话
    
    Returns:
        TrialRunManager: 试运行管理器实例
    """
    return TrialRunManager(db)
