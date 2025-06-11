"""
AI服务类，整合DeepSeekClient和TongyiClient，提供统一的AI服务接口
"""
import os
from typing import Dict, Any, Optional, List
import json

from deepseek_client import DeepSeekClient
from tongyi_client import TongyiClient
from api_config import get_api_config

class AIService:
    """AI服务类，提供大模型统一调用接口"""
    
    def __init__(self, deepseek_api_key: str = None, tongyi_api_key: str = None):
        """
        初始化AI服务
        
        Args:
            deepseek_api_key: DeepSeek API密钥，默认从配置获取
            tongyi_api_key: 通义千问API密钥，默认从配置获取
        """
        if not deepseek_api_key or not tongyi_api_key:
            config = get_api_config()
            deepseek_api_key = deepseek_api_key or config.get("deepseek_api_key")
            tongyi_api_key = tongyi_api_key or config.get("tongyi_api_key")
        #创建两个客户端实例
        self.deepseek_client = DeepSeekClient(api_key=deepseek_api_key)
        self.tongyi_client = TongyiClient(api_key=tongyi_api_key, use_openai_client=False)
    
    async def generate_system_outline(self, requirement: str) -> Dict[str, Any]:
        """
        生成系统架构大纲
        
        Args:
            requirement: 需求文档内容
            
        Returns:
            Dict[str, Any]: 大纲生成结果
        """
        # 使用通义千问进行大纲生成
        result = await self.tongyi_client.generate_outline(requirement)
        return result
    
    async def generate_code(self, requirement: str, outline: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成代码
        
        Args:
            requirement: 需求文档内容
            outline: 系统架构大纲
            
        Returns:
            Dict[str, Any]: 代码生成结果
        """
        # 使用DeepSeek进行代码生成
        result = await self.deepseek_client.generate_code(requirement, outline)
        return result
    
    async def generate_database_script(self, requirement: str) -> Dict[str, Any]:
        """
        生成数据库脚本
        
        Args:
            requirement: 需求文档内容
            
        Returns:
            Dict[str, Any]: 数据库脚本生成结果
        """
        # 使用DeepSeek生成数据库脚本
        result = await self.deepseek_client.generate_database_script(requirement)
        return result
    
    async def generate_test_cases(self, requirement: str, code_section: str = None) -> Dict[str, Any]:
        """
        生成测试用例
        
        Args:
            requirement: 需求文档内容
            code_section: 代码段（可选）
            
        Returns:
            Dict[str, Any]: 测试用例生成结果
        """
        #prompt = f"""是一个 f-string（格式化字符串）用于创建一个字符串变量 prompt
        prompt = f"""
请根据以下需求生成完整的测试用例，包括单元测试和集成测试。测试代码应完整、可执行。

需求文档:
{requirement}

"""
        # prompt += ... 是 Python 中的 字符串拼接操作，用于在原有提示词的基础上 追加额外内容
        if code_section:
            prompt += f"""
相关代码:
```
{code_section}
```
"""

        prompt += """
请生成测试用例，确保覆盖主要功能和边缘情况。使用pytest框架组织测试代码。
"""
        
        # 使用DeepSeek生成测试用例
        result = await self.deepseek_client.generate_text(prompt, temperature=0.3)
        
        if "error" in result:
            return {"error": result["error"]}
        
        return {
            "test_cases": result["text"],
            "raw_response": result.get("raw_response")
        }
    
    async def generate_deployment_guide(self, requirement: str, outline: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成部署指南
        
        Args:
            requirement: 需求文档内容
            outline: 系统架构大纲
            
        Returns:
            Dict[str, Any]: 部署指南生成结果
        """
        prompt = f"""
请根据以下需求和系统架构，生成详细的系统部署指南，包括环境配置、安装步骤、配置说明和启动命令。

需求文档:
{requirement}

"""
        
        if outline:
            prompt += f"""
系统架构:
{json.dumps(outline, ensure_ascii=False, indent=2)}
"""
        
        prompt += """
请提供以下内容:
1. 系统要求
2. 环境准备
3. 安装步骤
4. 配置说明
5. 启动和验证
6. 常见问题解决

请使用Markdown格式，确保指南清晰易懂，便于开发人员和运维人员使用。
"""
        
        # 使用DeepSeek生成部署指南
        result = await self.deepseek_client.generate_text(prompt, temperature=0.3)
        
        if "error" in result:
            return {"error": result["error"]}
        
        return {
            "deployment_guide": result["text"],
            "raw_response": result.get("raw_response")
        } 