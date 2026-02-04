"""
提示词模板管理器

负责管理5类教学文件的评分标准模板，包括：
- 教案
- 教学反思
- 教研/听课记录
- 成绩/学情分析
- 课件
"""

import json
import logging
from typing import Optional, Dict, List
from datetime import datetime

from sqlalchemy.orm import Session
from app.models import ScoringTemplate

logger = logging.getLogger(__name__)


# 教案评分模板
LESSON_PLAN_TEMPLATE = {
    "file_type": "教案",
    "grade_standards": {
        "excellent": {"min": 90, "max": 100},
        "good": {"min": 80, "max": 89},
        "pass": {"min": 60, "max": 79},
        "fail": {"min": 0, "max": 59}
    },
    "core_indicators": [
        {
            "name": "教学目标",
            "weight": 25,
            "description": "目标明确具体、符合课程标准、关注学生发展",
            "sub_indicators": [
                {"name": "目标明确具体", "score": 10},
                {"name": "符合课程标准", "score": 8},
                {"name": "关注学生发展", "score": 7}
            ]
        },
        {
            "name": "教学内容",
            "weight": 25,
            "description": "内容准确完整、重难点突出、组织合理",
            "sub_indicators": [
                {"name": "内容准确完整", "score": 10},
                {"name": "重难点突出", "score": 8},
                {"name": "组织合理", "score": 7}
            ]
        },
        {
            "name": "教学方法",
            "weight": 25,
            "description": "方法适切有效、体现学生主体、手段多样",
            "sub_indicators": [
                {"name": "方法适切有效", "score": 10},
                {"name": "体现学生主体", "score": 8},
                {"name": "手段多样", "score": 7}
            ]
        },
        {
            "name": "教学评价",
            "weight": 25,
            "description": "评价方式多元、标准明确、关注过程",
            "sub_indicators": [
                {"name": "评价方式多元", "score": 10},
                {"name": "标准明确", "score": 8},
                {"name": "关注过程", "score": 7}
            ]
        }
    ],
    "veto_items": {
        "general": [
            "存在造假行为（抄袭、伪造数据等）",
            "存在师德失范内容",
            "未提交核心文件或文件内容为空"
        ],
        "specific": [
            "教学目标完全缺失",
            "教学内容存在严重知识性错误",
            "教学方法完全不适合教学内容"
        ]
    },
    "bonus_rules": {
        "max_bonus": 10,
        "items": [
            {"name": "获奖", "max_score": 5},
            {"name": "创新", "max_score": 5}
        ]
    },
    "output_format": {
        "veto_check": "是否触发否决项",
        "score_details": "各指标得分明细",
        "base_score": "基础分",
        "grade_suggestion": "等级建议",
        "summary": "总体评价和改进建议"
    }
}

# 教学反思评分模板
TEACHING_REFLECTION_TEMPLATE = {
    "file_type": "教学反思",
    "grade_standards": {
        "excellent": {"min": 90, "max": 100},
        "good": {"min": 80, "max": 89},
        "pass": {"min": 60, "max": 79},
        "fail": {"min": 0, "max": 59}
    },
    "core_indicators": [
        {
            "name": "反思深度",
            "weight": 30,
            "description": "问题分析深入、原因剖析透彻",
            "sub_indicators": [
                {"name": "问题分析深入", "score": 15},
                {"name": "原因剖析透彻", "score": 15}
            ]
        },
        {
            "name": "反思内容",
            "weight": 30,
            "description": "案例具体真实、覆盖全面",
            "sub_indicators": [
                {"name": "案例具体真实", "score": 15},
                {"name": "覆盖全面", "score": 15}
            ]
        },
        {
            "name": "改进措施",
            "weight": 25,
            "description": "措施具体可行、针对性强",
            "sub_indicators": [
                {"name": "措施具体可行", "score": 15},
                {"name": "针对性强", "score": 10}
            ]
        },
        {
            "name": "理论支撑",
            "weight": 15,
            "description": "理论联系实际、专业性强",
            "sub_indicators": [
                {"name": "理论联系实际", "score": 10},
                {"name": "专业性强", "score": 5}
            ]
        }
    ],
    "veto_items": {
        "general": [
            "存在造假行为（抄袭、伪造数据等）",
            "存在师德失范内容",
            "未提交核心文件或文件内容为空"
        ],
        "specific": [
            "反思内容与教学完全无关",
            "反思内容过于简单（少于200字）",
            "完全没有具体教学案例"
        ]
    },
    "bonus_rules": {
        "max_bonus": 10,
        "items": [
            {"name": "获奖", "max_score": 5},
            {"name": "创新", "max_score": 5}
        ]
    },
    "output_format": {
        "veto_check": "是否触发否决项",
        "score_details": "各指标得分明细",
        "base_score": "基础分",
        "grade_suggestion": "等级建议",
        "summary": "总体评价和改进建议"
    }
}

