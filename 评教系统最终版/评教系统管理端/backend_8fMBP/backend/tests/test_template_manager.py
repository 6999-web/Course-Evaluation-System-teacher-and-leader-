"""
模板管理器单元测试

测试模板管理器的具体功能和边界情况
"""

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, ScoringTemplate
from app.services.template_manager import (
    TemplateManager,
    DEFAULT_TEMPLATES,
    LESSON_PLAN_TEMPLATE
)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
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


class TestTemplateManagerBasicOperations:
    """模板管理器基本操作测试"""
    
    def test_create_template_success(self, template_manager):
        """测试成功创建模板"""
        template_data = DEFAULT_TEMPLATES["教案"]
        
        template_id = template_manager.create_template("教案", template_data)
        
        assert template_id > 0
        assert isinstance(template_id, int)
    
    def test_create_duplicate_template_fails(self, template_manager):
        """测试创建重复模板失败"""
        template_data = DEFAULT_TEMPLATES["教案"]
        
        # 创建第一个模板
        template_manager.create_template("教案", template_data)
        
        # 尝试创建重复模板
        with pytest.raises(ValueError):
            template_manager.create_template("教案", template_data)
    
    def test_get_template_success(self, template_manager):
        """测试成功获取模板"""
        template_data = DEFAULT_TEMPLATES["教案"]
        template_manager.create_template("教案", template_data)
        
        retrieved = template_manager.get_template("教案")
        
        assert retrieved is not None
        assert retrieved["file_type"] == "教案"
        assert "grade_standards" in retrieved
        assert "core_indicators" in retrieved
    
    def test_get_nonexistent_template_returns_none(self, template_manager):
        """测试获取不存在的模板返回 None"""
        result = template_manager.get_template("nonexistent")
        
        assert result is None
    
    def test_update_template_success(self, template_manager):
        """测试成功更新模板"""
        template_data = DEFAULT_TEMPLATES["教案"]
        template_id = template_manager.create_template("教案", template_data)
        
        # 修改模板
        updated_data = json.loads(json.dumps(template_data))
        updated_data["core_indicators"][0]["weight"] = 35
        
        success = template_manager.update_template(template_id, updated_data)
        
        assert success is True
        
        # 验证更新
        retrieved = template_manager.get_template("教案")
        assert retrieved["core_indicators"][0]["weight"] == 35
    
    def test_update_nonexistent_template_fails(self, template_manager):
        """测试更新不存在的模板失败"""
        template_data = DEFAULT_TEMPLATES["教案"]
        
        success = template_manager.update_template(999, template_data)
        
        assert success is False
    
    def test_delete_template_success(self, template_manager):
        """测试成功删除模板"""
        template_data = DEFAULT_TEMPLATES["教案"]
        template_id = template_manager.create_template("教案", template_data)
        
        success = template_manager.delete_template(template_id)
        
        assert success is True
        
        # 验证删除
        retrieved = template_manager.get_template("教案")
        assert retrieved is None
    
    def test_delete_nonexistent_template_fails(self, template_manager):
        """测试删除不存在的模板失败"""
        success = template_manager.delete_template(999)
        
        assert success is False
    
    def test_list_templates_empty(self, template_manager):
        """测试空模板列表"""
        templates = template_manager.list_templates()
        
        assert isinstance(templates, list)
        assert len(templates) == 0
    
    def test_list_templates_with_data(self, template_manager):
        """测试包含数据的模板列表"""
        # 创建多个模板
        for file_type, template_data in DEFAULT_TEMPLATES.items():
            template_manager.create_template(file_type, template_data)
        
        templates = template_manager.list_templates()
        
        assert len(templates) == len(DEFAULT_TEMPLATES)
        
        # 验证列表中的字段
        for template in templates:
            assert "id" in template
            assert "file_type" in template
            assert "is_active" in template
            assert "created_at" in template
            assert "updated_at" in template


class TestTemplateValidation:
    """模板验证测试"""
    
    def test_validate_template_structure_valid(self, template_manager):
        """测试验证有效的模板结构"""
        template_data = DEFAULT_TEMPLATES["教案"]
        
        # 应该不抛出异常
        result = template_manager._validate_template_structure(template_data)
        
        assert result is True
    
    def test_validate_template_missing_file_type(self, template_manager):
        """测试验证缺少 file_type 的模板"""
        template_data = {
            "grade_standards": {},
            "core_indicators": [],
            "veto_items": {"general": [], "specific": []},
            "bonus_rules": {"max_bonus": 10, "items": []},
            "output_format": {}
        }
        
        with pytest.raises(ValueError):
            template_manager._validate_template_structure(template_data)
    
    def test_validate_template_missing_grade_standards(self, template_manager):
        """测试验证缺少等级标准的模板"""
        template_data = {
            "file_type": "教案",
            "core_indicators": [],
            "veto_items": {"general": [], "specific": []},
            "bonus_rules": {"max_bonus": 10, "items": []},
            "output_format": {}
        }
        
        with pytest.raises(ValueError):
            template_manager._validate_template_structure(template_data)
    
    def test_validate_template_missing_grade_level(self, template_manager):
        """测试验证缺少等级的模板"""
        template_data = {
            "file_type": "教案",
            "grade_standards": {
                "excellent": {"min": 90, "max": 100},
                "good": {"min": 80, "max": 89}
                # 缺少 pass 和 fail
            },
            "core_indicators": [{"name": "test", "weight": 100}],
            "veto_items": {"general": ["test"], "specific": ["test"]},
            "bonus_rules": {"max_bonus": 10, "items": []},
            "output_format": {}
        }
        
        with pytest.raises(ValueError):
            template_manager._validate_template_structure(template_data)
    
    def test_validate_template_invalid_core_indicators(self, template_manager):
        """测试验证无效的核心指标"""
        template_data = {
            "file_type": "教案",
            "grade_standards": {
                "excellent": {"min": 90, "max": 100},
                "good": {"min": 80, "max": 89},
                "pass": {"min": 60, "max": 79},
                "fail": {"min": 0, "max": 59}
            },
            "core_indicators": [],  # 空列表
            "veto_items": {"general": ["test"], "specific": ["test"]},
            "bonus_rules": {"max_bonus": 10, "items": []},
            "output_format": {}
        }
        
        with pytest.raises(ValueError):
            template_manager._validate_template_structure(template_data)


