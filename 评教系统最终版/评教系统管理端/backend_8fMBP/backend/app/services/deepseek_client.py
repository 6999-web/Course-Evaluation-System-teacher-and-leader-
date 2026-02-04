"""
Deepseek API 客户端

负责与 Deepseek API 进行通信，实现自动评分功能
"""

import json
import logging
import time
from typing import Optional, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class DeepseekAPIError(Exception):
    """Deepseek API 错误基类"""
    pass


class APICallError(DeepseekAPIError):
    """API 调用错误"""
    pass


class APITimeoutError(DeepseekAPIError):
    """API 超时错误"""
    pass


class APIResponseError(DeepseekAPIError):
    """API 响应错误"""
    pass


class DeepseekAPIClient:
    """
    Deepseek API 客户端
    
    负责与 Deepseek API 进行通信，实现自动评分功能
    """
    
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.deepseek.com/v1/chat/completions",
        model: str = "deepseek-chat",
        temperature: float = 0.1,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        初始化 Deepseek API 客户端
        
        Args:
            api_key: API 密钥
            api_url: API 端点 URL
            model: 模型名称
            temperature: 温度参数（控制随机性）
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        
        # 创建会话并配置重试策略
        self.session = self._create_session()
        
        logger.info(f"Deepseek API 客户端初始化成功: {api_url}, 模型: {model}")
    
    def _create_session(self) -> requests.Session:
        """
        创建带有重试策略的 requests 会话
        
        Returns:
            requests.Session: 配置好的会话对象
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def call_api(self, prompt: str) -> Dict:
        """
        调用 Deepseek API 进行评分
        
        Args:
            prompt: 提示词
        
        Returns:
            dict: API 返回的评分结果
        
        Raises:
            APICallError: API 调用失败
            APITimeoutError: API 调用超时
            APIResponseError: API 响应格式错误
        """
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
        
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                logger.debug(f"调用 Deepseek API，尝试 {attempt + 1}/{self.max_retries}")
                
                response = self.session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                # 检查响应状态码
                if response.status_code != 200:
                    error_msg = f"API 返回错误状态码: {response.status_code}"
                    logger.warning(f"{error_msg}, 响应: {response.text}")
                    
                    if response.status_code >= 500:
                        # 服务器错误，可以重试
                        attempt += 1
                        if attempt < self.max_retries:
                            wait_time = 2 ** attempt  # 指数退避
                            logger.info(f"等待 {wait_time} 秒后重试...")
                            time.sleep(wait_time)
                            continue
                    
                    raise APICallError(error_msg)
                
                # 解析响应
                result = self._parse_response(response.json())
                
                logger.info(f"API 调用成功，返回结果长度: {len(str(result))}")
                return result
                
            except requests.Timeout as e:
                last_error = e
                attempt += 1
                logger.warning(f"API 调用超时，尝试 {attempt}/{self.max_retries}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise APITimeoutError(f"API 调用超时，已重试 {self.max_retries} 次")
                    
            except requests.RequestException as e:
                last_error = e
                attempt += 1
                logger.error(f"API 调用失败: {str(e)}")
                
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise APICallError(f"API 调用失败: {str(e)}")
                    
            except (APIResponseError, json.JSONDecodeError) as e:
                # 响应格式错误，不重试
                logger.error(f"API 响应格式错误: {str(e)}")
                raise
        
        # 如果所有重试都失败
        if last_error:
            raise APICallError(f"API 调用失败，已重试 {self.max_retries} 次: {str(last_error)}")
    
    def _parse_response(self, response_data: Dict) -> Dict:
        """
        解析 API 响应
        
        Args:
            response_data: API 返回的原始数据
        
        Returns:
            dict: 解析后的评分结果
        
        Raises:
            APIResponseError: 响应格式错误
        """
        try:
            # 检查必需的字段
            if "choices" not in response_data or len(response_data["choices"]) == 0:
                raise APIResponseError("API 响应缺少 choices 字段")
            
            # 提取消息内容
            message = response_data["choices"][0].get("message", {})
            content = message.get("content", "")
            
            if not content:
                raise APIResponseError("API 响应消息为空")
            
            # 尝试解析 JSON 格式的评分结果
            try:
                # 查找 JSON 内容（可能被包含在其他文本中）
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    scoring_result = json.loads(json_str)
                else:
                    raise json.JSONDecodeError("未找到 JSON 内容", content, 0)
                
            except json.JSONDecodeError as e:
                logger.error(f"无法解析 API 返回的 JSON: {str(e)}")
                logger.debug(f"原始内容: {content}")
                raise APIResponseError(f"API 返回的内容不是有效的 JSON: {str(e)}")
            
            # 验证评分结果的必需字段
            self._validate_scoring_result(scoring_result)
            
            logger.debug(f"API 响应解析成功: {scoring_result}")
            return scoring_result
            
        except APIResponseError:
            raise
        except Exception as e:
            logger.error(f"解析 API 响应失败: {str(e)}")
            raise APIResponseError(f"解析 API 响应失败: {str(e)}")
    
    def _validate_scoring_result(self, result: Dict) -> bool:
        """
        验证评分结果的格式
        
        Args:
            result: 评分结果
        
        Returns:
            bool: 是否有效
        
        Raises:
            APIResponseError: 格式无效
        """
        required_fields = [
            "veto_check",
            "score_details",
            "base_score",
            "grade_suggestion",
            "summary"
        ]
        
        for field in required_fields:
            if field not in result:
                raise APIResponseError(f"评分结果缺少必需字段: {field}")
        
        # 验证 veto_check 字段
        veto_check = result.get("veto_check", {})
        if not isinstance(veto_check, dict):
            raise APIResponseError("veto_check 必须是字典类型")
        
        if "triggered" not in veto_check:
            raise APIResponseError("veto_check 缺少 triggered 字段")
        
        # 验证 base_score 字段
        base_score = result.get("base_score")
        if not isinstance(base_score, (int, float)):
            raise APIResponseError("base_score 必须是数字类型")
        
        if base_score < 0 or base_score > 100:
            raise APIResponseError(f"base_score 必须在 0-100 之间，当前值: {base_score}")
        
        # 验证 grade_suggestion 字段
        grade_suggestion = result.get("grade_suggestion", "")
        valid_grades = ["优秀", "良好", "合格", "不合格", "excellent", "good", "pass", "fail"]
        if grade_suggestion not in valid_grades:
            logger.warning(f"grade_suggestion 值不在预期范围内: {grade_suggestion}")
        
        return True
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
            logger.info("Deepseek API 客户端会话已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 创建全局客户端实例（需要在应用启动时初始化）
_client_instance: Optional[DeepseekAPIClient] = None


def init_deepseek_client(
    api_key: str,
    api_url: str = "https://api.deepseek.com/v1/chat/completions",
    model: str = "deepseek-chat",
    temperature: float = 0.1,
    max_retries: int = 3,
    timeout: int = 30
) -> DeepseekAPIClient:
    """
    初始化全局 Deepseek API 客户端
    
    Args:
        api_key: API 密钥
        api_url: API 端点 URL
        model: 模型名称
        temperature: 温度参数
        max_retries: 最大重试次数
        timeout: 超时时间
    
    Returns:
        DeepseekAPIClient: 初始化的客户端实例
    """
    global _client_instance
    
    _client_instance = DeepseekAPIClient(
        api_key=api_key,
        api_url=api_url,
        model=model,
        temperature=temperature,
        max_retries=max_retries,
        timeout=timeout
    )
    
    return _client_instance


def get_deepseek_client() -> Optional[DeepseekAPIClient]:
    """
    获取全局 Deepseek API 客户端实例
    
    Returns:
        DeepseekAPIClient: 客户端实例，如果未初始化则返回 None
    """
    return _client_instance


def close_deepseek_client():
    """关闭全局 Deepseek API 客户端"""
    global _client_instance
    
    if _client_instance:
        _client_instance.close()
        _client_instance = None
