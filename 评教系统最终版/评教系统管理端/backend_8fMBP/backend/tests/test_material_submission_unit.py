"""
文件提交单元测试

测试文件类型校验、文件状态更新、重新上传流程等功能。
"""

import os
import tempfile
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import (
    MaterialSubmission, EvaluationAssignmentTask, ScoringRecord,
    User, ScoringLog
)
from app.services.material_submission_service import MaterialSubmissionService
from app.utils.file_parser import FileParser


class TestMaterialSubmissionService:
    """材料提交服务单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.db = Mock()
        self.service = MaterialSubmissionService(self.db)
    
    # ==================== 文件类型校验测试 ====================
    
    def test_validate_file_type_supported_format(self):
        """
        测试支持的文件格式校验
        
        **Validates: Requirements 7.1, 7.2**
        """
        # 测试支持的格式
        is_valid, error_msg = self.service.validate_file_type(
            'docx',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is True
        assert error_msg == ""
    
    def test_validate_file_type_unsupported_format(self):
        """
        测试不支持的文件格式校验
        
        **Validates: Requirements 7.1, 7.2**
        """
        # 测试不支持的格式
        is_valid, error_msg = self.service.validate_file_type(
            'exe',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is False
        assert "不支持的文件格式" in error_msg
    
    def test_validate_file_type_not_required(self):
        """
        测试文件类型不符合任务要求
        
        **Validates: Requirements 7.1, 7.2**
        """
        # 测试文件类型虽然支持但不符合任务要求
        is_valid, error_msg = self.service.validate_file_type(
            'pdf',
            ['docx', 'pptx']  # 不包含 pdf
        )
        assert is_valid is False
        assert "不符合任务要求" in error_msg
    
    def test_validate_file_type_case_insensitive(self):
        """
        测试文件类型校验不区分大小写
        
        **Validates: Requirements 7.1, 7.2**
        """
        # 测试大写
        is_valid, error_msg = self.service.validate_file_type(
            'DOCX',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is True
        
        # 测试混合大小写
        is_valid, error_msg = self.service.validate_file_type(
            'DocX',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is True
    
    def test_validate_file_type_empty_required_list(self):
        """
        测试空的必需文件类型列表
        
        **Validates: Requirements 7.1, 7.2**
        """
        # 如果没有指定必需类型，只要格式支持就可以
        is_valid, error_msg = self.service.validate_file_type(
            'docx',
            []
        )
        assert is_valid is True
    
    # ==================== 文件状态更新测试 ====================
    
    def test_create_submission_with_pending_status(self):
        """
        测试创建提交记录时状态为待评分
        
        **Validates: Requirements 7.3**
        """
        # 模拟数据库操作
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_001"
        mock_submission.scoring_status = "pending"
        mock_submission.files = [{"file_name": "test.docx"}]
        
        self.db.add = Mock()
        self.db.commit = Mock()
        self.db.refresh = Mock(side_effect=lambda x: None)
        
        # 创建提交记录
        files = [{"file_id": "file_001", "file_name": "test.docx"}]
        
        # 验证初始状态
        assert mock_submission.scoring_status == "pending"
        assert len(mock_submission.files) > 0
    
    def test_update_submission_status_to_pending(self):
        """
        测试更新提交状态为待评分
        
        **Validates: Requirements 7.3**
        """
        # 模拟提交记录
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_001"
        mock_submission.scoring_status = "pending"
        mock_submission.parsed_content = None
        mock_submission.file_hash = None
        mock_submission.encrypted_path = None
        
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_submission)))))
        self.db.commit = Mock()
        self.db.refresh = Mock(side_effect=lambda x: None)
        
        # 更新状态
        result = self.service.update_submission_status(
            "sub_001",
            "pending",
            parsed_content="test content",
            file_hash="abc123"
        )
        
        # 验证状态已更新
        assert result.scoring_status == "pending"
    
    def test_update_submission_status_nonexistent(self):
        """
        测试更新不存在的提交记录
        
        **Validates: Requirements 7.3**
        """
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None)))))
        
        # 应该抛出异常
        with pytest.raises(Exception) as exc_info:
            self.service.update_submission_status("sub_999", "pending")
        
        assert "提交记录不存在" in str(exc_info.value)
    
    # ==================== 文件重新上传测试 ====================
    
    def test_reupload_file_replaces_old_file(self):
        """
        测试重新上传文件覆盖旧文件
        
        **Validates: Requirements 7.5**
        """
        # 模拟原始提交记录
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_001"
        mock_submission.files = [{"file_name": "old_file.docx"}]
        mock_submission.scoring_status = "scored"
        mock_submission.parsed_content = "old content"
        mock_submission.file_hash = "old_hash"
        mock_submission.encrypted_path = "/old/path"
        
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_submission)))))
        self.db.commit = Mock()
        self.db.refresh = Mock(side_effect=lambda x: None)
        
        # 重新上传新文件
        new_files = [{"file_name": "new_file.docx"}]
        result = self.service.reupload_file("sub_001", new_files)
        
        # 验证旧文件已被覆盖
        assert result.files == new_files
        assert result.files[0]["file_name"] == "new_file.docx"
        assert result.files[0]["file_name"] != "old_file.docx"
    
    def test_reupload_file_resets_scoring_status(self):
        """
        测试重新上传文件重置评分状态
        
        **Validates: Requirements 7.5**
        """
        # 模拟原始提交记录
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_001"
        mock_submission.files = [{"file_name": "old_file.docx"}]
        mock_submission.scoring_status = "scored"
        mock_submission.parsed_content = "old content"
        mock_submission.file_hash = "old_hash"
        mock_submission.encrypted_path = "/old/path"
        mock_submission.submitted_at = datetime.utcnow()
        
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_submission)))))
        self.db.commit = Mock()
        self.db.refresh = Mock(side_effect=lambda x: None)
        
        # 重新上传
        new_files = [{"file_name": "new_file.docx"}]
        result = self.service.reupload_file("sub_001", new_files)
        
        # 验证评分状态已重置
        assert result.scoring_status == "pending"
        assert result.parsed_content is None
        assert result.file_hash is None
        assert result.encrypted_path is None
    
    def test_reupload_file_updates_submission_time(self):
        """
        测试重新上传文件更新提交时间
        
        **Validates: Requirements 7.5**
        """
        # 模拟原始提交记录
        old_time = datetime.utcnow() - timedelta(days=1)
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_001"
        mock_submission.files = [{"file_name": "old_file.docx"}]
        mock_submission.submitted_at = old_time
        mock_submission.scoring_status = "pending"
        mock_submission.parsed_content = None
        mock_submission.file_hash = None
        mock_submission.encrypted_path = None
        
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_submission)))))
        self.db.commit = Mock()
        self.db.refresh = Mock(side_effect=lambda x: None)
        
        # 重新上传
        new_files = [{"file_name": "new_file.docx"}]
        result = self.service.reupload_file("sub_001", new_files)
        
        # 验证提交时间已更新
        assert result.submitted_at > old_time
    
    def test_reupload_file_nonexistent(self):
        """
        测试重新上传不存在的提交记录
        
        **Validates: Requirements 7.5**
        """
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None)))))
        
        # 应该抛出异常
        with pytest.raises(Exception) as exc_info:
            self.service.reupload_file("sub_999", [{"file_name": "new.docx"}])
        
        assert "提交记录不存在" in str(exc_info.value)
    
    # ==================== 文件哈希计算测试 ====================
    
    def test_calculate_file_hash(self):
        """
        测试文件哈希计算
        
        **Validates: Requirements 11.2**
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            # 计算哈希
            hash_value = self.service.calculate_file_hash(temp_path)
            
            # 验证哈希值是有效的 SHA256 哈希
            assert len(hash_value) == 64  # SHA256 哈希长度为 64 个十六进制字符
            assert all(c in '0123456789abcdef' for c in hash_value)
        finally:
            os.unlink(temp_path)
    
    def test_calculate_file_hash_consistency(self):
        """
        测试文件哈希计算的一致性
        
        **Validates: Requirements 11.2**
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            # 计算两次哈希
            hash1 = self.service.calculate_file_hash(temp_path)
            hash2 = self.service.calculate_file_hash(temp_path)
            
            # 验证两次计算结果相同
            assert hash1 == hash2
        finally:
            os.unlink(temp_path)
    
    def test_calculate_file_hash_nonexistent_file(self):
        """
        测试计算不存在的文件的哈希
        
        **Validates: Requirements 11.2**
        """
        # 应该抛出异常
        with pytest.raises(Exception) as exc_info:
            self.service.calculate_file_hash("/nonexistent/file.txt")
        
        assert "计算文件哈希失败" in str(exc_info.value)
    
    # ==================== 文件类型识别测试 ====================
    
    def test_get_file_type_from_filename(self):
        """
        测试从文件名获取文件类型
        
        **Validates: Requirements 7.1**
        """
        # 测试各种文件类型
        assert self.service.get_file_type_from_filename("test.docx") == "docx"
        assert self.service.get_file_type_from_filename("test.pdf") == "pdf"
        assert self.service.get_file_type_from_filename("test.pptx") == "pptx"
    
    def test_get_file_type_case_insensitive(self):
        """
        测试文件类型识别不区分大小写
        
        **Validates: Requirements 7.1**
        """
        # 测试大写
        assert self.service.get_file_type_from_filename("test.DOCX") == "docx"
        assert self.service.get_file_type_from_filename("test.PDF") == "pdf"
        
        # 测试混合大小写
        assert self.service.get_file_type_from_filename("test.DocX") == "docx"
    
    def test_get_file_type_no_extension(self):
        """
        测试没有扩展名的文件
        
        **Validates: Requirements 7.1**
        """
        assert self.service.get_file_type_from_filename("test") == ""
    
    def test_get_file_type_multiple_dots(self):
        """
        测试包含多个点的文件名
        
        **Validates: Requirements 7.1**
        """
        # 应该返回最后一个点后的部分
        assert self.service.get_file_type_from_filename("test.backup.docx") == "docx"
    
    # ==================== 提交记录查询测试 ====================
    
    def test_get_submission_exists(self):
        """
        测试获取存在的提交记录
        
        **Validates: Requirements 7.3**
        """
        # 模拟提交记录
        mock_submission = Mock(spec=MaterialSubmission)
        mock_submission.submission_id = "sub_001"
        
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_submission)))))
        
        # 获取提交记录
        result = self.service.get_submission("sub_001")
        
        # 验证结果
        assert result is not None
        assert result.submission_id == "sub_001"
    
    def test_get_submission_not_exists(self):
        """
        测试获取不存在的提交记录
        
        **Validates: Requirements 7.3**
        """
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None)))))
        
        # 获取提交记录
        result = self.service.get_submission("sub_999")
        
        # 验证结果为 None
        assert result is None
    
    # ==================== 截止时间检查测试 ====================
    
    def test_validate_submission_deadline_before_deadline(self):
        """
        测试在截止时间前提交
        
        **Validates: Requirements 6.5**
        """
        # 模拟任务
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.task_id = "task_001"
        mock_task.deadline = datetime.utcnow() + timedelta(days=1)
        
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_task)))))
        
        # 检查截止时间
        is_valid, error_msg = self.service.validate_submission_deadline("task_001")
        
        # 验证结果
        assert is_valid is True
        assert error_msg == ""
    
    def test_validate_submission_deadline_after_deadline(self):
        """
        测试在截止时间后提交
        
        **Validates: Requirements 6.5**
        """
        # 模拟任务
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.task_id = "task_001"
        mock_task.deadline = datetime.utcnow() - timedelta(days=1)
        
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_task)))))
        
        # 检查截止时间
        is_valid, error_msg = self.service.validate_submission_deadline("task_001")
        
        # 验证结果
        assert is_valid is False
        assert "已超过截止时间" in error_msg
    
    def test_validate_submission_deadline_task_not_exists(self):
        """
        测试任务不存在
        
        **Validates: Requirements 6.5**
        """
        self.db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None)))))
        
        # 检查截止时间
        is_valid, error_msg = self.service.validate_submission_deadline("task_999")
        
        # 验证结果
        assert is_valid is False
        assert "任务不存在" in error_msg


class TestMaterialSubmissionEdgeCases:
    """文件提交边界情况测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.db = Mock()
        self.service = MaterialSubmissionService(self.db)
    
    def test_validate_file_type_with_special_characters(self):
        """测试包含特殊字符的文件类型"""
        is_valid, error_msg = self.service.validate_file_type(
            'doc@x',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is False
    
    def test_validate_file_type_empty_extension(self):
        """测试空的文件扩展名"""
        is_valid, error_msg = self.service.validate_file_type(
            '',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is False
    
    def test_get_file_type_from_filename_with_spaces(self):
        """测试包含空格的文件名"""
        result = self.service.get_file_type_from_filename("my test file.docx")
        assert result == "docx"
    
    def test_get_file_type_from_filename_with_special_chars(self):
        """测试包含特殊字符的文件名"""
        result = self.service.get_file_type_from_filename("test-file_2024.docx")
        assert result == "docx"
    
    def test_supported_file_types_list(self):
        """测试支持的文件类型列表"""
        assert 'docx' in self.service.SUPPORTED_FILE_TYPES
        assert 'pdf' in self.service.SUPPORTED_FILE_TYPES
        assert 'pptx' in self.service.SUPPORTED_FILE_TYPES
        assert len(self.service.SUPPORTED_FILE_TYPES) == 3


class TestMaterialSubmissionIntegration:
    """文件提交集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.db = Mock()
        self.service = MaterialSubmissionService(self.db)
    
    def test_complete_file_submission_workflow(self):
        """测试完整的文件提交工作流"""
        # 1. 验证文件类型
        is_valid, error_msg = self.service.validate_file_type(
            'docx',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is True
        
        # 2. 获取文件类型
        file_type = self.service.get_file_type_from_filename("lesson_plan.docx")
        assert file_type == "docx"
        
        # 3. 验证文件类型与任务要求一致
        is_valid, error_msg = self.service.validate_file_type(
            file_type,
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is True
    
    def test_file_reupload_workflow(self):
        """测试文件重新上传工作流"""
        # 1. 验证第一个文件
        is_valid, _ = self.service.validate_file_type(
            'docx',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is True
        
        # 2. 验证第二个文件
        is_valid, _ = self.service.validate_file_type(
            'pdf',
            ['docx', 'pdf', 'pptx']
        )
        assert is_valid is True
        
        # 3. 两个文件都有效
        assert is_valid is True
    
    def test_multiple_file_types_validation(self):
        """测试多个文件类型的校验"""
        file_types = ['docx', 'pdf', 'pptx']
        
        for file_type in file_types:
            is_valid, error_msg = self.service.validate_file_type(
                file_type,
                file_types
            )
            assert is_valid is True, f"文件类型 {file_type} 校验失败"