# 教研/听课记录评分模板
TEACHING_RESEARCH_TEMPLATE = {
    "file_type": "教研/听课记录",
    "grade_standards": {
        "excellent": {"min": 90, "max": 100},
        "good": {"min": 80, "max": 89},
        "pass": {"min": 60, "max": 79},
        "fail": {"min": 0, "max": 59}
    },
    "core_indicators": [
        {
            "name": "记录完整性",
            "weight": 25,
            "description": "基本信息完整、过程记录详细",
            "sub_indicators": [
                {"name": "基本信息完整", "score": 10},
                {"name": "过程记录详细", "score": 15}
            ]
        },
        {
            "name": "观察分析",
            "weight": 30,
            "description": "观察细致、分析到位",
            "sub_indicators": [
                {"name": "观察细致", "score": 15},
                {"name": "分析到位", "score": 15}
            ]
        },
        {
            "name": "评价建议",
            "weight": 30,
            "description": "评价客观公正、建议具体可行",
            "sub_indicators": [
                {"name": "评价客观公正", "score": 15},
                {"name": "建议具体可行", "score": 15}
            ]
        },
        {
            "name": "专业性",
            "weight": 15,
            "description": "专业术语准确、理论依据充分",
            "sub_indicators": [
                {"name": "专业术语准确", "score": 8},
                {"name": "理论依据充分", "score": 7}
            ]
        }
    ],
    "veto_items": {
        "general": [
            "存在造假行为（抄袭、伪造数据等）",
            "存在师德失范内容",
            "未提交核心文件或文件内容为空"
        ],
        "specific": [
            "记录内容与教研/听课完全无关",
            "记录过于简单（少于300字）",
            "缺少基本信息（时间、地点、参与人员等）"
        ]
    },
    "bonus_rules": {
        "max_bonus": 10,
        "items": [
            {"name": "获奖", "max_score": 5},
            {"name": "创新", "max_score": 5}
        ]
    },
    "output_format": {
        "veto_check": "是否触发否决项",
        "score_details": "各指标得分明细",
        "base_score": "基础分",
        "grade_suggestion": "等级建议",
        "summary": "总体评价和改进建议"
    }
}

# 成绩/学情分析评分模板
GRADE_ANALYSIS_TEMPLATE = {
    "file_type": "成绩/学情分析",
    "grade_standards": {
        "excellent": {"min": 90, "max": 100},
        "good": {"min": 80, "max": 89},
        "pass": {"min": 60, "max": 79},
        "fail": {"min": 0, "max": 59}
    },
    "core_indicators": [
        {
            "name": "数据完整性",
            "weight": 20,
            "description": "数据真实准确、呈现清晰",
            "sub_indicators": [
                {"name": "数据真实准确", "score": 10},
                {"name": "呈现清晰", "score": 10}
            ]
        },
        {
            "name": "分析深度",
            "weight": 35,
            "description": "整体分析到位、个体差异关注、原因分析深入",
            "sub_indicators": [
                {"name": "整体分析到位", "score": 15},
                {"name": "个体差异关注", "score": 10},
                {"name": "原因分析深入", "score": 10}
            ]
        },
        {
            "name": "改进措施",
            "weight": 30,
            "description": "措施针对性强、可操作性强",
            "sub_indicators": [
                {"name": "措施针对性强", "score": 15},
                {"name": "可操作性强", "score": 15}
            ]
        },
        {
            "name": "专业性",
            "weight": 15,
            "description": "使用专业方法、理论依据充分",
            "sub_indicators": [
                {"name": "使用专业方法", "score": 8},
                {"name": "理论依据充分", "score": 7}
            ]
        }
    ],
    "veto_items": {
        "general": [
            "存在造假行为（抄袭、伪造数据等）",
            "存在师德失范内容",
            "未提交核心文件或文件内容为空"
        ],
        "specific": [
            "分析内容与成绩/学情完全无关",
            "缺少数据支撑",
            "分析过于简单（少于400字）"
        ]
    },
    "bonus_rules": {
        "max_bonus": 10,
        "items": [
            {"name": "获奖", "max_score": 5},
            {"name": "创新", "max_score": 5}
        ]
    },
    "output_format": {
        "veto_check": "是否触发否决项",
        "score_details": "各指标得分明细",
        "base_score": "基础分",
        "grade_suggestion": "等级建议",
        "summary": "总体评价和改进建议"
    }
}

