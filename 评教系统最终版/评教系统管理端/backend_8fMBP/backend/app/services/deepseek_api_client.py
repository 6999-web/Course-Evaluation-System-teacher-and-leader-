"""
Deepseek API 客户端

负责与 Deepseek API 进行交互，实现自动评分功能。
包含重试机制、超时处理、响应格式验证等功能。
"""

import json
import logging
import time
from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class DeepseekAPIError(Exception):
    """Deepseek API 基础异常类"""
    pass


class AuthenticationError(DeepseekAPIError):
    """API 认证失败异常"""
    pass


class APITimeoutError(DeepseekAPIError):
    """API 超时异常"""
    pass


class APICallError(DeepseekAPIError):
    """API 调用失败异常"""
    pass


class ValidationError(DeepseekAPIError):
    """响应格式验证异常"""
    pass


class DeepseekAPIClient:
    """
    Deepseek API 客户端
    
    负责调用 Deepseek API 进行文本评分，包含完整的错误处理和重试机制。
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
        初始化 API 客户端
        
        Args:
            api_key: API 密钥
            api_url: API 地址
            model: 使用的模型名称
            temperature: 温度参数，控制随机性
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        
        # 配置 requests 会话
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        logger.info(f"Deepseek API 客户端初始化完成: {self.api_url}")
    
    def call_api(self, prompt: str) -> Dict:
        """
        调用 Deepseek API 进行评分
        
        Args:
            prompt: 评分提示词
        
        Returns:
            dict: API 返回的评分结果
        
        Raises:
            AuthenticationError: 认证失败
            APITimeoutError: 超时
            APICallError: 调用失败
            ValidationError: 响应格式验证失败
        """
        if not prompt or prompt.strip() == "":
            raise ValueError("提示词不能为空")
        
        request_data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": 2000,
            "stream": False
        }
        
        logger.info(f"开始调用 Deepseek API, 提示词长度: {len(prompt)}")
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                response = self.session.post(
                    self.api_url,
                    json=request_data,
                    timeout=self.timeout
                )
                
                elapsed_time = time.time() - start_time
                logger.info(f"API 调用完成, 耗时: {elapsed_time:.2f}秒, 状态码: {response.status_code}")
                
                # 检查 HTTP 状态码
                if response.status_code == 401:
                    raise AuthenticationError("API 密钥无效或已过期")
                elif response.status_code == 429:
                    logger.warning(f"API 调用频率限制, 尝试 {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    else:
                        raise APICallError("API 调用频率限制，已达到最大重试次数")
                elif response.status_code >= 500:
                    logger.warning(f"服务器错误 {response.status_code}, 尝试 {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    else:
                        raise APICallError(f"服务器错误: {response.status_code}")
                
                response.raise_for_status()
                
                # 解析响应
                response_data = response.json()
                
                # 提取评分结果
                scoring_result = self._extract_scoring_result(response_data)
                
                # 验证响应格式
                self._validate_api_response(scoring_result)
                
                logger.info("API 调用成功，响应格式验证通过")
                return scoring_result
                
            except requests.Timeout:
                logger.warning(f"API 超时, 尝试 {attempt + 1}/{self.max_retries}")
                if attempt == self.max_retries - 1:
                    raise APITimeoutError(f"API 调用超时，已重试 {self.max_retries} 次")
                time.sleep(1)  # 短暂等待后重试
                
            except requests.RequestException as e:
                logger.error(f"API 请求异常: {str(e)}, 尝试 {attempt + 1}/{self.max_retries}")
                if attempt == self.max_retries - 1:
                    raise APICallError(f"API 调用失败: {str(e)}")
                time.sleep(1)  # 短暂等待后重试
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"响应解析失败: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise ValidationError(f"API 响应格式错误: {str(e)}")
                time.sleep(1)  # 短暂等待后重试
        
        # 如果所有重试都失败了
        raise APICallError(f"API 调用失败，已重试 {self.max_retries} 次")
    
    def _extract_scoring_result(self, response_data: Dict) -> Dict:
        """
        从 API 响应中提取评分结果
        
        Args:
            response_data: API 原始响应数据
        
        Returns:
            dict: 提取的评分结果
        
        Raises:
            ValidationError: 响应格式错误
        """
        try:
            # 检查响应结构
            if "choices" not in response_data:
                raise ValidationError("API 响应缺少 choices 字段")
            
            choices = response_data["choices"]
            if not choices or len(choices) == 0:
                raise ValidationError("API 响应 choices 为空")
            
            # 获取第一个选择的内容
            first_choice = choices[0]
            if "message" not in first_choice:
                raise ValidationError("API 响应缺少 message 字段")
            
            message = first_choice["message"]
            if "content" not in message:
                raise ValidationError("API 响应缺少 content 字段")
            
            content = message["content"].strip()
            if not content:
                raise ValidationError("API 响应内容为空")
            
            logger.debug(f"API 响应内容: {content[:200]}...")
            
            # 尝试解析 JSON 格式的评分结果
            try:
                # 查找 JSON 内容（可能包含在代码块中）
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start == -1 or json_end == 0:
                    raise ValidationError("API 响应中未找到 JSON 格式的评分结果")
                
                json_content = content[json_start:json_end]
                scoring_result = json.loads(json_content)
                
                return scoring_result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {str(e)}")
                logger.error(f"原始内容: {content}")
                raise ValidationError(f"API 响应 JSON 格式错误: {str(e)}")
        
        except Exception as e:
            logger.error(f"提取评分结果失败: {str(e)}")
            raise ValidationError(f"提取评分结果失败: {str(e)}")
    
    def _validate_api_response(self, response: Dict) -> bool:
        """
        验证 API 返回格式的完整性
        
        Args:
            response: API 返回的评分结果
        
        Returns:
            bool: 是否有效
        
        Raises:
            ValidationError: 如果响应格式不完整
        """
        required_fields = [
            "veto_check",
            "score_details", 
            "base_score",
            "grade_suggestion",
            "summary"
        ]
        
        # 检查必需字段
        for field in required_fields:
            if field not in response:
                raise ValidationError(f"API 返回缺少必需字段: {field}")
        
        # 验证 veto_check 结构
        veto_check = response.get("veto_check", {})
        if not isinstance(veto_check, dict):
            raise ValidationError("veto_check 必须是字典类型")
        
        if "triggered" not in veto_check:
            raise ValidationError("veto_check 缺少 triggered 字段")
        
        if not isinstance(veto_check["triggered"], bool):
            raise ValidationError("veto_check.triggered 必须是布尔类型")
        
        # 验证 score_details 结构
        score_details = response.get("score_details", [])
        if not isinstance(score_details, list):
            raise ValidationError("score_details 必须是列表类型")
        
        for detail in score_details:
            if not isinstance(detail, dict):
                raise ValidationError("score_details 中的每项必须是字典类型")
            
            required_detail_fields = ["indicator", "score", "max_score", "reason"]
            for field in required_detail_fields:
                if field not in detail:
                    raise ValidationError(f"score_details 缺少字段: {field}")
        
        # 验证分数范围
        base_score = response.get("base_score")
        if not isinstance(base_score, (int, float)):
            raise ValidationError("base_score 必须是数字类型")
        
        if not 0 <= base_score <= 100:
            raise ValidationError(f"base_score 超出范围 [0, 100]: {base_score}")
        
        # 验证等级
        grade_suggestion = response.get("grade_suggestion", "")
        valid_grades = ["优秀", "良好", "合格", "不合格"]
        if grade_suggestion not in valid_grades:
            raise ValidationError(f"无效的等级: {grade_suggestion}")
        
        # 验证总结
        summary = response.get("summary", "")
        if not isinstance(summary, str) or len(summary.strip()) == 0:
            raise ValidationError("summary 必须是非空字符串")
        
        logger.debug("API 响应格式验证通过")
        return True
    
    def parse_api_response(self, response: Dict) -> Dict:
        """
        解析 API 返回结果，提取关键信息
        
        Args:
            response: API 返回的原始结果
        
        Returns:
            dict: 解析后的评分信息
        """
        try:
            # 先验证响应格式
            self._validate_api_response(response)
            
            # 提取关键信息
            parsed_result = {
                "veto_triggered": response["veto_check"]["triggered"],
                "veto_reason": response["veto_check"].get("reason", ""),
                "base_score": float(response["base_score"]),
                "grade": response["grade_suggestion"],
                "summary": response["summary"],
                "score_details": response["score_details"]
            }
            
            # 如果触发否决项，设置分数为0
            if parsed_result["veto_triggered"]:
                parsed_result["base_score"] = 0.0
                parsed_result["grade"] = "不合格"
            
            logger.info(f"API 响应解析完成: 基础分={parsed_result['base_score']}, 等级={parsed_result['grade']}")
            return parsed_result
            
        except Exception as e:
            logger.error(f"解析 API 响应失败: {str(e)}")
            raise ValidationError(f"解析 API 响应失败: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        测试 API 连接
        
        Returns:
            bool: 连接是否正常
        """
        try:
            test_prompt = "请回复：连接测试成功"
            
            response = self.call_api(test_prompt)
            logger.info("API 连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"API 连接测试失败: {str(e)}")
            return False
    
    def get_api_info(self) -> Dict:
        """
        获取 API 客户端配置信息
        
        Returns:
            dict: 配置信息
        """
        return {
            "api_url": self.api_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "api_key_masked": f"{self.api_key[:8]}...{self.api_key[-4:]}" if self.api_key else "未设置"
        }


# 便利函数
def create_deepseek_client(
    api_key: Optional[str] = None,
    **kwargs
) -> DeepseekAPIClient:
    """
    创建 Deepseek API 客户端的便利函数
    
    Args:
        api_key: API 密钥，如果不提供则使用默认值
        **kwargs: 其他配置参数
    
    Returns:
        DeepseekAPIClient: 配置好的客户端实例
    """
    # 使用默认 API 密钥（从需求文档中获取）
    if api_key is None:
        api_key = "sk-b6ca926900534f1fa31067d49980ec56"
    
    return DeepseekAPIClient(api_key=api_key, **kwargs)


def validate_scoring_result(result: Dict) -> bool:
    """
    验证评分结果的完整性
    
    Args:
        result: 评分结果
    
    Returns:
        bool: 是否有效
    
    Raises:
        ValidationError: 如果结果格式不正确
    """
    required_fields = [
        "veto_triggered",
        "base_score",
        "grade",
        "summary",
        "score_details"
    ]
    
    for field in required_fields:
        if field not in result:
            raise ValidationError(f"评分结果缺少必需字段: {field}")
    
    # 验证分数和等级的一致性
    base_score = result["base_score"]
    grade = result["grade"]
    
    if result["veto_triggered"]:
        if base_score != 0 or grade != "不合格":
            raise ValidationError("触发否决项时，分数应为0，等级应为不合格")
    else:
        # 验证分数与等级的对应关系
        if base_score >= 90 and grade != "优秀":
            raise ValidationError(f"分数 {base_score} 应对应优秀等级，实际为 {grade}")
        elif 80 <= base_score < 90 and grade != "良好":
            raise ValidationError(f"分数 {base_score} 应对应良好等级，实际为 {grade}")
        elif 60 <= base_score < 80 and grade != "合格":
            raise ValidationError(f"分数 {base_score} 应对应合格等级，实际为 {grade}")
        elif base_score < 60 and grade != "不合格":
            raise ValidationError(f"分数 {base_score} 应对应不合格等级，实际为 {grade}")
    
    return True