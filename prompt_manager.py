import json
from typing import Dict, Any, List, Optional

class PromptManager:
    """提示词管理类，负责生成和管理模型提示词"""
    
    def __init__(self):
        """初始化提示词管理器"""
        self.templates = {
            "outline": {
                "title": "软件系统大纲生成",
                "description": "生成软件系统开发大纲",
                "template": """
                请根据以下需求文档，生成一个详细的软件系统开发大纲，包括架构设计、模块划分、
                数据模型设计、API接口设计以及技术选型建议。大纲应该清晰、结构化，并符合软件工程最佳实践。

                需求文档:
                {{requirement}}
                
                请以JSON格式返回，包含以下部分：
                1. 系统架构
                2. 核心模块
                3. 数据模型
                4. API接口
                5. 技术栈建议
                """
            },
            "code": {
                "title": "代码生成",
                "description": "生成符合需求的代码",
                "template": """
                请根据以下需求文档和系统大纲，生成符合要求的Python代码。代码必须符合PEP 8规范，
                包含完整的类、函数定义和必要的注释。请使用现代Python特性，确保代码可读性和可维护性。
                
                需求文档:
                {{requirement}}
                
                系统大纲:
                {{outline}}
                
                您需要提供的代码包括：
                1. 核心模块实现
                2. 数据模型设计
                3. API接口实现
                4. 配置和工具函数
                
                请生成完整可运行的代码，确保各部分之间的一致性和兼容性。
                """
            },
            "database": {
                "title": "数据库脚本生成",
                "description": "生成MySQL数据库脚本",
                "template": """
                请根据以下需求文档，生成MySQL数据库的创建脚本。脚本应包含表结构定义、
                主键和外键约束、索引设计以及必要的初始数据。请确保符合MySQL最佳实践。
                
                需求文档:
                {{requirement}}
                
                生成的SQL脚本应包含：
                1. 数据库创建语句
                2. 表结构定义
                3. 约束和索引
                4. 初始数据插入语句
                """
            },
            "cursor": {
                "title": "Cursor提示词",
                "description": "生成引导Cursor的提示词",
                "template": """
                我需要你帮我完成以下任务：

                任务背景：
                {{requirement}}

                请根据以上背景，生成详细、精确的指令，引导AI完成代码编写任务。指令应该：
                1. 清晰描述需求和期望输出
                2. 提供必要的上下文和约束条件
                3. 按步骤组织，指导AI逐步完成任务
                4. 包含代码质量和风格的要求
                
                请在指令中包含：
                - 项目背景简介
                - 详细的功能需求列表
                - 技术栈和架构要求
                - 代码组织和结构说明
                - 关键功能的实现思路
                - 预期的输出和测试标准
                """
            }
        }
    
    def generate_prompt(self, template_name: str, params: Dict[str, Any]) -> str:
        """
        生成提示词
        
        Args:
            template_name: 模板名称
            params: 模板参数
            
        Returns:
            str: 生成的提示词
        """
        if template_name not in self.templates:
            raise ValueError(f"未找到模板: {template_name}")
        
        template = self.templates[template_name]["template"]
        
        # 替换模板中的变量
        #. 同时遍历键和值
        for key, value in params.items():
            #构造占位符
            placeholder = "{{" + key + "}}"
            # 如果值是字典或列表，转换为格式化的JSON字符串
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                value_str = str(value)
            #替换占位符
            template = template.replace(placeholder, value_str)
        #去除字符串首尾的空白字符，使最终返回的提示词更简洁、规范
        return template.strip()
    
    def generate_cursor_prompt(self, requirement: str, outline: Optional[Dict[str, Any]] = None) -> str:
        """
        生成引导Cursor的提示词
        
        Args:
            requirement: 需求文档
            outline: 系统大纲
            
        Returns:
            str: 生成的Cursor提示词
        """
        params = {"requirement": requirement}
        
        if outline:
            # 将大纲添加到提示词中
            outline_str = json.dumps(outline, ensure_ascii=False, indent=2)
            params["requirement"] += f"\n\n系统大纲:\n{outline_str}"
        
        return self.generate_prompt("cursor", params)
    
    def get_template_names(self) -> List[str]:
        """
        获取所有可用的模板名称
        
        Returns:
            List[str]: 模板名称列表
        """
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Dict[str, str]:
        """
        获取模板信息
        
        Args:
            template_name: 模板名称
            
        Returns:
            Dict[str, str]: 模板信息
        """
        if template_name not in self.templates:
            raise ValueError(f"未找到模板: {template_name}")
        
        return {
            "title": self.templates[template_name]["title"],
            "description": self.templates[template_name]["description"],
            "template": self.templates[template_name]["template"]
        }
    
    def add_template(self, name: str, title: str, description: str, template: str) -> None:
        """
        添加新模板
        
        Args:
            name: 模板名称
            title: 模板标题
            description: 模板描述
            template: 模板内容
        """
        self.templates[name] = {
            "title": title,
            "description": description,
            "template": template
        } 