# 课件评分模板
COURSEWARE_TEMPLATE = {
    "file_type": "课件",
    "grade_standards": {
        "excellent": {"min": 90, "max": 100},
        "good": {"min": 80, "max": 89},
        "pass": {"min": 60, "max": 79},
        "fail": {"min": 0, "max": 59}
    },
    "core_indicators": [
        {
            "name": "内容质量",
            "weight": 25,
            "description": "内容准确完整、重难点突出、逻辑清晰",
            "sub_indicators": [
                {"name": "内容准确完整", "score": 10},
                {"name": "重难点突出", "score": 8},
                {"name": "逻辑清晰", "score": 7}
            ]
        },
        {
            "name": "设计美观",
            "weight": 25,
            "description": "版式设计合理、色彩搭配协调、字体大小适中",
            "sub_indicators": [
                {"name": "版式设计合理", "score": 10},
                {"name": "色彩搭配协调", "score": 8},
                {"name": "字体大小适中", "score": 7}
            ]
        },
        {
            "name": "媒体运用",
            "weight": 25,
            "description": "图片使用恰当、动画效果适度、多媒体丰富",
            "sub_indicators": [
                {"name": "图片使用恰当", "score": 10},
                {"name": "动画效果适度", "score": 8},
                {"name": "多媒体丰富", "score": 7}
            ]
        },
        {
            "name": "教学适用性",
            "weight": 25,
            "description": "符合学生特点、便于教学使用、互动性强",
            "sub_indicators": [
                {"name": "符合学生特点", "score": 10},
                {"name": "便于教学使用", "score": 8},
                {"name": "互动性强", "score": 7}
            ]
        }
    ],
    "veto_items": {
        "general": [
            "存在造假行为（抄袭、伪造数据等）",
            "存在师德失范内容",
            "未提交核心文件或文件内容为空"
        ],
        "specific": [
            "课件内容与教学主题完全无关",
            "课件内容存在严重知识性错误",
            "课件页数过少（少于10页）"
        ]
    },
    "bonus_rules": {
        "max_bonus": 10,
        "items": [
            {"name": "获奖", "max_score": 5},
            {"name": "创新", "max_score": 5}
        ]
    },
    "output_format": {
        "veto_check": "是否触发否决项",
        "score_details": "各指标得分明细",
        "base_score": "基础分",
        "grade_suggestion": "等级建议",
        "summary": "总体评价和改进建议"
    }
}

# 所有模板
DEFAULT_TEMPLATES = {
    "教案": LESSON_PLAN_TEMPLATE,
    "教学反思": TEACHING_REFLECTION_TEMPLATE,
    "教研/听课记录": TEACHING_RESEARCH_TEMPLATE,
    "成绩/学情分析": GRADE_ANALYSIS_TEMPLATE,
    "课件": COURSEWARE_TEMPLATE
}



