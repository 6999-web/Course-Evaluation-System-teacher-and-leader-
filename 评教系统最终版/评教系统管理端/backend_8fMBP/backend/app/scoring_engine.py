"""
自动评分引擎
负责调用 DeepSeek API 进行评分并处理结果
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from .deepseek_client import DeepseekAPIClient

logger = logging.getLogger(__name__)


class ScoringEngine:
    """自动评分引擎"""
    
    # 评分模板
    TEMPLATES = {
        "教案": {
            "name": "教案",
            "indicators": [
                {"name": "教学目标", "weight": 25},
                {"name": "教学内容", "weight": 25},
                {"name": "教学方法", "weight": 25},
                {"name": "教学评价", "weight": 25}
            ],
            "veto_items": {
                "general": ["造假", "师德失范", "未提交核心文件"],
                "specific": ["教学目标完全缺失", "教学内容存在严重知识性错误"]
            }
        },
        "教学反思": {
            "name": "教学反思",
            "indicators": [
                {"name": "反思深度", "weight": 30},
                {"name": "反思内容", "weight": 30},
                {"name": "改进措施", "weight": 25},
                {"name": "理论支撑", "weight": 15}
            ],
            "veto_items": {
                "general": ["造假", "师德失范", "未提交核心文件"],
                "specific": ["反思内容与教学完全无关", "反思内容过于简单"]
            }
        },
        "教研/听课记录": {
            "name": "教研/听课记录",
            "indicators": [
                {"name": "记录完整性", "weight": 25},
                {"name": "观察分析", "weight": 30},
                {"name": "评价建议", "weight": 30},
                {"name": "专业性", "weight": 15}
            ],
            "veto_items": {
                "general": ["造假", "师德失范", "未提交核心文件"],
                "specific": ["记录内容与教研/听课完全无关", "缺少基本信息"]
            }
        },
        "成绩/学情分析": {
            "name": "成绩/学情分析",
            "indicators": [
                {"name": "数据完整性", "weight": 20},
                {"name": "分析深度", "weight": 35},
                {"name": "改进措施", "weight": 30},
                {"name": "专业性", "weight": 15}
            ],
            "veto_items": {
                "general": ["造假", "师德失范", "未提交核心文件"],
                "specific": ["分析内容与成绩/学情完全无关", "缺少数据支撑"]
            }
        },
        "课件": {
            "name": "课件",
            "indicators": [
                {"name": "内容质量", "weight": 25},
                {"name": "设计美观", "weight": 25},
                {"name": "媒体运用", "weight": 25},
                {"name": "教学适用性", "weight": 25}
            ],
            "veto_items": {
                "general": ["造假", "师德失范", "未提交核心文件"],
                "specific": ["课件内容与教学主题完全无关", "课件内容存在严重知识性错误"]
            }
        }
    }
    
    def __init__(self, api_key: str, api_url: str = "https://api.deepseek.com/v1/chat/completions"):
        """
        初始化评分引擎
        
        Args:
            api_key: DeepSeek API 密钥
            api_url: DeepSeek API 地址
        """
        self.api_client = DeepseekAPIClient(api_key, api_url)
    
    def build_prompt(self, file_type: str, content: str, total_score: int = 100, 
                     scoring_criteria: Optional[List[Dict]] = None, bonus_rules: Optional[Dict] = None) -> str:
        """
        构建评分提示词
        
        Args:
            file_type: 文件类型
            content: 文件内容
            total_score: 考评表总分（默认100分）
            scoring_criteria: 考评表评分标准 [{"name": "完成度", "max_score": 10}, ...]
            bonus_rules: 加分项规则
            
        Returns:
            完整的提示词
        """
        # 如果提供了自定义评分标准，使用自定义标准；否则使用默认模板
        if scoring_criteria and len(scoring_criteria) > 0:
            # 使用考评表的自定义评分标准
            indicators_desc = "\n".join([
                f"{i+1}. {criterion['name']}（{criterion.get('max_score', 0)}分）"
                for i, criterion in enumerate(scoring_criteria)
            ])
            template_name = file_type
            
            # 使用通用的否决项
            veto_general = "造假、师德失范、未提交核心文件"
            veto_specific = "内容与主题完全无关、内容过于简单或缺失"
        else:
            # 使用默认模板
            template = self.TEMPLATES.get(file_type)
            if not template:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            # 根据总分调整指标权重
            scale_factor = total_score / 100.0
            indicators_desc = "\n".join([
                f"{i+1}. {ind['name']}（{int(ind['weight'] * scale_factor)}分）"
                for i, ind in enumerate(template['indicators'])
            ])
            template_name = template['name']
            
            # 构建否决项描述
            veto_general = "、".join(template['veto_items']['general'])
            veto_specific = "、".join(template['veto_items']['specific'])
        
        # 计算等级标准（按总分比例）
        excellent_threshold = int(total_score * 0.9)  # 90%
        good_threshold = int(total_score * 0.8)       # 80%
        pass_threshold = int(total_score * 0.6)       # 60%
        
        prompt = f"""你是一位专业的教学评估专家，请根据以下标准对{template_name}进行评分。

【评分规则】
1. 首先检查一票否决项，如果触发则直接判定为不合格
2. 如果未触发否决项，则按核心指标进行评分
3. 总分{total_score}分，按指标权重分配
4. 最终得分将加上加分项（最多{int(total_score * 0.1)}分）

