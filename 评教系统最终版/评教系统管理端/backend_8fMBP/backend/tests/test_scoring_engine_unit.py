"""
评分引擎单元测试

测试评分引擎的具体业务场景、边界值和错误处理。
重点测试等级边界值、否决项触发场景和加分项计算。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scoring_engine import (
    ScoringEngine, 
    ScoringEngineError,
    FileNotFoundError,
    UnsupportedFileTypeError,
    ScoringFailedError,
    create_scoring_engine
)
from app.services.deepseek_api_client import DeepseekAPIClient
from app.models import MaterialSubmission, ScoringRecord


class TestScoringEngineUnit:
    """评分引擎单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建模拟的API客户端
        self.mock_api_client = Mock(spec=DeepseekAPIClient)
        self.engine = ScoringEngine(api_client=self.mock_api_client)
        
        # 模拟TemplateManager
        self.mock_template_manager = Mock()
        self.engine.template_manager = self.mock_template_manager
    
    # 测试等级边界值（Requirements 5.9, 5.10, 5.11, 5.12）
    
    def test_grade_boundary_excellent_90(self):
        """测试优秀等级边界值 - 90分"""
        grade = self.engine.determine_grade(90.0)
        assert grade == "优秀"
    
    def test_grade_boundary_excellent_100(self):
        """测试优秀等级边界值 - 100分"""
        grade = self.engine.determine_grade(100.0)
        assert grade == "优秀"
    
    def test_grade_boundary_good_80(self):
        """测试良好等级边界值 - 80分"""
        grade = self.engine.determine_grade(80.0)
        assert grade == "良好"
    
    def test_grade_boundary_good_89(self):
        """测试良好等级边界值 - 89分"""
        grade = self.engine.determine_grade(89.0)
        assert grade == "良好"
    
    def test_grade_boundary_pass_60(self):
        """测试合格等级边界值 - 60分"""
        grade = self.engine.determine_grade(60.0)
        assert grade == "合格"
    
    def test_grade_boundary_pass_79(self):
        """测试合格等级边界值 - 79分"""
        grade = self.engine.determine_grade(79.0)
        assert grade == "合格"
    
    def test_grade_boundary_fail_59(self):
        """测试不合格等级边界值 - 59分"""
        grade = self.engine.determine_grade(59.0)
        assert grade == "不合格"
    
    def test_grade_boundary_fail_0(self):
        """测试不合格等级边界值 - 0分"""
        grade = self.engine.determine_grade(0.0)
        assert grade == "不合格"
    
    def test_grade_boundary_edge_cases(self):
        """测试等级边界值的边缘情况"""
        # 测试小数点边界
        assert self.engine.determine_grade(89.9) == "良好"
        assert self.engine.determine_grade(90.1) == "优秀"
        assert self.engine.determine_grade(79.9) == "合格"
        assert self.engine.determine_grade(80.1) == "良好"
        assert self.engine.determine_grade(59.9) == "不合格"
        assert self.engine.determine_grade(60.1) == "合格"
    
    # 测试否决项触发场景（Requirements 5.1, 5.2, 5.3, 5.4）
    
    def test_veto_result_creation_general_veto(self):
        """测试通用否决项触发场景"""
        parsed_result = {
            'veto_triggered': True,
            'veto_reason': '存在造假行为',
            'base_score': 85.0,
            'summary': '发现抄袭内容',
            'score_details': []
        }
        
        result = self.engine._create_veto_result(123, parsed_result, 'lesson_plan')
        
        assert result['submission_id'] == 123
        assert result['file_type'] == 'lesson_plan'
        assert result['base_score'] == 0.0
        assert result['bonus_score'] == 0.0
        assert result['final_score'] == 0.0
        assert result['grade'] == '不合格'
        assert result['veto_triggered'] == True
        assert result['veto_reason'] == '存在造假行为'
        assert result['status'] == 'completed'
    
    def test_veto_result_creation_specific_veto(self):
        """测试专项否决项触发场景"""
        parsed_result = {
            'veto_triggered': True,
            'veto_reason': '教学目标完全缺失',
            'base_score': 75.0,
            'summary': '教案中未发现教学目标',
            'score_details': []
        }
        
        result = self.engine._create_veto_result(456, parsed_result, 'lesson_plan')
        
        assert result['submission_id'] == 456
        assert result['final_score'] == 0.0
        assert result['grade'] == '不合格'
        assert result['veto_triggered'] == True
        assert result['veto_reason'] == '教学目标完全缺失'
    
    def test_veto_result_creation_teacher_ethics_veto(self):
        """测试师德失范否决项触发场景"""
        parsed_result = {
            'veto_triggered': True,
            'veto_reason': '存在师德失范内容',
            'base_score': 90.0,
            'summary': '发现不当言论',
            'score_details': []
        }
        
        result = self.engine._create_veto_result(789, parsed_result, 'teaching_reflection')
        
        assert result['final_score'] == 0.0
        assert result['grade'] == '不合格'
        assert result['veto_reason'] == '存在师德失范内容'
    
    # 测试加分项计算（Requirements 5.6, 5.7）
    
    def test_bonus_calculation_normal_case(self):
        """测试正常加分项计算"""
        bonus_items = [
            {'name': '获奖', 'score': 3.0, 'description': '省级教学比赛二等奖'},
            {'name': '创新', 'score': 2.0, 'description': '教学方法创新'}
        ]
        
        bonus_score, bonus_details = self.engine._calculate_bonus_score(bonus_items)
        
        assert bonus_score == 5.0
        assert len(bonus_details) == 2
        assert bonus_details[0]['name'] == '获奖'
        assert bonus_details[0]['score'] == 3.0
        assert bonus_details[1]['name'] == '创新'
        assert bonus_details[1]['score'] == 2.0
    
    def test_bonus_calculation_exceed_limit(self):
        """测试加分项超过10分限制"""
        bonus_items = [
            {'name': '获奖1', 'score': 5.0, 'description': '国家级奖项'},
            {'name': '获奖2', 'score': 4.0, 'description': '省级奖项'},
            {'name': '获奖3', 'score': 3.0, 'description': '市级奖项'},
            {'name': '创新', 'score': 2.0, 'description': '教学创新'}
        ]
        
        bonus_score, bonus_details = self.engine._calculate_bonus_score(bonus_items)
        
        # 总加分应该被限制为10分
        assert bonus_score == 10.0
        
        # 各项加分应该按比例缩放
        total_original = 5.0 + 4.0 + 3.0 + 2.0  # 14.0
        scale_factor = 10.0 / 14.0
        
        assert abs(bonus_details[0]['score'] - 5.0 * scale_factor) < 0.01
        assert abs(bonus_details[1]['score'] - 4.0 * scale_factor) < 0.01
        assert abs(bonus_details[2]['score'] - 3.0 * scale_factor) < 0.01
        assert abs(bonus_details[3]['score'] - 2.0 * scale_factor) < 0.01
    
    def test_bonus_calculation_single_item_exceed_5(self):
        """测试单项加分超过5分限制"""
        bonus_items = [
            {'name': '特殊奖项', 'score': 8.0, 'description': '特殊贡献奖'}
        ]
        
        bonus_score, bonus_details = self.engine._calculate_bonus_score(bonus_items)
        
        # 单项加分应该被限制为5分
        assert bonus_score == 5.0
        assert bonus_details[0]['score'] == 5.0
    
    def test_bonus_calculation_empty_list(self):
        """测试空加分项列表"""
        bonus_items = []
        
        bonus_score, bonus_details = self.engine._calculate_bonus_score(bonus_items)
        
        assert bonus_score == 0.0
        assert bonus_details == []
    
    def test_bonus_calculation_none_input(self):
        """测试None输入"""
        bonus_score, bonus_details = self.engine._calculate_bonus_score(None)
        
        assert bonus_score == 0.0
        assert bonus_details == []
    
    def test_bonus_calculation_zero_scores(self):
        """测试零分加分项"""
        bonus_items = [
            {'name': '参与', 'score': 0.0, 'description': '参与活动'},
            {'name': '尝试', 'score': 0.0, 'description': '尝试创新'}
        ]
        
        bonus_score, bonus_details = self.engine._calculate_bonus_score(bonus_items)
        
        assert bonus_score == 0.0
        assert len(bonus_details) == 2
        assert all(detail['score'] == 0.0 for detail in bonus_details)
    
    # 测试最终得分计算
    
    def test_final_score_calculation_normal(self):
        """测试正常最终得分计算"""
        parsed_result = {
            'base_score': 85.0,
            'summary': '整体表现良好',
            'score_details': []
        }
        bonus_items = [
            {'name': '获奖', 'score': 3.0, 'description': '教学比赛获奖'}
        ]
        
        result = self.engine._calculate_final_score(123, parsed_result, bonus_items, 'lesson_plan')
        
        assert result['submission_id'] == 123
        assert result['file_type'] == 'lesson_plan'
        assert result['base_score'] == 85.0
        assert result['bonus_score'] == 3.0
        assert result['final_score'] == 88.0
        assert result['grade'] == '良好'
        assert result['veto_triggered'] == False
    
    def test_final_score_calculation_exceed_100(self):
        """测试最终得分超过100分的情况"""
        parsed_result = {
            'base_score': 95.0,
            'summary': '表现优秀',
            'score_details': []
        }
        bonus_items = [
            {'name': '获奖', 'score': 8.0, 'description': '多项获奖'}
        ]
        
        result = self.engine._calculate_final_score(456, parsed_result, bonus_items, 'lesson_plan')
        
        # 最终得分应该被限制在100分
        assert result['final_score'] == 100.0
        assert result['grade'] == '优秀'
    
    def test_final_score_calculation_no_bonus(self):
        """测试无加分项的最终得分计算"""
        parsed_result = {
            'base_score': 75.0,
            'summary': '基本合格',
            'score_details': []
        }
        bonus_items = []
        
        result = self.engine._calculate_final_score(789, parsed_result, bonus_items, 'lesson_plan')
        
        assert result['base_score'] == 75.0
        assert result['bonus_score'] == 0.0
        assert result['final_score'] == 75.0
        assert result['grade'] == '合格'
    
    # 测试文件类型判断
    
    def test_determine_file_type_lesson_plan_by_name(self):
        """测试通过文件名判断教案类型"""
        file_type = self.engine._determine_file_type('数学教案.docx', '这是一个教案内容')
        assert file_type == 'lesson_plan'
    
    def test_determine_file_type_lesson_plan_by_content(self):
        """测试通过内容判断教案类型"""
        content = '教学目标：掌握基本概念。教学重点：理解原理。教学难点：应用方法。教学过程：导入、新课、练习、总结。'
        file_type = self.engine._determine_file_type('课程文档.docx', content)
        assert file_type == 'lesson_plan'
    
    def test_determine_file_type_teaching_reflection(self):
        """测试判断教学反思类型"""
        file_type = self.engine._determine_file_type('教学反思.docx', '本次教学反思如下...')
        assert file_type == 'teaching_reflection'
    
    def test_determine_file_type_teaching_research(self):
        """测试判断教研/听课记录类型"""
        file_type = self.engine._determine_file_type('听课记录.docx', '听课记录：时间、地点、内容...')
        assert file_type == 'teaching_research'
    
    def test_determine_file_type_grade_analysis(self):
        """测试判断成绩/学情分析类型"""
        file_type = self.engine._determine_file_type('成绩分析.docx', '本次考试成绩分析...')
        assert file_type == 'grade_analysis'
    
    def test_determine_file_type_courseware(self):
        """测试判断课件类型"""
        file_type = self.engine._determine_file_type('课件.pptx', '这是课件内容')
        assert file_type == 'courseware'
    
    def test_determine_file_type_default(self):
        """测试无法判断时使用默认类型"""
        file_type = self.engine._determine_file_type('未知文档.docx', '这是一些普通内容')
        assert file_type == 'lesson_plan'  # 默认为教案类型
    
    # 测试API结果解析
    
    def test_parse_api_result_normal(self):
        """测试正常API结果解析"""
        api_result = {
            'veto_check': {
                'triggered': False,
                'reason': ''
            },
            'base_score': 85.5,
            'grade_suggestion': '良好',
            'summary': '整体表现良好',
            'score_details': [
                {'indicator': '教学目标', 'score': 22, 'max_score': 25}
            ]
        }
        
        parsed = self.engine._parse_api_result(api_result)
        
        assert parsed['veto_triggered'] == False
        assert parsed['veto_reason'] == ''
        assert parsed['base_score'] == 85.5
        assert parsed['grade_suggestion'] == '良好'
        assert parsed['summary'] == '整体表现良好'
        assert len(parsed['score_details']) == 1
    
    def test_parse_api_result_with_veto(self):
        """测试带否决项的API结果解析"""
        api_result = {
            'veto_check': {
                'triggered': True,
                'reason': '存在造假行为'
            },
            'base_score': 0,
            'grade_suggestion': '不合格',
            'summary': '发现抄袭',
            'score_details': []
        }
        
        parsed = self.engine._parse_api_result(api_result)
        
        assert parsed['veto_triggered'] == True
        assert parsed['veto_reason'] == '存在造假行为'
        assert parsed['base_score'] == 0.0
        assert parsed['grade_suggestion'] == '不合格'
    
    # 测试错误处理
    
    def test_file_not_found_error(self):
        """测试文件未找到错误"""
        with patch('app.services.scoring_engine.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value.__next__.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            # Mock the logging method to avoid database issues
            with patch.object(self.engine, '_log_scoring_activity'):
                with pytest.raises(FileNotFoundError) as exc_info:
                    self.engine.score_file(999)
                
                assert "未找到提交记录: 999" in str(exc_info.value)
    
    def test_scoring_failed_error_on_api_failure(self):
        """测试API调用失败时的错误处理"""
        # 模拟数据库返回
        with patch('app.services.scoring_engine.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value.__next__.return_value = mock_db
            
            mock_submission = Mock()
            mock_submission.submission_id = 123  # Use correct field name
            mock_submission.files = [{'file_name': 'test.docx', 'file_url': '/path/to/test.docx'}]
            mock_submission.encrypted_path = None
            mock_db.query.return_value.filter.return_value.first.return_value = mock_submission
            
            # Mock the logging method to avoid database issues
            with patch.object(self.engine, '_log_scoring_activity'):
                # 模拟文件解析成功
                with patch.object(self.engine, '_parse_file_content', return_value='文件内容'):
                    # 模拟提示词构建成功
                    with patch.object(self.engine, '_build_scoring_prompt', return_value='提示词'):
                        # 模拟API调用失败
                        self.mock_api_client.call_api.side_effect = Exception('API调用失败')
                        
                        with pytest.raises(ScoringFailedError) as exc_info:
                            self.engine.score_file(123)
                        
                        assert "评分失败" in str(exc_info.value)
    
    # 测试便利函数
    
    def test_create_scoring_engine_function(self):
        """测试便利创建函数"""
        with patch('app.services.scoring_engine.create_deepseek_client') as mock_create_client:
            mock_client = Mock()
            mock_create_client.return_value = mock_client
            
            engine = create_scoring_engine()
            
            assert isinstance(engine, ScoringEngine)
            assert engine.api_client == mock_client
            mock_create_client.assert_called_once()
    
    def test_create_scoring_engine_with_custom_client(self):
        """测试使用自定义客户端创建引擎"""
        custom_client = Mock(spec=DeepseekAPIClient)
        engine = create_scoring_engine(custom_client)
        
        assert isinstance(engine, ScoringEngine)
        assert engine.api_client == custom_client
    
    # 测试API信息获取
    
    def test_get_api_info(self):
        """测试获取API信息"""
        expected_info = {
            'api_url': 'https://api.deepseek.com/v1/chat/completions',
            'model': 'deepseek-chat',
            'temperature': 0.1
        }
        self.mock_api_client.get_api_info.return_value = expected_info
        
        info = self.engine.get_api_info()
        
        assert info == expected_info
        self.mock_api_client.get_api_info.assert_called_once()
    
    # 测试批量评分
    
    def test_batch_score_all_success(self):
        """测试批量评分全部成功"""
        submission_ids = [1, 2, 3]
        
        # 模拟单个评分成功
        mock_results = [
            {'submission_id': 1, 'final_score': 85, 'grade': '良好'},
            {'submission_id': 2, 'final_score': 92, 'grade': '优秀'},
            {'submission_id': 3, 'final_score': 78, 'grade': '合格'}
        ]
        
        with patch.object(self.engine, 'score_file', side_effect=mock_results):
            results = self.engine.batch_score(submission_ids)
            
            assert len(results) == 3
            assert all('status' not in result or result.get('status') != 'failed' for result in results)
    
    def test_batch_score_partial_failure(self):
        """测试批量评分部分失败"""
        submission_ids = [1, 2, 3]
        
        def mock_score_file(submission_id, bonus_items=None):
            if submission_id == 2:
                raise ScoringFailedError("评分失败")
            return {'submission_id': submission_id, 'final_score': 85, 'grade': '良好'}
        
        with patch.object(self.engine, 'score_file', side_effect=mock_score_file):
            results = self.engine.batch_score(submission_ids)
            
            assert len(results) == 3
            assert results[0]['submission_id'] == 1
            assert results[1]['status'] == 'failed'
            assert results[1]['submission_id'] == 2
            assert results[2]['submission_id'] == 3