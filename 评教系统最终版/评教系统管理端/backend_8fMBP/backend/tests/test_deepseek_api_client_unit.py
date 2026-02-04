"""
Deepseek API 客户端单元测试

测试 DeepseekAPIClient 的各种功能
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import Timeout, ConnectionError

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services.deepseek_client import (
    DeepseekAPIClient,
    APICallError,
    APITimeoutError,
    APIResponseError,
    init_deepseek_client,
    get_deepseek_client,
    close_deepseek_client
)


class TestDeepseekAPIClientInitialization:
    """Deepseek API 客户端初始化测试"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = DeepseekAPIClient(
            api_key="test-key",
            api_url="https://api.deepseek.com/v1/chat/completions",
            model="deepseek-chat",
            temperature=0.1,
            max_retries=3,
            timeout=30
        )
        
        assert client.api_key == "test-key"
        assert client.model == "deepseek-chat"
        assert client.temperature == 0.1
        assert client.max_retries == 3
        assert client.timeout == 30
        assert client.session is not None
        
        client.close()
    
    def test_client_default_parameters(self):
        """测试客户端默认参数"""
        client = DeepseekAPIClient(api_key="test-key")
        
        assert client.api_url == "https://api.deepseek.com/v1/chat/completions"
        assert client.model == "deepseek-chat"
        assert client.temperature == 0.1
        assert client.max_retries == 3
        assert client.timeout == 30
        
        client.close()
    
    def test_client_context_manager(self):
        """测试客户端上下文管理器"""
        with DeepseekAPIClient(api_key="test-key") as client:
            assert client is not None
            assert client.session is not None


class TestDeepseekAPIClientResponseParsing:
    """Deepseek API 客户端响应解析测试"""
    
    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        return DeepseekAPIClient(api_key="test-key")
    
    def test_parse_valid_response(self, client):
        """测试解析有效的 API 响应"""
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "veto_check": {"triggered": False, "reason": ""},
                            "score_details": [
                                {"indicator": "教学目标", "score": 25, "max_score": 25, "reason": "目标明确"}
                            ],
                            "base_score": 85,
                            "grade_suggestion": "良好",
                            "summary": "总体评价良好"
                        })
                    }
                }
            ]
        }
        
        result = client._parse_response(response_data)
        
        assert result["veto_check"]["triggered"] is False
        assert result["base_score"] == 85
        assert result["grade_suggestion"] == "良好"
        
        client.close()
    
    def test_parse_response_with_json_in_text(self, client):
        """测试解析包含 JSON 的文本响应"""
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "这是一个评分结果：\n" + json.dumps({
                            "veto_check": {"triggered": False, "reason": ""},
                            "score_details": [],
                            "base_score": 75,
                            "grade_suggestion": "合格",
                            "summary": "评价"
                        }) + "\n结束"
                    }
                }
            ]
        }
        
        result = client._parse_response(response_data)
        
        assert result["base_score"] == 75
        assert result["grade_suggestion"] == "合格"
        
        client.close()
    
    def test_parse_response_missing_choices(self, client):
        """测试解析缺少 choices 字段的响应"""
        response_data = {"data": "invalid"}
        
        with pytest.raises(APIResponseError) as exc_info:
            client._parse_response(response_data)
        
        assert "choices" in str(exc_info.value)
        
        client.close()
    
    def test_parse_response_empty_content(self, client):
        """测试解析空内容的响应"""
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": ""
                    }
                }
            ]
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            client._parse_response(response_data)
        
        assert "为空" in str(exc_info.value)
        
        client.close()
    
    def test_parse_response_invalid_json(self, client):
        """测试解析无效 JSON 的响应"""
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "这不是 JSON 格式"
                    }
                }
            ]
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            client._parse_response(response_data)
        
        assert "JSON" in str(exc_info.value)
        
        client.close()


