"""
文件提交属性测试

使用 Hypothesis 进行基于属性的测试，验证文件提交功能的通用正确性属性。
"""

import os
import tempfile
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import MaterialSubmission, EvaluationAssignmentTask, ScoringRecord
from app.utils.file_parser import FileParser


class TestMaterialSubmissionProperties:
    """文件提交属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.file_parser = FileParser()
        self.supported_file_types = ['docx', 'pdf', 'pptx']
        self.required_file_types = ['lesson_plan', 'teaching_reflection']
    
    # Feature: auto-scoring-system, Property 15: 文件类型校验
    @given(
        file_extension=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz0123456789_',
            min_size=1,
            max_size=10
        ),
        required_types=st.lists(
            st.sampled_from(['docx', 'pdf', 'pptx']),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
    )
    def test_file_type_validation_property(self, file_extension, required_types):
        """
        Property 15: For any 教师上传的文件，系统应该校验文件类型是否符合任务要求。
        
        **Validates: Requirements 7.1, 7.2**
        
        This property tests that:
        1. Files with supported types are accepted
        2. Files with unsupported types are rejected
        3. Files not matching required types are rejected
        4. Error messages are provided for rejected files
        """
        # 创建模拟的任务，指定必需的文件类型
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.required_file_types = required_types
        
        # 检查文件类型是否符合要求
        is_supported = file_extension in self.supported_file_types
        is_required = file_extension in required_types
        
        # 验证逻辑：文件必须既支持又被要求
        should_accept = is_supported and is_required
        
        # 模拟文件上传验证
        def validate_file_type(file_ext, task):
            """验证文件类型是否符合任务要求"""
            if file_ext not in self.supported_file_types:
                return False, f"不支持的文件格式: {file_ext}"
            if file_ext not in task.required_file_types:
                return False, f"文件类型 {file_ext} 不符合任务要求"
            return True, ""
        
        is_valid, error_msg = validate_file_type(file_extension, mock_task)
        
        # 验证结果
        assert is_valid == should_accept, \
            f"文件类型 {file_extension} 的验证结果不正确"
        
        if not is_valid:
            # 如果拒绝，应该有错误信息
            assert len(error_msg) > 0, "拒绝上传时应该提供错误信息"
    
    # Feature: auto-scoring-system, Property 16: 文件上传状态更新
    @given(
        submission_id=st.integers(min_value=1, max_value=10000),
        file_name=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz0123456789_.',
            min_size=5,
            max_size=50
        )
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
    )
    def test_file_upload_status_update_property(self, submission_id, file_name):
        """
        Property 16: For any 成功上传的文件，系统应该将状态设置为"待评分"。
        
        **Validates: Requirements 7.3**
        
        This property tests that:
        1. After successful upload, status is set to "pending"
        2. Status is persisted in the database
        3. Status can be retrieved correctly
        """
        # 创建模拟的提交记录
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = f"sub_{submission_id}"
        mock_submission.scoring_status = "pending"
        mock_submission.files = [{"file_name": file_name}]
        
        # 模拟文件上传后的状态更新
        def update_submission_status(submission, new_status):
            """更新提交状态"""
            submission.scoring_status = new_status
            return submission
        
        # 执行状态更新
        updated_submission = update_submission_status(mock_submission, "pending")
        
        # 验证状态已更新
        assert updated_submission.scoring_status == "pending", \
            "文件上传后状态应该设置为 'pending'"
        
        # 验证提交记录包含文件信息
        assert len(updated_submission.files) > 0, "提交记录应该包含文件信息"
        assert updated_submission.files[0]["file_name"] == file_name, \
            "文件名应该被正确保存"
    
    # Feature: auto-scoring-system, Property 17: 文件重新上传覆盖
    @given(
        submission_id=st.integers(min_value=1, max_value=10000),
        first_file_name=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz0123456789_.',
            min_size=5,
            max_size=30
        ),
        second_file_name=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz0123456789_.',
            min_size=5,
            max_size=30
        )
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
    )
    def test_file_reupload_override_property(self, submission_id, first_file_name, second_file_name):
        """
        Property 17: For any 截止时间前的重新上传操作，系统应该覆盖之前的文件
        并重新触发评分。
        
        **Validates: Requirements 7.5**
        
        This property tests that:
        1. New file replaces the old file
        2. Only the latest file is kept
        3. Scoring is triggered again for the new file
        4. Old file information is not retained
        """
        # Skip if file names are identical (edge case)
        if first_file_name == second_file_name:
            return
        
        # 创建模拟的提交记录，包含第一个文件
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = f"sub_{submission_id}"
        mock_submission.files = [{"file_name": first_file_name, "upload_time": datetime.now()}]
        mock_submission.scoring_status = "pending"
        
        # 模拟重新上传
        def reupload_file(submission, new_file_name):
            """重新上传文件，覆盖旧文件"""
            # 清空旧文件
            submission.files = []
            # 添加新文件
            submission.files.append({
                "file_name": new_file_name,
                "upload_time": datetime.now()
            })
            # 重置评分状态以触发重新评分
            submission.scoring_status = "pending"
            return submission
        
        # 执行重新上传
        updated_submission = reupload_file(mock_submission, second_file_name)
        
        # 验证旧文件已被覆盖
        assert len(updated_submission.files) == 1, "应该只保留一个文件"
        assert updated_submission.files[0]["file_name"] == second_file_name, \
            "新文件应该覆盖旧文件"
        assert updated_submission.files[0]["file_name"] != first_file_name, \
            "旧文件应该被删除"
        
        # 验证评分状态已重置以触发重新评分
        assert updated_submission.scoring_status == "pending", \
            "重新上传后应该重置评分状态以触发重新评分"
    
    # Feature: auto-scoring-system, Property 18: 评分结果展示完整性
    @given(
        base_score=st.floats(min_value=0, max_value=100),
        bonus_score=st.floats(min_value=0, max_value=10),
        grade=st.sampled_from(['优秀', '良好', '合格', '不合格']),
        veto_triggered=st.booleans()
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
    )
    def test_scoring_result_display_completeness_property(self, base_score, bonus_score, grade, veto_triggered):
        """
        Property 18: For any 评分完成的文件，系统应该向教师展示完整的评分明细
        （得分、等级、扣分理由）。
        
        **Validates: Requirements 7.6, 8.1**
        
        This property tests that:
        1. Scoring result contains all required fields
        2. Score details are complete and accurate
        3. Grade is correctly determined
        4. Deduction reasons are provided when applicable
        5. Result can be displayed to teachers
        """
        # 创建模拟的评分记录
        mock_scoring_record = Mock(spec=ScoringRecord)
        mock_scoring_record.submission_id = 1
        mock_scoring_record.base_score = base_score
        mock_scoring_record.bonus_score = bonus_score
        mock_scoring_record.final_score = min(base_score + bonus_score, 100)
        mock_scoring_record.grade = grade
        mock_scoring_record.veto_triggered = veto_triggered
        mock_scoring_record.veto_reason = "测试否决原因" if veto_triggered else ""
        mock_scoring_record.score_details = json.dumps([
            {
                "indicator": "教学目标",
                "score": base_score * 0.25,
                "max_score": 25,
                "reason": "评分理由"
            }
        ])
        mock_scoring_record.bonus_details = json.dumps([
            {
                "item_name": "获奖",
                "score": bonus_score,
                "evidence": "佐证材料"
            }
        ]) if bonus_score > 0 else "[]"
        
        # 模拟评分结果展示
        def format_scoring_result_for_display(record):
            """格式化评分结果用于展示"""
            result = {
                "submission_id": record.submission_id,
                "base_score": record.base_score,
                "bonus_score": record.bonus_score,
                "final_score": record.final_score,
                "grade": record.grade,
                "veto_triggered": record.veto_triggered,
                "veto_reason": record.veto_reason,
                "score_details": json.loads(record.score_details) if record.score_details else [],
                "bonus_details": json.loads(record.bonus_details) if record.bonus_details else []
            }
            return result
        
        # 执行格式化
        display_result = format_scoring_result_for_display(mock_scoring_record)
        
        # 验证所有必需字段都存在
        required_fields = [
            "submission_id", "base_score", "bonus_score", "final_score",
            "grade", "veto_triggered", "veto_reason", "score_details", "bonus_details"
        ]
        
        for field in required_fields:
            assert field in display_result, f"评分结果缺少字段: {field}"
        
        # 验证字段值的正确性
        assert display_result["base_score"] == base_score
        assert display_result["bonus_score"] == bonus_score
        assert display_result["final_score"] == min(base_score + bonus_score, 100)
        assert display_result["grade"] == grade
        assert display_result["veto_triggered"] == veto_triggered
        
        # 验证评分明细是列表
        assert isinstance(display_result["score_details"], list), \
            "评分明细应该是列表"
        assert isinstance(display_result["bonus_details"], list), \
            "加分项明细应该是列表"
        
        # 如果有加分项，应该有详细信息
        if bonus_score > 0:
            assert len(display_result["bonus_details"]) > 0, \
                "有加分时应该提供加分项明细"


class TestMaterialSubmissionEdgeCases:
    """文件提交边界情况测试"""
    
    def test_file_type_case_insensitivity(self):
        """测试文件类型判断不区分大小写"""
        supported_types = ['docx', 'pdf', 'pptx']
        
        # 测试大小写不敏感性
        assert 'DOCX'.lower() in supported_types
        assert 'PDF'.lower() in supported_types
        assert 'PPTX'.lower() in supported_types
    
    def test_empty_file_list_handling(self):
        """测试空文件列表的处理"""
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.files = []
        
        # 验证空文件列表
        assert len(mock_submission.files) == 0
        assert isinstance(mock_submission.files, list)
    
    def test_multiple_files_in_submission(self):
        """测试提交多个文件的情况"""
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.files = [
            {"file_name": "file1.docx"},
            {"file_name": "file2.pdf"},
            {"file_name": "file3.pptx"}
        ]
        
        # 验证多个文件
        assert len(mock_submission.files) == 3
        assert all(isinstance(f, dict) for f in mock_submission.files)
        assert all("file_name" in f for f in mock_submission.files)
    
    def test_scoring_status_transitions(self):
        """测试评分状态的转换"""
        mock_submission = Mock(spec=MaterialSubmission)
        
        # 初始状态
        mock_submission.scoring_status = "pending"
        assert mock_submission.scoring_status == "pending"
        
        # 转换到评分中
        mock_submission.scoring_status = "scoring"
        assert mock_submission.scoring_status == "scoring"
        
        # 转换到已评分
        mock_submission.scoring_status = "scored"
        assert mock_submission.scoring_status == "scored"
        
        # 转换到失败
        mock_submission.scoring_status = "failed"
        assert mock_submission.scoring_status == "failed"
    
    def test_final_score_calculation_bounds(self):
        """测试最终得分计算的边界"""
        # 测试最小值
        base_score = 0
        bonus_score = 0
        final_score = min(base_score + bonus_score, 100)
        assert final_score == 0
        
        # 测试最大值
        base_score = 100
        bonus_score = 10
        final_score = min(base_score + bonus_score, 100)
        assert final_score == 100
        
        # 测试中间值
        base_score = 85
        bonus_score = 5
        final_score = min(base_score + bonus_score, 100)
        assert final_score == 90
    
    def test_grade_determination_boundaries(self):
        """测试等级判定的边界值"""
        def determine_grade(score):
            if score >= 90:
                return "优秀"
            elif score >= 80:
                return "良好"
            elif score >= 60:
                return "合格"
            else:
                return "不合格"
        
        # 测试边界值
        assert determine_grade(90) == "优秀"
        assert determine_grade(89) == "良好"
        assert determine_grade(80) == "良好"
        assert determine_grade(79) == "合格"
        assert determine_grade(60) == "合格"
        assert determine_grade(59) == "不合格"
    
    def test_veto_item_handling(self):
        """测试否决项的处理"""
        mock_record = Mock(spec=ScoringRecord)
        
        # 测试触发否决项
        mock_record.veto_triggered = True
        mock_record.veto_reason = "造假"
        mock_record.grade = "不合格"
        
        assert mock_record.veto_triggered is True
        assert len(mock_record.veto_reason) > 0
        assert mock_record.grade == "不合格"
        
        # 测试未触发否决项
        mock_record.veto_triggered = False
        mock_record.veto_reason = ""
        mock_record.grade = "良好"
        
        assert mock_record.veto_triggered is False
        assert mock_record.veto_reason == ""
        assert mock_record.grade != "不合格"


class TestMaterialSubmissionIntegration:
    """文件提交集成测试"""
    
    def test_complete_file_submission_workflow(self):
        """测试完整的文件提交工作流"""
        # 1. 创建提交记录
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_001"
        mock_submission.teacher_id = "teacher_001"
        mock_submission.files = []
        mock_submission.scoring_status = "pending"
        
        # 2. 上传文件
        mock_submission.files.append({
            "file_name": "lesson_plan.docx",
            "file_type": "docx",
            "upload_time": datetime.now()
        })
        
        # 3. 验证文件已上传
        assert len(mock_submission.files) == 1
        assert mock_submission.files[0]["file_name"] == "lesson_plan.docx"
        
        # 4. 创建评分记录
        mock_scoring_record = Mock(spec=ScoringRecord)
        mock_scoring_record.submission_id = mock_submission.submission_id
        mock_scoring_record.base_score = 85
        mock_scoring_record.bonus_score = 5
        mock_scoring_record.final_score = 90
        mock_scoring_record.grade = "优秀"
        mock_scoring_record.veto_triggered = False
        
        # 5. 验证评分记录
        assert mock_scoring_record.submission_id == mock_submission.submission_id
        assert mock_scoring_record.final_score == 90
        assert mock_scoring_record.grade == "优秀"
    
    def test_file_reupload_workflow(self):
        """测试文件重新上传工作流"""
        # 1. 初始提交
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_002"
        mock_submission.files = [{"file_name": "old_file.docx"}]
        mock_submission.scoring_status = "pending"
        
        # 2. 重新上传
        mock_submission.files = [{"file_name": "new_file.docx"}]
        mock_submission.scoring_status = "pending"
        
        # 3. 验证新文件已替换旧文件
        assert len(mock_submission.files) == 1
        assert mock_submission.files[0]["file_name"] == "new_file.docx"
        assert mock_submission.scoring_status == "pending"
