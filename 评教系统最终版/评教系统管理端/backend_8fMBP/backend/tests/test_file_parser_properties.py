"""
文件解析器属性测试

使用 Hypothesis 进行属性测试，验证文件解析器的通用正确性属性
"""

import os
import sys
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from utils.file_parser import (
    FileParser,
    UnsupportedFormatError,
    EmptyFileError,
    FileCorruptedError,
    is_supported_format
)


class TestFileParserProperties:
    """文件解析器属性测试"""
    
    # Feature: auto-scoring-system, Property 8: 不支持文件格式错误处理
    @given(
        file_extension=st.sampled_from([
            'txt', 'jpg', 'png', 'gif', 'mp3', 'mp4', 'zip', 'rar',
            'exe', 'bat', 'sh', 'json', 'xml', 'html', 'css', 'js',
            'java', 'cpp', 'c', 'py', 'rb', 'go', 'rs', 'ts', 'jsx'
        ])
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
    )
    def test_unsupported_format_error_handling(self, file_extension, tmp_path):
        """
        Property 8: For any 不支持的文件格式，文件解析器应该返回错误信息并标记文件为"解析失败"状态。
        
        **Validates: Requirements 4.4**
        
        This property verifies that:
        1. Unsupported file formats raise UnsupportedFormatError
        2. The error message is informative
        3. The error contains the unsupported format information
        """
        parser = FileParser()
        
        # 创建一个不支持的文件
        test_file = tmp_path / f"test.{file_extension}"
        test_file.write_text("test content")
        
        # 验证格式不被支持
        assert not is_supported_format(file_extension), \
            f"Format {file_extension} should not be supported"
        
        # 验证解析器抛出 UnsupportedFormatError
        with pytest.raises(UnsupportedFormatError) as exc_info:
            parser.parse_file(str(test_file))
        
        # 验证错误信息包含有用的信息
        error_message = str(exc_info.value)
        assert "不支持" in error_message or "unsupported" in error_message.lower(), \
            f"Error message should indicate unsupported format: {error_message}"
        
        # 验证错误信息包含文件扩展名
        assert file_extension in error_message or file_extension.upper() in error_message, \
            f"Error message should contain file extension {file_extension}: {error_message}"
    
    # Property: 支持的格式应该被正确识别
    @given(
        file_extension=st.sampled_from(['docx', 'pdf', 'pptx', 'ppt'])
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_supported_format_recognition(self, file_extension):
        """
        Property: For any 支持的文件格式，is_supported_format 应该返回 True
        
        This property verifies that supported formats are correctly identified.
        """
        assert is_supported_format(file_extension) is True, \
            f"Format {file_extension} should be supported"
    
    # Property: 文件类型检测应该不区分大小写
    @given(
        file_extension=st.sampled_from(['DOCX', 'Docx', 'PDF', 'Pdf', 'PPTX', 'Pptx'])
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_case_insensitive_format_detection(self, file_extension, tmp_path):
        """
        Property: For any 文件扩展名，格式检测应该不区分大小写
        
        This property verifies that file format detection is case-insensitive.
        """
        parser = FileParser()
        
        # 创建一个文件
        test_file = tmp_path / f"test.{file_extension}"
        test_file.write_text("test content")
        
        # 获取文件信息
        info = parser.get_file_info(str(test_file))
        
        # 验证文件类型被正确识别（转换为小写）
        expected_type = file_extension.lower()
        assert info['file_type'] == expected_type, \
            f"File type should be {expected_type}, got {info['file_type']}"
        
        # 验证支持状态
        assert info['is_supported'] is True, \
            f"Format {file_extension} should be supported"
    
    # Property: 错误处理应该是一致的
    @given(
        file_extension=st.sampled_from([
            'txt', 'jpg', 'png', 'gif', 'mp3', 'mp4', 'zip', 'rar'
        ])
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_consistent_error_handling(self, file_extension, tmp_path):
        """
        Property: For any 不支持的文件格式，多次调用应该产生一致的错误
        
        This property verifies that error handling is consistent across multiple calls.
        """
        parser = FileParser()
        
        # 创建一个不支持的文件
        test_file = tmp_path / f"test.{file_extension}"
        test_file.write_text("test content")
        
        # 多次调用应该产生相同的错误
        errors = []
        for _ in range(3):
            try:
                parser.parse_file(str(test_file))
            except UnsupportedFormatError as e:
                errors.append(str(e))
        
        # 验证所有错误消息都包含相同的关键信息
        assert len(errors) == 3, "Should have 3 errors"
        
        # 验证错误消息的一致性
        for error_msg in errors:
            assert "不支持" in error_msg or "unsupported" in error_msg.lower(), \
                f"Error message should indicate unsupported format: {error_msg}"
    
    # Property: 文件信息应该总是包含必需的字段
    @given(
        file_extension=st.sampled_from([
            'docx', 'pdf', 'pptx', 'txt', 'jpg', 'png'
        ])
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_file_info_completeness(self, file_extension, tmp_path):
        """
        Property: For any 文件，get_file_info 应该返回包含所有必需字段的信息
        
        This property verifies that file info always contains required fields.
        """
        parser = FileParser()
        
        # 创建一个文件
        test_file = tmp_path / f"test.{file_extension}"
        test_file.write_text("test content")
        
        # 获取文件信息
        info = parser.get_file_info(str(test_file))
        
        # 验证必需字段存在
        required_fields = [
            'file_name',
            'file_type',
            'file_size',
            'is_supported',
            'file_size_mb',
            'modified_time'
        ]
        
        for field in required_fields:
            assert field in info, f"File info should contain field: {field}"
        
        # 验证字段值的有效性
        assert isinstance(info['file_name'], str), "file_name should be string"
        assert isinstance(info['file_type'], str), "file_type should be string"
        assert isinstance(info['file_size'], int), "file_size should be int"
        assert isinstance(info['is_supported'], bool), "is_supported should be bool"
        assert isinstance(info['file_size_mb'], float), "file_size_mb should be float"
        assert isinstance(info['modified_time'], str), "modified_time should be string"
        
        # 验证字段值的合理性
        assert info['file_size'] > 0, "file_size should be positive"
        assert info['file_size_mb'] >= 0, "file_size_mb should be non-negative"
        assert info['file_type'] == file_extension.lower(), \
            f"file_type should be {file_extension.lower()}"


class TestFileParserErrorMessages:
    """文件解析器错误消息测试"""
    
    # Property: 错误消息应该包含有用的调试信息
    @given(
        file_extension=st.sampled_from([
            'txt', 'jpg', 'png', 'gif', 'mp3', 'mp4', 'zip', 'rar',
            'exe', 'bat', 'sh', 'json', 'xml', 'html'
        ])
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_error_message_informativeness(self, file_extension, tmp_path):
        """
        Property: For any 不支持的文件格式，错误消息应该包含有用的调试信息
        
        This property verifies that error messages are informative for debugging.
        """
        parser = FileParser()
        
        # 创建一个不支持的文件
        test_file = tmp_path / f"test.{file_extension}"
        test_file.write_text("test content")
        
        # 捕获错误
        try:
            parser.parse_file(str(test_file))
            assert False, "Should raise UnsupportedFormatError"
        except UnsupportedFormatError as e:
            error_msg = str(e)
            
            # 验证错误消息包含文件扩展名
            assert file_extension in error_msg or file_extension.upper() in error_msg, \
                f"Error message should contain file extension: {error_msg}"
            
            # 验证错误消息不为空
            assert len(error_msg) > 0, "Error message should not be empty"
            
            # 验证错误消息长度合理（不过长）
            assert len(error_msg) < 500, "Error message should not be too long"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
