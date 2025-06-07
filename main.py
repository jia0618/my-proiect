"""
AI软件管理平台主程序入口文件
"""
import os
import json
import asyncio
import argparse
from typing import Dict, Any, Optional
from datetime import datetime

from db_manager import DBManager
from ai_service import AIService

class AIModelPlatform:
    """AI软件管理平台主类"""
    
    def __init__(self, deepseek_api_key: str = None, tongyi_api_key: str = None,
                 db_host: str = None, db_user: str = None, db_password: str = None,
                 db_name: str = None, db_port: int = None):
        """
        初始化AI软件管理平台
        
        Args:
            deepseek_api_key: DeepSeek API密钥
            tongyi_api_key: 通义前问API密钥
            db_host: 数据库主机
            db_user: 数据库用户
            db_password: 数据库密码
            db_name: 数据库名
            db_port: 数据库端口
        """
        # 初始化AI服务
        self.ai_service = AIService(
            deepseek_api_key=deepseek_api_key,
            tongyi_api_key=tongyi_api_key
        )
        
        # 初始化数据库管理器
        self.db_manager = DBManager(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )
        
        # 确保必要的数据表存在
        try:
            self.db_manager.create_tables()
        except Exception as e:
            print(f"初始化数据库表失败: {str(e)}")
    
    async def process_requirement(self, project_name: str, requirement_path: str) -> Dict[str, Any]:
        """
        处理需求文档
        
        Args:
            project_name: 项目名称
            requirement_path: 需求文档路径
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            # 读取需求文档
            with open(requirement_path, "r", encoding="utf-8") as f:
                requirement_content = f.read()
            
            # 创建项目记录
            project_id = self.db_manager.save_project(project_name, "通过AI平台生成的项目")
            
            # 保存需求记录
            self.db_manager.save_requirement(project_id, requirement_content)
            
            # 生成系统大纲
            print("正在生成系统架构大纲...")
            outline_result = await self.ai_service.generate_system_outline(requirement_content)
            
            if "error" in outline_result:
                print(f"生成大纲失败: {outline_result['error']}")
                return {"project_id": project_id, "error": outline_result["error"]}
            
            parsed_outline = outline_result.get("parsed_outline")
            if parsed_outline:
                # 保存大纲
                self.db_manager.save_outline(project_id, parsed_outline)
            else:
                print("警告: 大纲解析失败，将使用空大纲继续")
                parsed_outline = {}
            
            # 生成数据库脚本
            print("正在生成数据库脚本...")
            db_script_result = await self.ai_service.generate_database_script(requirement_content)
            
            if "sql_script" in db_script_result:
                # 保存数据库脚本
                self.db_manager.save_db_script(project_id, db_script_result["sql_script"])
            
            # 生成代码
            print("正在生成代码...")
            code_result = await self.ai_service.generate_code(requirement_content, parsed_outline)
            
            if "code_sections" in code_result:
                # 保存代码段
                for name, content in code_result["code_sections"].items():
                    self.db_manager.save_code(project_id, name, content)
            
            # 返回处理结果
            return {
                "project_id": project_id,
                "outline": parsed_outline,
                "code_sections": code_result.get("code_sections", {}),
                "sql_script": db_script_result.get("sql_script", "")
            }
            
        except Exception as e:
            print(f"处理需求时出错: {str(e)}")
            return {"error": str(e)}
    
    def export_results(self, project_id: int, output_dir: str) -> None:
        """
        导出处理结果到文件
        
        Args:
            project_id: 项目ID
            output_dir: 输出目录
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(os.path.join(output_dir, "code"), exist_ok=True)
            
            # 获取项目信息
            project = self.db_manager.get_project(project_id)
            requirement = self.db_manager.get_requirement(project_id)
            outline = self.db_manager.get_outline(project_id)
            
            # 导出需求文档
            if requirement:
                with open(os.path.join(output_dir, "requirement.md"), "w", encoding="utf-8") as f:
                    f.write(requirement["content"])
            
            # 导出大纲
            if outline:
                with open(os.path.join(output_dir, "outline.json"), "w", encoding="utf-8") as f:
                    json.dump(outline["content"], f, ensure_ascii=False, indent=2)
            
            # 查询并导出代码
            query = "SELECT * FROM code_generations WHERE project_id = %s"
            code_sections = self.db_manager.execute_query(query, (project_id,))
            
            for section in code_sections:
                file_path = os.path.join(output_dir, "code", f"{section['module_name']}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(section["content"])
            
            # 查询并导出数据库脚本
            query = "SELECT * FROM db_scripts WHERE project_id = %s ORDER BY created_at DESC LIMIT 1"
            db_scripts = self.db_manager.execute_query(query, (project_id,))
            
            if db_scripts:
                with open(os.path.join(output_dir, "database.sql"), "w", encoding="utf-8") as f:
                    f.write(db_scripts[0]["content"])
            
            print(f"结果已导出到目录: {output_dir}")
            
        except Exception as e:
            print(f"导出结果失败: {str(e)}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI软件管理平台")
    parser.add_argument("-r", "--requirement", required=True, help="需求文档路径")
    parser.add_argument("-p", "--project_name", default="新项目", help="项目名称")
    parser.add_argument("-o", "--output", default="./output", help="输出目录")
    parser.add_argument("--deepseek_key", help="DeepSeek API密钥")
    parser.add_argument("--tongyi_key", help="通义前问API密钥")
    
    args = parser.parse_args()
    
    platform = AIModelPlatform(
        deepseek_api_key=args.deepseek_key,
        tongyi_api_key=args.tongyi_key
    )
    
    result = await platform.process_requirement(args.project_name, args.requirement)
    
    if "error" in result:
        print(f"处理失败: {result['error']}")
        return 1
    
    # 导出结果
    platform.export_results(result["project_id"], args.output)
    print(f"项目处理完成，项目ID: {result['project_id']}")
    return 0

if __name__ == "__main__":
    exitcode = asyncio.run(main())
    exit(exitcode) 