class TemplateManager:
    """
    提示词模板管理器
    
    负责管理5类教学文件的评分标准模板
    """
    
    def __init__(self, db: Session):
        """
        初始化模板管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def get_template(self, file_type: str) -> Optional[Dict]:
        """
        获取指定文件类型的提示词模板
        
        Args:
            file_type: 文件类型（教案、教学反思、教研/听课记录、成绩/学情分析、课件）
        
        Returns:
            dict: 模板内容，如果不存在则返回 None
        """
        try:
            template = self.db.query(ScoringTemplate).filter(
                ScoringTemplate.file_type == file_type,
                ScoringTemplate.is_active == True
            ).first()
            
            if template:
                return json.loads(template.template_content)
            
            logger.warning(f"模板不存在: {file_type}")
            return None
        except Exception as e:
            logger.error(f"获取模板失败: {file_type}, 错误: {str(e)}")
            raise
    
    def create_template(self, file_type: str, template_data: Dict) -> int:
        """
        创建新的提示词模板
        
        Args:
            file_type: 文件类型
            template_data: 模板数据
        
        Returns:
            int: 创建的模板 ID
        """
        try:
            # 检查模板是否已存在
            existing = self.db.query(ScoringTemplate).filter(
                ScoringTemplate.file_type == file_type
            ).first()
            
            if existing:
                logger.warning(f"模板已存在: {file_type}")
                raise ValueError(f"模板已存在: {file_type}")
            
            # 验证模板结构
            self._validate_template_structure(template_data)
            
            # 创建新模板
            template = ScoringTemplate(
                file_type=file_type,
                template_content=json.dumps(template_data, ensure_ascii=False),
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            self.db.add(template)
            self.db.commit()
            
            logger.info(f"模板创建成功: {file_type}, ID: {template.id}")
            return template.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建模板失败: {file_type}, 错误: {str(e)}")
            raise
    
    def update_template(self, template_id: int, template_data: Dict) -> bool:
        """
        更新提示词模板
        
        Args:
            template_id: 模板 ID
            template_data: 新的模板数据
        
        Returns:
            bool: 是否更新成功
        """
        try:
            template = self.db.query(ScoringTemplate).filter(
                ScoringTemplate.id == template_id
            ).first()
            
            if not template:
                logger.warning(f"模板不存在: ID {template_id}")
                return False
            
            # 验证模板结构
            self._validate_template_structure(template_data)
            
            # 更新模板
            template.template_content = json.dumps(template_data, ensure_ascii=False)
            template.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"模板更新成功: ID {template_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新模板失败: ID {template_id}, 错误: {str(e)}")
            raise
    
    def build_prompt(self, file_type: str, content: str, bonus_rules: Optional[Dict] = None) -> str:
        """
        根据模板和文件内容构建完整提示词
        
        Args:
            file_type: 文件类型
            content: 文件内容
            bonus_rules: 加分项规则（可选）
        
        Returns:
            str: 完整的提示词
        """
        try:
            template = self.get_template(file_type)
            
            if not template:
                raise ValueError(f"模板不存在: {file_type}")
            
            # 构建提示词
            prompt = self._build_prompt_from_template(template, content, bonus_rules)
            
            logger.debug(f"提示词构建成功: {file_type}, 长度: {len(prompt)}")
            return prompt
        except Exception as e:
            logger.error(f"构建提示词失败: {file_type}, 错误: {str(e)}")
            raise
    
    def _validate_template_structure(self, template_data: Dict) -> bool:
        """
        验证模板结构的完整性
        
        Args:
            template_data: 模板数据
        
        Returns:
            bool: 是否有效
        
        Raises:
            ValueError: 如果模板结构不完整
        """
        required_fields = [
            "file_type",
            "grade_standards",
            "core_indicators",
            "veto_items",
            "bonus_rules",
            "output_format"
        ]
        
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"模板缺少必需字段: {field}")
        
        # 验证等级标准
        grade_standards = template_data.get("grade_standards", {})
        required_grades = ["excellent", "good", "pass", "fail"]
        for grade in required_grades:
            if grade not in grade_standards:
                raise ValueError(f"等级标准缺少: {grade}")
        
        # 验证核心指标
        core_indicators = template_data.get("core_indicators", [])
        if not isinstance(core_indicators, list) or len(core_indicators) == 0:
            raise ValueError("核心指标必须是非空列表")
        
        # 验证否决项
        veto_items = template_data.get("veto_items", {})
        if "general" not in veto_items or "specific" not in veto_items:
            raise ValueError("否决项必须包含 general 和 specific")
        
        return True
    
    def _build_prompt_from_template(self, template: Dict, content: str, 
                                    bonus_rules: Optional[Dict] = None) -> str:
        """
        从模板构建提示词
        
        Args:
            template: 模板数据
            content: 文件内容
            bonus_rules: 加分项规则
        
        Returns:
            str: 完整的提示词
        """
        file_type = template.get("file_type", "")
        
        # 构建基础提示词
        prompt = f"""你是一位专业的教学评估专家，请根据以下标准对{file_type}进行评分。

