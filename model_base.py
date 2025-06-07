"""
模型客户端基类，为不同的大模型客户端提供通用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ModelBase(ABC):
    """大模型调用基类，定义通用接口"""
    
    def __init__(self, api_key: str = None):
        """
        初始化模型客户端
        
        Args:
            api_key: API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成文本
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        pass
    
    @abstractmethod
    async def generate_outline(self, requirement: str) -> Dict[str, Any]:
        """
        根据需求生成系统架构大纲
        
        Args:
            requirement: 需求内容
            
        Returns:
            Dict[str, Any]: 生成的大纲和解析结果
        """
        pass 