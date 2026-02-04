"""
DeepSeek API 客户端
用于调用 DeepSeek API 进行自动评分
"""

import requests
import json
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DeepseekAPIClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.deepseek.com/v1/chat/completions"):
        """
        初始化 DeepSeek API 客户端
        
        Args:
            api_key: API 密钥
            api_url: API 地址
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = "deepseek-chat"
        self.temperature = 0.1
        self.max_retries = 3
        self.timeout = 30
    
    def call_api(self, prompt: str, max_retries: Optional[int] = None) -> Dict:
        """
        调用 DeepSeek API
        
        Args:
            prompt: 提示词
            max_retries: 最大重试次数
            
        Returns:
            API 返回结果
            
        Raises:
            Exception: API 调用失败
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": 2000
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"调用 DeepSeek API (尝试 {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                # 检查响应状态
                if response.status_code != 200:
                    error_msg = f"API 返回错误: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    last_error = error_msg
                    
                    # 如果是认证错误，不重试
                    if response.status_code == 401:
                        raise Exception(f"API 认证失败: {error_msg}")
                    
                    # 其他错误重试
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 指数退避
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(error_msg)
                
                # 解析响应
                result = response.json()
                
                # 验证响应格式
                if "choices" not in result or not result["choices"]:
                    raise Exception("API 返回格式错误: 缺少 choices 字段")
                
                # 提取内容
                content = result["choices"][0].get("message", {}).get("content", "")
                if not content:
                    raise Exception("API 返回内容为空")
                
                logger.info("API 调用成功")
                return {
                    "success": True,
                    "content": content,
                    "usage": result.get("usage", {})
                }
                
            except requests.exceptions.Timeout:
                error_msg = f"API 调用超时 (超过 {self.timeout} 秒)"
                logger.warning(error_msg)
                last_error = error_msg
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(error_msg)
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"网络连接失败: {str(e)}"
                logger.warning(error_msg)
                last_error = error_msg
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(error_msg)
                    
            except Exception as e:
                error_msg = f"API 调用异常: {str(e)}"
                logger.error(error_msg)
                last_error = error_msg
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        # 所有重试都失败
        raise Exception(f"API 调用失败 (已重试 {max_retries} 次): {last_error}")
    
    def parse_response(self, response_text: str) -> Dict:
        """
        解析 API 返回的评分结果
        
        Args:
            response_text: API 返回的文本内容
            
        Returns:
            解析后的评分结果
            
        Raises:
            Exception: 解析失败
        """
        try:
            # 尝试从响应中提取 JSON
            # API 可能返回 markdown 格式的 JSON，需要提取
            
            # 首先尝试直接解析
            try:
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                pass
            
            # 尝试从 markdown 代码块中提取
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end > start:
                    json_str = response_text[start:end].strip()
                    result = json.loads(json_str)
                    return result
            
            # 尝试从 ``` 代码块中提取
            if "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                if end > start:
                    json_str = response_text[start:end].strip()
                    result = json.loads(json_str)
                    return result
            
            # 如果都失败，抛出异常
            raise Exception(f"无法从响应中提取 JSON: {response_text[:200]}")
            
        except json.JSONDecodeError as e:
            raise Exception(f"JSON 解析失败: {str(e)}")
        except Exception as e:
            raise Exception(f"响应解析失败: {str(e)}")
    
    def validate_response(self, parsed_response: Dict) -> bool:
        """
        验证解析后的响应格式
        
        Args:
            parsed_response: 解析后的响应
            
        Returns:
            是否有效
            
        Raises:
            Exception: 验证失败
        """
        required_fields = ["veto_check", "score_details", "base_score", "grade_suggestion", "summary"]
        
        for field in required_fields:
            if field not in parsed_response:
                raise Exception(f"响应缺少必需字段: {field}")
        
        # 验证 veto_check 结构
        veto_check = parsed_response.get("veto_check", {})
        if "triggered" not in veto_check or "reason" not in veto_check:
            raise Exception("veto_check 字段格式错误")
        
        # 验证 score_details 是列表
        score_details = parsed_response.get("score_details", [])
        if not isinstance(score_details, list):
            raise Exception("score_details 应该是列表")
        
        # 验证 base_score 是数字
        base_score = parsed_response.get("base_score")
        if not isinstance(base_score, (int, float)):
            raise Exception("base_score 应该是数字")
        
        return True