class TestDeepseekAPIClientValidation:
    """Deepseek API 客户端验证测试"""
    
    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        return DeepseekAPIClient(api_key="test-key")
    
    def test_validate_valid_scoring_result(self, client):
        """测试验证有效的评分结果"""
        result = {
            "veto_check": {"triggered": False, "reason": ""},
            "score_details": [{"indicator": "test", "score": 10, "max_score": 10, "reason": "good"}],
            "base_score": 85,
            "grade_suggestion": "良好",
            "summary": "评价"
        }
        
        assert client._validate_scoring_result(result) is True
        
        client.close()
    
    def test_validate_missing_required_field(self, client):
        """测试验证缺少必需字段的结果"""
        result = {
            "veto_check": {"triggered": False},
            "score_details": [],
            "base_score": 85
            # 缺少 grade_suggestion 和 summary
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            client._validate_scoring_result(result)
        
        assert "必需字段" in str(exc_info.value)
        
        client.close()
    
    def test_validate_invalid_base_score(self, client):
        """测试验证无效的 base_score"""
        result = {
            "veto_check": {"triggered": False, "reason": ""},
            "score_details": [],
            "base_score": 150,  # 超过 100
            "grade_suggestion": "良好",
            "summary": "评价"
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            client._validate_scoring_result(result)
        
        assert "0-100" in str(exc_info.value)
        
        client.close()
    
    def test_validate_invalid_veto_check(self, client):
        """测试验证无效的 veto_check"""
        result = {
            "veto_check": "invalid",  # 应该是字典
            "score_details": [],
            "base_score": 85,
            "grade_suggestion": "良好",
            "summary": "评价"
        }
        
        with pytest.raises(APIResponseError) as exc_info:
            client._validate_scoring_result(result)
        
        assert "字典" in str(exc_info.value)
        
        client.close()


class TestDeepseekAPIClientErrorHandling:
    """Deepseek API 客户端错误处理测试"""
    
    @pytest.fixture
    def client(self):
        """创建客户端实例"""
        return DeepseekAPIClient(api_key="test-key", max_retries=2, timeout=5)
    
    @patch('services.deepseek_client.requests.Session.post')
    def test_api_call_timeout(self, mock_post, client):
        """测试 API 调用超时"""
        mock_post.side_effect = Timeout("Connection timeout")
        
        with pytest.raises(APITimeoutError) as exc_info:
            client.call_api("test prompt")
        
        assert "超时" in str(exc_info.value)
        assert mock_post.call_count >= 1  # 至少调用一次
        
        client.close()
    
    @patch('services.deepseek_client.requests.Session.post')
    def test_api_call_connection_error(self, mock_post, client):
        """测试 API 调用连接错误"""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(APICallError) as exc_info:
            client.call_api("test prompt")
        
        assert "失败" in str(exc_info.value)
        
        client.close()
    
    @patch('services.deepseek_client.requests.Session.post')
    def test_api_call_http_error(self, mock_post, client):
        """测试 API 调用 HTTP 错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        with pytest.raises(APICallError) as exc_info:
            client.call_api("test prompt")
        
        assert "401" in str(exc_info.value)
        
        client.close()
    
    @patch('services.deepseek_client.requests.Session.post')
    def test_api_call_success(self, mock_post, client):
        """测试 API 调用成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "veto_check": {"triggered": False, "reason": ""},
                            "score_details": [],
                            "base_score": 85,
                            "grade_suggestion": "良好",
                            "summary": "评价"
                        })
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = client.call_api("test prompt")
        
        assert result["base_score"] == 85
        assert result["grade_suggestion"] == "良好"
        
        client.close()


class TestDeepseekAPIClientGlobalFunctions:
    """Deepseek API 客户端全局函数测试"""
    
    def test_init_and_get_client(self):
        """测试初始化和获取全局客户端"""
        # 清理之前的实例
        close_deepseek_client()
        
        # 初始化客户端
        client = init_deepseek_client(api_key="test-key")
        
        assert client is not None
        assert client.api_key == "test-key"
        
        # 获取客户端
        retrieved_client = get_deepseek_client()
        
        assert retrieved_client is client
        
        # 关闭客户端
        close_deepseek_client()
        
        assert get_deepseek_client() is None
    
    def test_get_client_before_init(self):
        """测试在初始化前获取客户端"""
        close_deepseek_client()
        
        client = get_deepseek_client()
        
        assert client is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
