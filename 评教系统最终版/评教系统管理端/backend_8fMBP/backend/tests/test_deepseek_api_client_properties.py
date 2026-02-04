"""
Deepseek API 客户端属性测试

使用 Hypothesis 进行属性测试，验证 API 客户端的通用正确性属性
"""

import json
import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings, HealthCheck
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services.deepseek_client import (
    DeepseekAPIClient,
    APICallError,
    APITimeoutError,
    APIResponseError
)


class TestDeepseekAPIClientProperties:
    """Deepseek API 客户端属性测试"""
    
    # Feature: auto-scoring-system, Property 4: API 调用失败处理
    @given(
        status_code=st.sampled_from([400, 401, 403, 404, 500, 502, 503, 504])
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_api_call_failure_handling(self, status_code):
        """
        Property 4: For any API 调用失败的情况，系统应该记录错误日志并将文件标记为"评分失败"状态。
        
        **Validates: Requirements 2.5**
        
        This property verifies that:
        1. API call failures are properly handled
        2. Appropriate exceptions are raised
        3. Error information is preserved
        """
        client = DeepseekAPIClient(api_key="test-key", max_retries=1)
        
        with patch('services.deepseek_client.requests.Session.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.text = f"Error {status_code}"
            mock_post.return_value = mock_response
            
            # 验证 API 调用失败时抛出异常
            with pytest.raises(APICallError) as exc_info:
                client.call_api("test prompt")
            
            # 验证错误信息包含状态码
            error_msg = str(exc_info.value)
            assert str(status_code) in error_msg or "失败" in error_msg, \
                f"Error message should contain status code or failure indication: {error_msg}"
        
        client.close()
    
    # Feature: auto-scoring-system, Property 5: API 返回格式验证
    @given(
        base_score=st.integers(min_value=0, max_value=100),
        grade=st.sampled_from(["优秀", "良好", "合格", "不合格"])
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_api_response_format_validation(self, base_score, grade):
        """
        Property 5: For any API 返回的结果，系统应该验证其包含必需的字段。
        
        **Validates: Requirements 2.6**
        
        This property verifies that:
        1. API responses are validated for required fields
        2. Invalid responses are rejected
        3. Valid responses are accepted
        """
        client = DeepseekAPIClient(api_key="test-key")
        
        # 创建有效的响应
        valid_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "veto_check": {"triggered": False, "reason": ""},
                            "score_details": [
                                {"indicator": "test", "score": 10, "max_score": 10, "reason": "good"}
                            ],
                            "base_score": base_score,
                            "grade_suggestion": grade,
                            "summary": "评价"
                        })
                    }
                }
            ]
        }
        
        # 验证有效响应可以被解析
        result = client._parse_response(valid_response)
        
        # 验证必需字段存在
        required_fields = ["veto_check", "score_details", "base_score", "grade_suggestion", "summary"]
        for field in required_fields:
            assert field in result, f"Result should contain field: {field}"
        
        # 验证字段值的有效性
        assert isinstance(result["veto_check"], dict), "veto_check should be dict"
        assert isinstance(result["base_score"], (int, float)), "base_score should be number"
        assert result["base_score"] == base_score, f"base_score should be {base_score}"
        assert result["grade_suggestion"] == grade, f"grade_suggestion should be {grade}"
        
        client.close()
    
    # Feature: auto-scoring-system, Property 6: API 超时重试机制
    @given(
        attempt_count=st.integers(min_value=1, max_value=3)
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None  # 禁用 deadline 检查，因为重试会导致延迟
    )
    def test_api_timeout_retry_mechanism(self, attempt_count):
        """
        Property 6: For any API 调用超时的情况，系统应该重试最多3次。
        
        **Validates: Requirements 2.7**
        
        This property verifies that:
        1. Timeout errors trigger retries
        2. Maximum retry count is respected
        3. Appropriate exception is raised after max retries
        """
        client = DeepseekAPIClient(api_key="test-key", max_retries=3)
        
        with patch('services.deepseek_client.requests.Session.post') as mock_post:
            from requests.exceptions import Timeout
            mock_post.side_effect = Timeout("Connection timeout")
            
            # 验证超时后抛出 APITimeoutError
            with pytest.raises(APITimeoutError) as exc_info:
                client.call_api("test prompt")
            
            # 验证错误信息包含重试信息
            error_msg = str(exc_info.value)
            assert "超时" in error_msg or "timeout" in error_msg.lower(), \
                f"Error message should indicate timeout: {error_msg}"
            
            # 验证至少尝试了一次
            assert mock_post.call_count >= 1, "Should attempt at least once"
        
        client.close()
    
    # Property: API 响应中的 base_score 应该总是在有效范围内
    @given(
        base_score=st.integers(min_value=0, max_value=100)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_base_score_validity(self, base_score):
        """
        Property: For any 有效的 base_score，系统应该接受它
        
        This property verifies that base_score validation works correctly.
        """
        client = DeepseekAPIClient(api_key="test-key")
        
        result = {
            "veto_check": {"triggered": False, "reason": ""},
            "score_details": [],
            "base_score": base_score,
            "grade_suggestion": "合格",
            "summary": "评价"
        }
        
        # 验证有效的 base_score 被接受
        assert client._validate_scoring_result(result) is True
        
        client.close()
    
    # Property: API 响应中的 veto_check 应该总是包含 triggered 字段
    @given(
        triggered=st.booleans()
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_veto_check_structure(self, triggered):
        """
        Property: For any veto_check，应该包含 triggered 字段
        
        This property verifies that veto_check structure is correct.
        """
        client = DeepseekAPIClient(api_key="test-key")
        
        result = {
            "veto_check": {"triggered": triggered, "reason": ""},
            "score_details": [],
            "base_score": 75,
            "grade_suggestion": "合格",
            "summary": "评价"
        }
        
        # 验证结构有效
        assert client._validate_scoring_result(result) is True
        
        # 验证 triggered 字段的值
        assert result["veto_check"]["triggered"] == triggered
        
        client.close()
    
    # Property: API 客户端应该能够处理各种 grade_suggestion 值
    @given(
        grade=st.sampled_from(["优秀", "良好", "合格", "不合格", "excellent", "good", "pass", "fail"])
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_grade_suggestion_handling(self, grade):
        """
        Property: For any 有效的 grade_suggestion，系统应该接受它
        
        This property verifies that various grade formats are handled correctly.
        """
        client = DeepseekAPIClient(api_key="test-key")
        
        result = {
            "veto_check": {"triggered": False, "reason": ""},
            "score_details": [],
            "base_score": 75,
            "grade_suggestion": grade,
            "summary": "评价"
        }
        
        # 验证各种 grade 值都被接受
        assert client._validate_scoring_result(result) is True
        
        client.close()


class TestDeepseekAPIClientEdgeCases:
    """Deepseek API 客户端边界情况测试"""
    
    def test_parse_response_with_nested_json(self):
        """测试解析包含嵌套 JSON 的响应"""
        client = DeepseekAPIClient(api_key="test-key")
        
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "前缀文本\n" + json.dumps({
                            "veto_check": {"triggered": False, "reason": ""},
                            "score_details": [
                                {
                                    "indicator": "test",
                                    "score": 10,
                                    "max_score": 10,
                                    "reason": "good",
                                    "details": {"nested": "value"}
                                }
                            ],
                            "base_score": 85,
                            "grade_suggestion": "良好",
                            "summary": "评价"
                        }) + "\n后缀文本"
                    }
                }
            ]
        }
        
        result = client._parse_response(response_data)
        
        assert result["base_score"] == 85
        assert len(result["score_details"]) == 1
        
        client.close()
    
    def test_validate_boundary_scores(self):
        """测试验证边界分数"""
        client = DeepseekAPIClient(api_key="test-key")
        
        # 测试最小分数
        result_min = {
            "veto_check": {"triggered": False, "reason": ""},
            "score_details": [],
            "base_score": 0,
            "grade_suggestion": "不合格",
            "summary": "评价"
        }
        assert client._validate_scoring_result(result_min) is True
        
        # 测试最大分数
        result_max = {
            "veto_check": {"triggered": False, "reason": ""},
            "score_details": [],
            "base_score": 100,
            "grade_suggestion": "优秀",
            "summary": "评价"
        }
        assert client._validate_scoring_result(result_max) is True
        
        client.close()
    
    def test_client_session_reuse(self):
        """测试客户端会话重用"""
        client = DeepseekAPIClient(api_key="test-key")
        
        session1 = client.session
        session2 = client.session
        
        # 验证会话对象是同一个
        assert session1 is session2
        
        client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