【评分规则】
1. 首先检查一票否决项，如果触发则直接判定为不合格
2. 如果未触发否决项，则按核心指标进行评分
3. 总分100分，按指标权重分配
4. 最终得分将加上加分项（最多10分）

【一票否决项】
通用否决项：
"""
        
        # 添加通用否决项
        veto_items = template.get("veto_items", {})
        for item in veto_items.get("general", []):
            prompt += f"- {item}\n"
        
        prompt += "\n专项否决项：\n"
        for item in veto_items.get("specific", []):
            prompt += f"- {item}\n"
        
        # 添加核心指标
        prompt += "\n【核心指标】（总分100分）\n\n"
        core_indicators = template.get("core_indicators", [])
        for idx, indicator in enumerate(core_indicators, 1):
            name = indicator.get("name", "")
            weight = indicator.get("weight", 0)
            description = indicator.get("description", "")
            prompt += f"{idx}. {name}（{weight}分）\n   {description}\n\n"
        
        # 添加等级标准
        prompt += "【等级标准】\n"
        grade_standards = template.get("grade_standards", {})
        grade_names = {
            "excellent": "优秀",
            "good": "良好",
            "pass": "合格",
            "fail": "不合格"
        }
        for grade_key, grade_name in grade_names.items():
            if grade_key in grade_standards:
                grade_range = grade_standards[grade_key]
                prompt += f"- {grade_name}：{grade_range['min']}-{grade_range['max']}分\n"
        
        # 添加待评分内容
        prompt += f"\n【待评分{file_type}内容】\n{content}\n"
        
        # 添加输出格式要求
        prompt += """
【输出格式要求】
请严格按照以下JSON格式输出评分结果：
{
    "veto_check": {
        "triggered": false,
        "reason": ""
    },
    "score_details": [
        {
            "indicator": "指标名称",
            "score": 分数,
            "max_score": 满分,
            "reason": "评分理由"
        }
    ],
    "base_score": 总分,
    "grade_suggestion": "等级",
    "summary": "总体评价和改进建议"
}
"""
        
        return prompt
    
    def list_templates(self) -> List[Dict]:
        """
        获取所有活跃的模板列表
        
        Returns:
            list: 模板列表
        """
        try:
            templates = self.db.query(ScoringTemplate).filter(
                ScoringTemplate.is_active == True
            ).all()
            
            result = []
            for template in templates:
                result.append({
                    "id": template.id,
                    "file_type": template.file_type,
                    "is_active": template.is_active,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "updated_at": template.updated_at.isoformat() if template.updated_at else None
                })
            
            return result
        except Exception as e:
            logger.error(f"获取模板列表失败: {str(e)}")
            raise
    
    def delete_template(self, template_id: int) -> bool:
        """
        删除模板（逻辑删除）
        
        Args:
            template_id: 模板 ID
        
        Returns:
            bool: 是否删除成功
        """
        try:
            template = self.db.query(ScoringTemplate).filter(
                ScoringTemplate.id == template_id
            ).first()
            
            if not template:
                logger.warning(f"模板不存在: ID {template_id}")
                return False
            
            template.is_active = False
            template.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"模板删除成功: ID {template_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除模板失败: ID {template_id}, 错误: {str(e)}")
            raise