class TestPromptBuilding:
    """提示词构建测试"""
    
    def test_build_prompt_contains_file_type(self, template_manager):
        """测试构建的提示词包含文件类型"""
        template_data = DEFAULT_TEMPLATES["教案"]
        template_manager.create_template("教案", template_data)
        
        prompt = template_manager.build_prompt("教案", "测试内容")
        
        assert "教案" in prompt
    
    def test_build_prompt_contains_content(self, template_manager):
        """测试构建的提示词包含文件内容"""
        template_data = DEFAULT_TEMPLATES["教案"]
        template_manager.create_template("教案", template_data)
        
        content = "这是测试内容"
        prompt = template_manager.build_prompt("教案", content)
        
        assert content in prompt
    
    def test_build_prompt_contains_evaluation_rules(self, template_manager):
        """测试构建的提示词包含评分规则"""
        template_data = DEFAULT_TEMPLATES["教案"]
        template_manager.create_template("教案", template_data)
        
        prompt = template_manager.build_prompt("教案", "测试内容")
        
        assert "评分规则" in prompt
        assert "否决项" in prompt
        assert "核心指标" in prompt
    
    def test_build_prompt_contains_output_format(self, template_manager):
        """测试构建的提示词包含输出格式"""
        template_data = DEFAULT_TEMPLATES["教案"]
        template_manager.create_template("教案", template_data)
        
        prompt = template_manager.build_prompt("教案", "测试内容")
        
        assert "JSON" in prompt
        assert "veto_check" in prompt
        assert "score_details" in prompt
    
    def test_build_prompt_for_all_file_types(self, template_manager):
        """测试为所有文件类型构建提示词"""
        for file_type, template_data in DEFAULT_TEMPLATES.items():
            template_manager.create_template(file_type, template_data)
            
            prompt = template_manager.build_prompt(file_type, "测试内容")
            
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert file_type in prompt
    
    def test_build_prompt_nonexistent_template_fails(self, template_manager):
        """测试为不存在的模板构建提示词失败"""
        with pytest.raises(ValueError):
            template_manager.build_prompt("nonexistent", "测试内容")


class TestTemplateIntegration:
    """模板管理器集成测试"""
    
    def test_full_template_lifecycle(self, template_manager):
        """测试完整的模板生命周期"""
        template_data = DEFAULT_TEMPLATES["教案"]
        
        # 创建
        template_id = template_manager.create_template("教案", template_data)
        assert template_id > 0
        
        # 读取
        retrieved = template_manager.get_template("教案")
        assert retrieved is not None
        
        # 更新
        updated_data = json.loads(json.dumps(template_data))
        updated_data["core_indicators"][0]["weight"] = 30
        success = template_manager.update_template(template_id, updated_data)
        assert success is True
        
        # 验证更新
        retrieved = template_manager.get_template("教案")
        assert retrieved["core_indicators"][0]["weight"] == 30
        
        # 删除
        success = template_manager.delete_template(template_id)
        assert success is True
        
        # 验证删除
        retrieved = template_manager.get_template("教案")
        assert retrieved is None
    
    def test_multiple_templates_management(self, template_manager):
        """测试多个模板的管理"""
        # 创建所有模板
        template_ids = {}
        for file_type, template_data in DEFAULT_TEMPLATES.items():
            template_id = template_manager.create_template(file_type, template_data)
            template_ids[file_type] = template_id
        
        # 验证所有模板都存在
        templates = template_manager.list_templates()
        assert len(templates) == len(DEFAULT_TEMPLATES)
        
        # 删除一个模板
        template_manager.delete_template(template_ids["教案"])
        
        # 验证删除
        templates = template_manager.list_templates()
        assert len(templates) == len(DEFAULT_TEMPLATES) - 1
        
        # 验证其他模板仍然存在
        for file_type in ["教学反思", "教研/听课记录", "成绩/学情分析", "课件"]:
            retrieved = template_manager.get_template(file_type)
            assert retrieved is not None
