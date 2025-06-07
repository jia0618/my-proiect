"""
DeepSeek模型客户端，负责调用DeepSeek API
"""
import json
import aiohttp
from typing import Dict, Any, Optional
import os

from model_base import ModelBase
from api_config import get_api_config, get_available_models

class DeepSeekClient(ModelBase):
    """DeepSeek模型客户端类"""
    
    def __init__(self, api_key: str = None):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥，如果为None则从配置获取
        """
        # 如果未提供API密钥，从配置获取
        if not api_key:
            config = get_api_config()
            api_key = config.get("deepseek_api_key")
        
        super().__init__(api_key)
        self.model = get_available_models().get("deepseek", "deepseek-chat")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成文本
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 默认参数
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4000)
        }
        
        # 合并其他参数
        for key, value in kwargs.items():
            if key not in ["temperature", "max_tokens"]:
                data[key] = value
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"error": f"API调用失败: {response.status} - {error_text}"}
                    
                    result = await response.json()
                    return {
                        "text": result["choices"][0]["message"]["content"],
                        "raw_response": result
                    }
        except Exception as e:
            return {"error": f"API调用异常: {str(e)}"}
    
    async def generate_outline(self, requirement: str) -> Dict[str, Any]:
        """
        根据需求生成系统架构大纲
        
        Args:
            requirement: 需求内容
            
        Returns:
            Dict[str, Any]: 生成的大纲和解析结果
        """
        prompt = f"""
请分析以下软件需求，生成系统架构大纲。大纲应包括：
1. 系统架构类型（如MVC、微服务等）
2. 核心模块及功能
3. 数据模型
4. API接口
5. 部署架构

请以JSON格式输出，确保格式正确可解析。

需求文档：
{requirement}
"""
        
        result = await self.generate_text(prompt, temperature=0.3)
        
        if "error" in result:
            return {"error": result["error"]}
        
        # 尝试从结果中解析JSON
        try:
            # 提取可能的JSON部分
            text = result["text"]
            json_start = text.find("{")
            json_end = text.rfind("}")
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end+1]
                parsed_outline = json.loads(json_str)
                
                return {
                    "outline_text": text,
                    "parsed_outline": parsed_outline,
                    "raw_response": result.get("raw_response")
                }
            else:
                return {
                    "outline_text": text,
                    "error": "无法解析JSON格式的大纲",
                    "raw_response": result.get("raw_response")
                }
        except json.JSONDecodeError as e:
            return {
                "outline_text": result["text"],
                "error": f"JSON解析失败: {str(e)}",
                "raw_response": result.get("raw_response")
            }
            
    async def generate_code(self, requirement: str, outline: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据需求和大纲生成代码
        
        Args:
            requirement: 需求内容
            outline: 系统架构大纲
            
        Returns:
            Dict[str, Any]: 生成的代码和其他信息
        """
        prompt = f"""
请根据以下需求和系统架构大纲，生成相关的代码。代码应该完整、可执行，并符合最佳实践。

需求文档:
{requirement}

"""
        
        if outline:
            prompt += f"""
系统架构大纲:
{json.dumps(outline, ensure_ascii=False, indent=2)}
"""
        
        prompt += """
请生成以下部分的代码:
1. 核心模块
2. 数据访问层
3. 业务逻辑层
4. API接口

每个代码块请使用Markdown代码块格式，并在开始注明文件名。
"""
        
        result = await self.generate_text(prompt, temperature=0.2, max_tokens=8000)
        
        if "error" in result:
            return {"error": result["error"]}
        
        # 解析代码块
        text = result["text"]
        code_sections = {}
        
        # 简单的代码块提取
        import re
        code_blocks = re.findall(r'```\w*\s*(.+?)\s*\n([\s\S]+?)```', text)
        
        for filename, code in code_blocks:
            clean_filename = filename.strip()
            if clean_filename:
                code_sections[clean_filename] = code.strip()
            else:
                # 如果没有文件名，使用索引作为键
                code_sections[f"code_section_{len(code_sections)}"] = code.strip()
        
        return {
            "code_sections": code_sections,
            "full_text": text,
            "raw_response": result.get("raw_response")
        }
    
    async def generate_database_script(self, requirement: str) -> Dict[str, Any]:
        """
        根据需求生成数据库脚本
        
        Args:
            requirement: 需求内容
            
        Returns:
            Dict[str, Any]: 生成的数据库脚本
        """
        prompt = f"""
请根据以下需求生成完整的MySQL数据库创建脚本，包括表结构、关系、索引和初始数据。

需求文档:
{requirement}

请确保SQL脚本符合MySQL最佳实践，包含所有必要的表和字段，并使用合适的数据类型、约束和索引。
返回的脚本应该可以直接执行，不含任何语法错误。
"""
        
        result = await self.generate_text(prompt, temperature=0.2)
        
        if "error" in result:
            return {"error": result["error"]}
        
        # 提取SQL脚本
        text = result["text"]
        
        # 尝试提取SQL代码块
        import re
        sql_blocks = re.findall(r'```sql\s*([\s\S]+?)\s*```', text)
        
        if sql_blocks:
            # 合并所有SQL代码块
            sql_script = "\n\n".join(sql_blocks)
        else:
            # 如果没有明确的SQL代码块，尝试提取看起来像SQL的内容
            lines = text.split('\n')
            sql_lines = []
            in_sql_block = False
            
            for line in lines:
                if line.strip().startswith("CREATE") or line.strip().startswith("USE") or in_sql_block:
                    in_sql_block = True
                    sql_lines.append(line)
            
            sql_script = "\n".join(sql_lines) if sql_lines else text
        
        return {
            "sql_script": sql_script,
            "full_text": text,
            "raw_response": result.get("raw_response")
        } 