【一票否决项】
通用否决项：
- {veto_general}

专项否决项：
- {veto_specific}

【核心指标】（总分{total_score}分）
{indicators_desc}

【等级标准】
- 优秀：{excellent_threshold}-{total_score}分
- 良好：{good_threshold}-{excellent_threshold-1}分
- 合格：{pass_threshold}-{good_threshold-1}分
- 不合格：<{pass_threshold}分

【待评分{template_name}内容】
{content}

【输出格式要求】
请严格按照以下JSON格式输出评分结果：
{{
    "veto_check": {{
        "triggered": false,
        "reason": ""
    }},
    "score_details": [
        {{
            "indicator": "指标名称",
            "score": 分数,
            "max_score": 满分,
            "reason": "评分理由"
        }}
    ],
    "base_score": 总分,
    "grade_suggestion": "等级",
    "summary": "总体评价和改进建议（请按以下结构化格式输出）：\n\n【总体评价】\n简要总结整体表现（2-3句话）\n\n【专业反思深度】\n分析教师对教学实践的反思是否深入、系统，是否能够从理论层面进行分析，是否触及教学本质问题。\n• 反思的系统性和深度\n• 理论分析的水平\n• 对教学本质的认识\n\n【改进措施可操作性】\n评估提出的改进措施是否具体、可行，是否有明确的实施步骤和时间节点，是否考虑了实际教学条件。\n• 措施的具体性和可行性\n• 实施步骤的清晰度\n• 与实际条件的匹配度\n\n【专业发展规划】\n考察教师是否有明确的专业成长目标，是否制定了短期、中期、长期发展计划，是否体现了持续学习和自我提升的意识。\n• 发展目标的明确性\n• 发展计划的完整性\n• 持续学习的意识"
}}
"""
        return prompt
    
    def score_file(self, file_type: str, content: str, total_score: int = 100,
                   scoring_criteria: Optional[List[Dict]] = None, bonus_items: Optional[List[Dict]] = None) -> Dict:
        """
        对文件进行评分
        
        Args:
            file_type: 文件类型
            content: 文件内容
            total_score: 考评表总分（默认100分）
            scoring_criteria: 考评表评分标准
            bonus_items: 加分项列表
            
        Returns:
            评分结果
        """
        try:
            # 验证文件类型（如果没有自定义标准，则需要验证）
            if not scoring_criteria and file_type not in self.TEMPLATES:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            # 验证内容
            if not content or content.strip() == "":
                return {
                    "success": False,
                    "error": "文件内容为空",
                    "veto_triggered": True,
                    "veto_reason": "未提交核心文件（文件内容为空）",
                    "final_score": 0,
                    "grade": "不合格"
                }
            
            # 构建提示词
            prompt = self.build_prompt(file_type, content, total_score, scoring_criteria)
            
            # 调用 API
            logger.info(f"开始评分 {file_type}，总分: {total_score}分...")
            api_response = self.api_client.call_api(prompt)
            
            if not api_response.get("success"):
                raise Exception(f"API 调用失败: {api_response.get('error', '未知错误')}")
            
            # 解析响应
            response_text = api_response.get("content", "")
            parsed_result = self.api_client.parse_response(response_text)
            
            # 验证响应格式
            self.api_client.validate_response(parsed_result)
            
            # 检查否决项
            veto_check = parsed_result.get("veto_check", {})
            if veto_check.get("triggered"):
                return {
                    "success": True,
                    "veto_triggered": True,
                    "veto_reason": veto_check.get("reason", "触发否决项"),
                    "base_score": 0,
                    "final_score": 0,
                    "grade": "不合格",
                    "score_details": parsed_result.get("score_details", []),
                    "summary": parsed_result.get("summary", "")
                }
            
            # 获取基础分
            base_score = parsed_result.get("base_score", 0)
            
            # 计算加分项（最多为总分的10%）
            max_bonus = int(total_score * 0.1)
            bonus_score = 0
            bonus_details = []
            if bonus_items:
                for item in bonus_items:
                    score = item.get("score", 0)
                    bonus_score += score
                    bonus_details.append({
                        "name": item.get("name", ""),
                        "score": score
                    })
            
            # 限制加分不超过总分的10%
            if bonus_score > max_bonus:
                bonus_score = max_bonus
            
            # 计算最终分数（不超过总分）
            final_score = min(base_score + bonus_score, total_score)
            
            # 确定等级（根据总分比例）
            grade = self.determine_grade(final_score, total_score)
            
            return {
                "success": True,
                "veto_triggered": False,
                "base_score": base_score,
                "bonus_score": bonus_score,
                "bonus_details": bonus_details,
                "final_score": final_score,
                "grade": grade,
                "score_details": parsed_result.get("score_details", []),
                "summary": parsed_result.get("summary", "")
            }
            
        except Exception as e:
            logger.error(f"评分失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "final_score": 0,
                "grade": "评分失败"
            }
    
    def determine_grade(self, score: float, total_score: int = 100) -> str:
        """
        根据分数确定等级
        
        Args:
            score: 分数
            total_score: 总分
            
        Returns:
            等级
        """
        percentage = (score / total_score) * 100
        
        if percentage >= 90:
            return "优秀"
        elif percentage >= 80:
            return "良好"
        elif percentage >= 60:
            return "合格"
        else:
            return "不合格"
