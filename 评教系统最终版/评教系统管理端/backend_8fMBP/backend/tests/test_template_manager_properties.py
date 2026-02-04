"""
模板管理器属性测试

使用 Hypothesis 进行属性测试，验证模板管理器的通用正确性属性
"""

import json
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, ScoringTemplate
from app.services.template_manager import (
    TemplateManager,
    DEFAULT_TEMPLATES,
    LESSON_PLAN_TEMPLATE,
    TEACHING_REFLECTION_TEMPLATE,
    TEACHING_RESEARCH_TEMPLATE,
    GRADE_ANALYSIS_TEMPLATE,
    COURSEWARE_TEMPLATE
)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    # 使用内存数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def template_manager(db_session):
    """创建模板管理器实例"""
    return TemplateManager(db_session)


class TestTemplateManagerProperties:
    """模板管理器属性测试类"""
    
    # Feature: auto-scoring-system, Property 7: 提示词模板结构完整性
    @given(
        file_type=st.sampled_from([
            "教案", "教学反思", "教研/听课记录", "成绩/学情分析", "课件"
        ])
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_template_structure_completeness_property(self, file_type):
        """
        Property 7: For any 创建的提示词模板，应该包含所有必需字段：
        等级划分标准、核心指标、专项否决项、通用否决项、加分项规则、输出格式定义。
        
        Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
        
        This property tests that:
        1. All templates contain required fields
        2. Template structure is valid and complete
        3. All templates can be retrieved and validated
        """
        # 获取默认模板
        template_data = DEFAULT_TEMPLATES.get(file_type)
        assert template_data is not None, f"模板不存在: {file_type}"
        
        # 验证必需字段
        required_fields = [
            "file_type",
            "grade_standards",
            "core_indicators",
            "veto_items",
            "bonus_rules",
            "output_format"
        ]
        
        for field in required_fields:
            assert field in template_data, f"模板缺少字段: {field}"
        
        # 验证等级标准
        grade_standards = template_data.get("grade_standards", {})
        required_grades = ["excellent", "good", "pass", "fail"]
        for grade in required_grades:
            assert grade in grade_standards, f"等级标准缺少: {grade}"
            grade_range = grade_standards[grade]
            assert "min" in grade_range and "max" in grade_range
            assert grade_range["min"] <= grade_range["max"]
        
        # 验证核心指标
        core_indicators = template_data.get("core_indicators", [])
        assert isinstance(core_indicators, list)
        assert len(core_indicators) > 0, "核心指标不能为空"
        
        total_weight = 0
        for indicator in core_indicators:
            assert "name" in indicator
            assert "weight" in indicator
            assert "description" in indicator
            total_weight += indicator.get("weight", 0)
        
        # 权重总和应该是100
        assert total_weight == 100, f"权重总和应该是100，实际: {total_weight}"
        
        # 验证否决项
        veto_items = template_data.get("veto_items", {})
        assert "general" in veto_items, "否决项缺少 general"
        assert "specific" in veto_items, "否决项缺少 specific"
        assert isinstance(veto_items["general"], list)
        assert isinstance(veto_items["specific"], list)
        assert len(veto_items["general"]) > 0
        assert len(veto_items["specific"]) > 0
        
        # 验证加分项规则
        bonus_rules = template_data.get("bonus_rules", {})
        assert "max_bonus" in bonus_rules
        assert "items" in bonus_rules
        assert bonus_rules["max_bonus"] > 0
        assert isinstance(bonus_rules["items"], list)
        
        # 验证输出格式
        output_format = template_data.get("output_format", {})
        required_output_fields = [
            "veto_check", "score_details", "base_score", 
            "grade_suggestion", "summary"
        ]
        for field in required_output_fields:
            assert field in output_format, f"输出格式缺少: {field}"
    
    # 补充属性测试：模板创建和检索
    @given(
        file_type=st.sampled_from([
            "教案", "教学反思", "教研/听课记录", "成绩/学情分析", "课件"
        ])
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_template_creation_and_retrieval_property(self, file_type):
        """
        补充属性测试：模板创建和检索的一致性
        
        For any 模板，创建后应该能够正确检索
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        template_manager = TemplateManager(db_session)
        template_data = DEFAULT_TEMPLATES.get(file_type)
        
        # 创建模板
        template_id = template_manager.create_template(file_type, template_data)
        assert template_id > 0, "模板ID应该大于0"
        
        # 检索模板
        retrieved_template = template_manager.get_template(file_type)
        assert retrieved_template is not None, "应该能够检索到模板"
        
        # 验证检索到的模板与原始模板一致
        assert retrieved_template["file_type"] == file_type
        assert retrieved_template["grade_standards"] == template_data["grade_standards"]
        assert len(retrieved_template["core_indicators"]) == len(template_data["core_indicators"])
        
        db_session.close()
    
    # 补充属性测试：模板更新
    @given(
        file_type=st.sampled_from([
            "教案", "教学反思", "教研/听课记录", "成绩/学情分析", "课件"
        ])
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_template_update_property(self, file_type):
        """
        补充属性测试：模板更新后应该能够正确检索更新后的内容
        
        For any 模板，更新后应该能够检索到更新后的内容
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        template_manager = TemplateManager(db_session)
        template_data = DEFAULT_TEMPLATES.get(file_type)
        
        # 创建模板
        template_id = template_manager.create_template(file_type, template_data)
        
        # 修改模板数据
        updated_data = json.loads(json.dumps(template_data))
        updated_data["core_indicators"][0]["weight"] = 30
        
        # 更新模板
        success = template_manager.update_template(template_id, updated_data)
        assert success, "模板更新应该成功"
        
        # 检索更新后的模板
        retrieved_template = template_manager.get_template(file_type)
        assert retrieved_template is not None
        assert retrieved_template["core_indicators"][0]["weight"] == 30
        
        db_session.close()
    
    # 补充属性测试：提示词构建
    @given(
        file_type=st.sampled_from([
            "教案", "教学反思", "教研/听课记录", "成绩/学情分析", "课件"
        ]),
        content=st.text(min_size=10, max_size=500)
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_prompt_building_property(self, file_type, content):
        """
        补充属性测试：构建的提示词应该包含必需的信息
        
        For any 模板和内容，构建的提示词应该包含：
        1. 文件类型
        2. 评分规则
        3. 否决项
        4. 核心指标
        5. 文件内容
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        template_manager = TemplateManager(db_session)
        template_data = DEFAULT_TEMPLATES.get(file_type)
        
        # 创建模板
        template_manager.create_template(file_type, template_data)
        
        # 构建提示词
        prompt = template_manager.build_prompt(file_type, content)
        
        # 验证提示词包含必需信息
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert file_type in prompt, "提示词应该包含文件类型"
        assert "评分规则" in prompt, "提示词应该包含评分规则"
        assert "否决项" in prompt, "提示词应该包含否决项"
        assert "核心指标" in prompt, "提示词应该包含核心指标"
        assert content in prompt, "提示词应该包含文件内容"
        assert "JSON" in prompt, "提示词应该包含输出格式说明"
        
        db_session.close()
    
    # 补充属性测试：模板列表
    def test_template_list_property(self):
        """
        补充属性测试：模板列表应该包含所有创建的模板
        
        For any 创建的模板，应该能够在模板列表中找到
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        template_manager = TemplateManager(db_session)
        
        # 创建所有默认模板
        for file_type, template_data in DEFAULT_TEMPLATES.items():
            template_manager.create_template(file_type, template_data)
        
        # 获取模板列表
        templates = template_manager.list_templates()
        
        # 验证列表包含所有模板
        assert len(templates) == len(DEFAULT_TEMPLATES)
        
        template_types = [t["file_type"] for t in templates]
        for file_type in DEFAULT_TEMPLATES.keys():
            assert file_type in template_types, f"模板列表应该包含: {file_type}"
        
        db_session.close()
    
    # 补充属性测试：模板删除
    @given(
        file_type=st.sampled_from([
            "教案", "教学反思", "教研/听课记录", "成绩/学情分析", "课件"
        ])
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_template_deletion_property(self, file_type):
        """
        补充属性测试：删除模板后应该无法检索
        
        For any 删除的模板，应该无法检索到
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        template_manager = TemplateManager(db_session)
        template_data = DEFAULT_TEMPLATES.get(file_type)
        
        # 创建模板
        template_id = template_manager.create_template(file_type, template_data)
        
        # 验证模板存在
        template = template_manager.get_template(file_type)
        assert template is not None
        
        # 删除模板
        success = template_manager.delete_template(template_id)
        assert success, "模板删除应该成功"
        
        # 验证模板已删除
        template = template_manager.get_template(file_type)
        assert template is None, "删除后应该无法检索到模板"
        
        db_session.close()


class TestTemplateManagerEdgeCases:
    """模板管理器边界情况测试"""
    
    def test_default_templates_not_empty(self):
        """测试默认模板不为空"""
        assert len(DEFAULT_TEMPLATES) == 5
        assert "教案" in DEFAULT_TEMPLATES
        assert "教学反思" in DEFAULT_TEMPLATES
        assert "教研/听课记录" in DEFAULT_TEMPLATES
        assert "成绩/学情分析" in DEFAULT_TEMPLATES
        assert "课件" in DEFAULT_TEMPLATES
    
    def test_all_default_templates_valid(self):
        """测试所有默认模板都有效"""
        for file_type, template_data in DEFAULT_TEMPLATES.items():
            assert template_data["file_type"] == file_type
            assert "grade_standards" in template_data
            assert "core_indicators" in template_data
            assert "veto_items" in template_data
            assert "bonus_rules" in template_data
            assert "output_format" in template_data
    
    def test_template_manager_with_invalid_template(self, db_session):
        """测试模板管理器处理无效模板"""
        manager = TemplateManager(db_session)
        
        # 尝试创建无效模板
        invalid_template = {"file_type": "invalid"}
        
        with pytest.raises(ValueError):
            manager.create_template("invalid", invalid_template)
    
    def test_template_manager_get_nonexistent_template(self, db_session):
        """测试获取不存在的模板"""
        manager = TemplateManager(db_session)
        
        # 尝试获取不存在的模板
        template = manager.get_template("nonexistent")
        assert template is None
    
    def test_template_manager_update_nonexistent_template(self, db_session):
        """测试更新不存在的模板"""
        manager = TemplateManager(db_session)
        
        # 尝试更新不存在的模板
        success = manager.update_template(999, DEFAULT_TEMPLATES["教案"])
        assert success is False
