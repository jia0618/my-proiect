import os
import json
import openai
import logging
import requests
import sys
from datetime import datetime

# 设置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('AIService')

# 导入API配置
try:
    # 首先尝试从app.utils导入
    from app.utils.api_config import get_api_config, get_available_models
    logger.info("从app.utils.api_config导入API配置成功")
except ImportError:
    try:
        # 如果失败，尝试直接导入
        from api_config import get_api_config, get_available_models
        logger.info("从api_config导入API配置成功")
    except ImportError:
        logger.error("无法导入API配置，将使用默认值")
        # 定义默认的API配置函数
        def get_api_config():
            import os
            return {
                "deepseek_api_key": os.environ.get("DEEPSEEK_API_KEY", "sk-8612f8702df64fd3b2c66f7486ce5845"),
                "tongyi_api_key": os.environ.get("TONGYI_API_KEY", "sk-1c44c33a881a43d98639c5993ce98164")
            }
        
        def get_available_models():
            return {
                "deepseek": "deepseek-chat",
                "tongyi": "qwen-max"
            }

# 设置API密钥
openai.api_key = os.environ.get('OPENAI_API_KEY', 'your-api-key')

class AIService:
    @staticmethod
    def generate_architecture_code(requirement, language, architecture_type):
        """
        根据需求生成架构代码，先使用通义千问生成架构大纲，然后使用DeepSeek生成代码
        """
        # 获取API配置
        api_config = get_api_config()
        available_models = get_available_models()
        
        # 获取API密钥
        deepseek_api_key = api_config.get('deepseek_api_key')
        tongyi_api_key = api_config.get('tongyi_api_key')
        
        logger.info(f"开始生成架构代码，语言:{language}，架构类型:{architecture_type}")
        logger.info(f"需求内容长度:{len(requirement)}")
        
        # 第一步：使用通义千问生成架构大纲
        logger.info("尝试使用通义千问API生成架构大纲")
        logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
        
        outline_prompt = f"""
        请根据以下需求生成{language}语言的{architecture_type}架构大纲:
        
        需求描述:
        {requirement}
        
        请生成详细的架构大纲，包括系统结构、核心模块、接口定义等，以便后续进行代码生成。
        """
        
        outline = ""
        outline_success = False
        
        # 尝试使用通义千问API生成大纲
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的软件架构师，擅长设计符合需求的软件架构大纲。"},
                    {"role": "user", "content": outline_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            logger.info("发送请求到通义千问API生成大纲...")
            print("通义千问生成大纲......")
            
            # 直接使用兼容模式API
            try:
                openai_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
                logger.info("使用通义千问兼容模式API")
                
                response = requests.post(
                    openai_url,
                    headers=headers,
                    json=data,
                    timeout=180  # 延长超时时间到3分钟
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                print(f"通义千问生成大纲出错: {str(e)}")
                raise
            
            # 处理通义千问响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容（兼容模式API）
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    outline = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        outline = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        outline = str(response_data)
                
                logger.info(f"成功获取架构大纲，大纲长度:{len(outline)}")
                print(f"通义千问生成大纲成功，大纲内容:\n{outline}")
                outline_success = True
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成大纲失败: {response.text}")
                
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成大纲出错: {str(tongyi_error)}")
        
        # 第二步：使用DeepSeek生成代码
        logger.info("尝试使用DeepSeek API生成架构代码")
        
        code_prompt = f"""
        请根据以下需求和架构大纲生成{language}语言的{architecture_type}架构代码:
        
        需求描述:
        {requirement}
        
        架构大纲:
        {outline if outline_success else "请自行设计合适的架构"}
        
        请生成完整的架构代码，包括必要的文件结构、接口定义和核心组件。
        输出应该是可以直接复制粘贴的代码，包含清晰的目录结构和文件内容。
        """
        
        try:
            # DeepSeek API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_api_key}"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一位专业的软件架构师，擅长设计符合需求的软件架构。"},
                    {"role": "user", "content": code_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            logger.info(f"DeepSeek API密钥: {deepseek_api_key[:5]}...{deepseek_api_key[-4:]}")
            logger.info("发送请求到DeepSeek API")
            print("DeepSeek生成代码中...")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=300  # 增加到5分钟超时
            )
            
            # 记录API响应
            logger.info(f"DeepSeek API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"DeepSeek API响应: {str(response_data)[:200]}...")
                code = response_data['choices'][0]['message']['content']
                logger.info(f"成功获取架构代码，代码长度:{len(code)}")
                print(f"DeepSeek生成代码成功")
                
                return {
                    "success": True,
                    "code": code,
                    "outline": outline if outline_success else "",
                    "raw_response": response_data,
                    "model_used": "deepseek",
                    "outline_model_used": "tongyi" if outline_success else "none"
                }
            else:
                logger.error(f"DeepSeek API请求失败: {response.text}")
                print(f"DeepSeek生成代码失败: {response.text}")
                
                # 如果DeepSeek失败且通义千问成功生成了大纲，可以尝试通义千问生成代码
                if outline_success:
                    return AIService._fallback_to_tongyi_for_code(tongyi_api_key, code_prompt, outline)
                else:
                    raise Exception(f"DeepSeek API错误: {response.text}")
                
        except Exception as deepseek_error:
            logger.error(f"DeepSeek API异常: {str(deepseek_error)}")
            print(f"DeepSeek生成代码出错: {str(deepseek_error)}")
            
            # 如果DeepSeek失败，使用通义千问作为备选
            return AIService._fallback_to_tongyi_for_code(tongyi_api_key, code_prompt, outline)
    
    @staticmethod
    def _fallback_to_tongyi_for_code(tongyi_api_key, code_prompt, outline):
        """通义千问代码生成备选方案"""
        logger.info("尝试使用通义千问API作为备选生成代码")
        print("尝试使用通义千问作为备选生成代码...")
        
        # 通义前问API请求
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "input": {
                    "messages": [
                        {"role": "system", "content": "你是一位专业的软件架构师，擅长设计符合需求的软件架构。"},
                        {"role": "user", "content": code_prompt}
                    ]
                },
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_tokens": 4000
                }
            }
            
            logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
            logger.info("发送请求到通义千问API")
            
            # 通义千问API调用，尝试不同的端点
            try:
                response = requests.post(
                    "https://dashscope.aliyuncs.com/v1/services/aigc/text-generation/generation",
                    headers=headers,
                    json=data,
                    timeout=120
                )
                
                # 如果v1返回404，尝试v2端点
                if response.status_code == 404:
                    logger.info("通义千问v1 API返回404，尝试v2端点")
                    response = requests.post(
                        "https://dashscope.aliyuncs.com/v2/services/aigc/text-generation/generation",
                        headers=headers,
                        json=data,
                        timeout=120
                    )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                # 再尝试兼容模式API
                logger.info("尝试使用通义千问兼容模式API")
                openai_headers = {
                    "Authorization": f"Bearer {tongyi_api_key}",
                    "Content-Type": "application/json"
                }
                
                openai_data = {
                    "model": "qwen-max",
                    "messages": [
                        {"role": "system", "content": "你是一位专业的软件架构师，擅长设计符合需求的软件架构。"},
                        {"role": "user", "content": code_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
                
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=openai_headers,
                    json=openai_data,
                    timeout=120
                )
            
            # 记录API响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容
                if 'output' in response_data and 'text' in response_data['output']:
                    # 标准v1/v2格式
                    code = response_data['output']['text']
                elif 'choices' in response_data and len(response_data['choices']) > 0:
                    # 兼容模式格式
                    code = response_data['choices'][0]['message']['content']
                else:
                    # 尝试提取任何可能的文本内容
                    logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                    code = str(response_data)
                
                logger.info(f"成功获取架构代码，代码长度:{len(code)}")
                print(f"通义千问生成代码成功")
                
                return {
                    "success": True,
                    "code": code,
                    "outline": outline,
                    "raw_response": response_data,
                    "model_used": "tongyi",
                    "outline_model_used": "tongyi"
                }
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成代码失败: {response.text}")
                return {
                    "success": False,
                    "error": f"所有模型API均调用失败，通义千问错误:{response.text}",
                    "outline": outline,
                    "tongyi_error": response.text
                }
            
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成代码异常: {str(tongyi_error)}")
            return {
                "success": False,
                "error": f"所有模型API均调用失败，通义千问错误:{str(tongyi_error)}",
                "outline": outline,
                "tongyi_error": str(tongyi_error)
            }
    
    @staticmethod
    def generate_database_design(requirement):
        """
        根据需求生成数据库设计，使用通义千问生成大纲，DeepSeek生成具体脚本
        """
        api_config = get_api_config()
        deepseek_api_key = api_config.get('deepseek_api_key')
        tongyi_api_key = api_config.get('tongyi_api_key')
        
        logger.info(f"开始生成数据库设计，需求内容长度:{len(requirement)}")
        
        # 第一步：使用通义千问生成数据库大纲
        logger.info("尝试使用通义千问API生成数据库大纲")
        logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
        
        outline_prompt = f"""
        请分析以下需求，生成数据库设计大纲。大纲应包括：
        1. 所需的数据库表
        2. 每个表的主要字段
        3. 表之间的关系
        4. 索引设计建议
        
        请输出JSON格式，确保格式正确可解析。
        
        需求描述:
        {requirement}
        """
        
        db_outline = ""
        outline_success = False
        
        # 尝试使用通义千问API生成大纲
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的数据库设计师，擅长根据需求设计高效的数据库结构。"},
                    {"role": "user", "content": outline_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            logger.info("发送请求到通义千问API生成数据库大纲...")
            print("通义千问生成数据库大纲......")
            
            # 使用兼容模式API
            try:
                openai_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
                logger.info("使用通义千问兼容模式API")
                
                response = requests.post(
                    openai_url,
                    headers=headers,
                    json=data,
                    timeout=180  # 延长超时时间到3分钟
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                print(f"通义千问生成数据库大纲出错: {str(e)}")
                raise
            
            # 处理通义千问响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容（兼容模式API）
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    db_outline = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        db_outline = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        db_outline = str(response_data)
                
                logger.info(f"成功获取数据库大纲，大纲长度:{len(db_outline)}")
                print(f"通义千问生成数据库大纲成功，大纲内容:\n{db_outline}")
                outline_success = True
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成数据库大纲失败: {response.text}")
                
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成数据库大纲出错: {str(tongyi_error)}")

        # 第二步：使用DeepSeek生成详细的数据库脚本
        logger.info("尝试使用DeepSeek API生成数据库脚本")
        
        prompt = f"""
        请根据以下需求和数据库大纲设计MySQL数据库表结构:
        
        需求描述:
        {requirement}
        
        数据库大纲:
        {db_outline if outline_success else "请根据需求设计合适的数据库结构"}
        
        严格按照以下要求编写MySQL CREATE TABLE语句:
        1. 每个表必须有自增ID主键: `id` INT NOT NULL AUTO_INCREMENT
        2. 每个表必须包含created_at和updated_at时间戳字段
        3. 每个表和字段必须使用COMMENT添加中文注释
        4. 所有表必须使用InnoDB引擎，utf8mb4字符集和utf8mb4_unicode_ci排序规则
        5. 正确定义外键关系
        6. 字段名称必须使用下划线命名法(如user_name)
        7. 必须使用反引号`包裹所有表名和字段名

        每个表的CREATE TABLE语句必须使用这个模板:
        ```sql
        CREATE TABLE `表名` (
          `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
          `字段名` 数据类型 [约束] COMMENT '字段说明',
          ...其他字段...
          `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
          PRIMARY KEY (`id`),
          [索引和外键定义]
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表说明';
        ```

        另外，请一定将表结构以JSON格式提供，格式如下:
        ```json
        {{
          "tables": [
            {{
              "name": "表名",
              "description": "表描述",
              "fields": [
                {{"name": "id", "type": "INT", "description": "主键ID", "constraints": "NOT NULL AUTO_INCREMENT"}},
                {{"name": "字段名", "type": "数据类型", "description": "字段描述", "constraints": "约束"}}
              ],
              "primary_key": ["id"],
              "foreign_keys": [{{"field": "外键字段", "references": "引用表.引用字段"}}],
              "indexes": [{{"name": "索引名", "fields": ["字段1", "字段2"]}}]
            }}
          ],
          "relationships": [
            {{"from": "表名.字段", "to": "表名.字段", "type": "1:N"}}
          ]
        }}
        ```

        请确保返回两部分内容:
        1. 多个CREATE TABLE SQL语句
        2. 上述JSON格式的表结构数据

        请注意SQL必须是有效的MySQL 5.7语法，不要省略任何必要的语法元素。
        """
        
        design = ""
        response_data = None
        deepseek_error_message = "DeepSeek 未尝试或未记录错误" # Default error message

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_api_key}"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一位专业的数据库设计师，擅长根据需求设计高效的数据库结构。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            logger.info(f"DeepSeek API密钥: {deepseek_api_key[:5]}...{deepseek_api_key[-4:]}")
            logger.info("发送请求到DeepSeek API")
            print("DeepSeek生成数据库脚本中...")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=300
            )
            logger.info(f"DeepSeek API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"DeepSeek API响应: {str(response_data)[:200]}...")
                design = response_data['choices'][0]['message']['content']
                logger.info(f"成功获取数据库设计，内容长度:{len(design)}")
                print(f"DeepSeek生成数据库脚本成功")
                
                return {
                    "success": True,
                    "design": design,
                    "outline": db_outline if outline_success else "",
                    "raw_response": response_data,
                    "model_used": "deepseek",
                    "outline_model_used": "tongyi" if outline_success else "none"
                }
            else: 
                logger.error(f"DeepSeek API请求失败: {response.text}")
                print(f"DeepSeek生成数据库脚本失败: {response.text}")
                deepseek_error_message = f"DeepSeek API错误: {response.text}"
                raise Exception(deepseek_error_message)
                
        except Exception as deepseek_error_obj:
            if deepseek_error_message == "DeepSeek 未尝试或未记录错误":
                 deepseek_error_message = str(deepseek_error_obj)
            logger.error(f"DeepSeek API异常或明确失败: {deepseek_error_message}")
            logger.info("尝试使用通义前问API作为备选")
            print(f"DeepSeek生成数据库脚本出错: {str(deepseek_error_obj)}")
            
            # 如果DeepSeek失败，使用通义千问作为备选
            return AIService._fallback_to_tongyi_for_database(tongyi_api_key, prompt, db_outline)
    
    @staticmethod
    def _fallback_to_tongyi_for_database(tongyi_api_key, prompt, outline):
        """通义千问数据库脚本生成备选方案"""
        logger.info("尝试使用通义千问API作为备选生成数据库脚本")
        print("尝试使用通义千问作为备选生成数据库脚本...")
        
        # 通义前问API请求
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的数据库设计师，擅长根据需求设计高效的数据库结构。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
            logger.info("发送请求到通义千问API")
            
            # 通义千问兼容模式API调用
            try:
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=180
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                raise
            
            # 记录API响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    design = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        design = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        design = str(response_data)
                
                logger.info(f"成功获取数据库设计，内容长度:{len(design)}")
                print(f"通义千问生成数据库脚本成功")
                
                return {
                    "success": True,
                    "design": design,
                    "outline": outline,
                    "raw_response": response_data,
                    "model_used": "tongyi",
                    "outline_model_used": "tongyi"
                }
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成数据库脚本失败: {response.text}")
                return {
                    "success": False,
                    "error": f"所有模型API均调用失败，通义千问错误:{response.text}",
                    "outline": outline,
                    "tongyi_error": response.text
                }
            
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成数据库脚本异常: {str(tongyi_error)}")
            return {
                "success": False,
                "error": f"所有模型API均调用失败，通义千问错误:{str(tongyi_error)}",
                "outline": outline,
                "tongyi_error": str(tongyi_error)
            }
    
    @staticmethod
    def generate_module_code(requirement, architecture_code, module_type):
        """
        根据需求和架构代码生成模块代码，先使用通义千问生成模块大纲，再使用DeepSeek生成具体代码
        """
        api_config = get_api_config()
        deepseek_api_key = api_config.get('deepseek_api_key')
        tongyi_api_key = api_config.get('tongyi_api_key')
        
        logger.info(f"开始生成模块代码，模块类型:{module_type}")
        logger.info(f"需求内容长度:{len(requirement)}，架构代码长度:{len(architecture_code)}")
        
        # 第一步：使用通义千问生成模块大纲
        logger.info("尝试使用通义千问API生成模块大纲")
        logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
        
        outline_prompt = f"""
        请根据以下需求和架构代码，生成{module_type}模块的设计大纲。大纲应包括：
        1. 模块主要功能和职责
        2. 核心类和方法设计
        3. 与其他模块的交互方式
        4. 关键算法或业务逻辑说明
        
        请输出JSON格式，确保格式正确可解析。
        
        需求描述:
        {requirement}
        
        架构代码（参考）:
        {architecture_code[:2000] + "..." if len(architecture_code) > 2000 else architecture_code}
        """
        
        module_outline = ""
        outline_success = False
        
        # 尝试使用通义千问API生成大纲
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的软件开发者，擅长根据架构和需求开发功能模块。"},
                    {"role": "user", "content": outline_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            logger.info("发送请求到通义千问API生成模块大纲...")
            print("通义千问生成模块大纲......")
            
            # 使用兼容模式API
            try:
                openai_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
                logger.info("使用通义千问兼容模式API")
                
                response = requests.post(
                    openai_url,
                    headers=headers,
                    json=data,
                    timeout=180  # 延长超时时间到3分钟
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                print(f"通义千问生成模块大纲出错: {str(e)}")
                raise
            
            # 处理通义千问响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容（兼容模式API）
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    module_outline = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        module_outline = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        module_outline = str(response_data)
                
                logger.info(f"成功获取模块大纲，大纲长度:{len(module_outline)}")
                print(f"通义千问生成模块大纲成功，大纲内容:\n{module_outline}")
                outline_success = True
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成模块大纲失败: {response.text}")
                
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成模块大纲出错: {str(tongyi_error)}")

        # 第二步：使用DeepSeek生成详细的模块代码
        logger.info("尝试使用DeepSeek API生成模块代码")
        
        prompt = f"""
        请根据以下需求、架构代码和模块大纲生成{module_type}模块的代码:
        
        需求描述:
        {requirement}
        
        架构代码:
        {architecture_code[:2000] + "..." if len(architecture_code) > 2000 else architecture_code}
        
        模块大纲:
        {module_outline if outline_success else "请自行设计合适的模块结构"}
        
        请生成完整的模块代码，包括必要的类、方法和依赖项。
        """

        code = ""
        response_data = None
        deepseek_error_message = "DeepSeek 未尝试或未记录错误" # Default error message

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_api_key}"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一位专业的软件开发者，擅长根据架构和需求开发功能模块。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            logger.info(f"DeepSeek API密钥: {deepseek_api_key[:5]}...{deepseek_api_key[-4:]}")
            logger.info("发送请求到DeepSeek API")
            print("DeepSeek生成模块代码中...")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=300
            )
            logger.info(f"DeepSeek API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"DeepSeek API响应: {str(response_data)[:200]}...")
                code = response_data['choices'][0]['message']['content']
                logger.info(f"成功获取模块代码，代码长度:{len(code)}")
                print(f"DeepSeek生成模块代码成功")
                
                return {
                    "success": True,
                    "code": code,
                    "outline": module_outline if outline_success else "",
                    "raw_response": response_data,
                    "model_used": "deepseek",
                    "outline_model_used": "tongyi" if outline_success else "none"
                }
            else:
                logger.error(f"DeepSeek API请求失败: {response.text}")
                print(f"DeepSeek生成模块代码失败: {response.text}")
                deepseek_error_message = f"DeepSeek API错误: {response.text}"
                raise Exception(deepseek_error_message)
                
        except Exception as deepseek_error_obj:
            if deepseek_error_message == "DeepSeek 未尝试或未记录错误":
                 deepseek_error_message = str(deepseek_error_obj)
            logger.error(f"DeepSeek API异常或明确失败: {deepseek_error_message}")
            logger.info("尝试使用通义前问API作为备选")
            print(f"DeepSeek生成模块代码出错: {str(deepseek_error_obj)}")
            
            # 如果DeepSeek失败，使用通义千问作为备选
            return AIService._fallback_to_tongyi_for_module(tongyi_api_key, prompt, module_outline)
    
    @staticmethod
    def _fallback_to_tongyi_for_module(tongyi_api_key, prompt, outline):
        """通义千问模块代码生成备选方案"""
        logger.info("尝试使用通义千问API作为备选生成模块代码")
        print("尝试使用通义千问作为备选生成模块代码...")
        
        # 通义前问API请求
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的软件开发者，擅长根据架构和需求开发功能模块。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
            logger.info("发送请求到通义千问API")
            
            # 通义千问兼容模式API调用
            try:
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=180
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                raise
            
            # 记录API响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    code = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        code = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        code = str(response_data)
                
                logger.info(f"成功获取模块代码，代码长度:{len(code)}")
                print(f"通义千问生成模块代码成功")
                
                return {
                    "success": True,
                    "code": code,
                    "outline": outline,
                    "raw_response": response_data,
                    "model_used": "tongyi",
                    "outline_model_used": "tongyi"
                }
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成模块代码失败: {response.text}")
                return {
                    "success": False,
                    "error": f"所有模型API均调用失败，通义千问错误:{response.text}",
                    "outline": outline,
                    "tongyi_error": response.text
                }
            
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成模块代码异常: {str(tongyi_error)}")
            return {
                "success": False,
                "error": f"所有模型API均调用失败，通义千问错误:{str(tongyi_error)}",
                "outline": outline,
                "tongyi_error": str(tongyi_error)
            }
    
    @staticmethod
    def generate_test_cases(code, test_type, test_count=3):
        """
        根据代码生成测试用例，先使用通义千问生成测试大纲，再使用DeepSeek生成详细测试用例
        @param code: 要测试的代码
        @param test_type: 测试类型
        @param test_count: 要生成的测试用例数量，默认为3
        @return: 包含测试用例的字典
        """
        api_config = get_api_config()
        deepseek_api_key = api_config.get('deepseek_api_key')
        tongyi_api_key = api_config.get('tongyi_api_key')
        
        logger.info(f"开始生成测试用例，测试类型:{test_type}，数量:{test_count}")
        logger.info(f"代码长度:{len(code)}")
        
        if len(code) > 10000:
            logger.info(f"代码过长，截取前10000个字符用于生成测试用例")
            code_for_prompt = code[:10000] + "\n... [代码过长，已截断]"
        else:
            code_for_prompt = code
        
        # 第一步：使用通义千问生成测试大纲
        logger.info("尝试使用通义千问API生成测试大纲")
        logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
        
        outline_prompt = f"""
        请根据以下代码分析，生成{test_count}个{test_type}测试用例的大纲。
        
        需要测试的代码:
        {code_for_prompt}
        
        大纲应包括：
        1. 测试名称
        2. 测试目的
        3. 测试点与测试策略
        4. 预期结果概述
        
        请以JSON数组格式输出，确保格式正确可解析。
        [
          {{
            "name": "测试1名称",
            "purpose": "测试1目的",
            "test_points": ["测试点1", "测试点2"],
            "expected_result": "预期结果概述"
          }}
        ]
        """
        
        test_outline = ""
        outline_success = False
        
        # 尝试使用通义千问API生成大纲
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的测试工程师，擅长编写全面的测试用例。"},
                    {"role": "user", "content": outline_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            logger.info("发送请求到通义千问API生成测试大纲...")
            print("通义千问生成测试大纲......")
            
            # 使用兼容模式API
            try:
                openai_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
                logger.info("使用通义千问兼容模式API")
                
                response = requests.post(
                    openai_url,
                    headers=headers,
                    json=data,
                    timeout=180  # 延长超时时间到3分钟
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                print(f"通义千问生成测试大纲出错: {str(e)}")
                raise
            
            # 处理通义千问响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容（兼容模式API）
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    test_outline = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        test_outline = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        test_outline = str(response_data)
                
                logger.info(f"成功获取测试大纲，大纲长度:{len(test_outline)}")
                print(f"通义千问生成测试大纲成功，大纲内容:\n{test_outline}")
                outline_success = True
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成测试大纲失败: {response.text}")
                
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成测试大纲出错: {str(tongyi_error)}")

        # 第二步：使用DeepSeek生成详细的测试用例
        logger.info("尝试使用DeepSeek API生成测试用例")
        
        prompt = f"""
        请根据以下代码和测试大纲生成{test_count}个{test_type}测试用例:
        
        代码:
        {code_for_prompt}
        
        测试大纲:
        {test_outline if outline_success else "请自行设计合适的测试用例"}
        
        请生成{test_count}个测试用例，每个测试用例应该简洁明了，包含以下内容：
        1. 测试名称
        2. 测试目的（简短描述）
        3. 测试步骤（简洁的步骤列表，每个步骤不超过一句话）
        4. 预期结果
        
        将每个测试用例以JSON数组格式返回，示例格式如下：
        [
          {{
            "name": "测试用例1名称",
            "purpose": "测试目的描述",
            "steps": ["步骤1", "步骤2", "步骤3"],
            "expected_result": "预期结果描述"
          }},
          {{
            "name": "测试用例2名称",
            "purpose": "测试目的描述",
            "steps": ["步骤1", "步骤2", "步骤3"],
            "expected_result": "预期结果描述"
          }}
        ]
        
        请确保生成的测试用例步骤简洁明了，每个步骤不要超过一句话。
        """

        test_cases_result = [] # Default to empty list if all fails
        response_data = None
        deepseek_error_message = "DeepSeek 未尝试或未记录错误" # Default error message

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_api_key}"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一位专业的测试工程师，擅长编写全面的测试用例。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            logger.info(f"DeepSeek API密钥: {deepseek_api_key[:5]}...{deepseek_api_key[-4:]}")
            logger.info("发送请求到DeepSeek API")
            print("DeepSeek生成测试用例中...")
            
            response = None # Ensure response is defined
            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=120
                )
                logger.info(f"DeepSeek API响应状态码: {response.status_code}")
                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"DeepSeek API响应: {str(response_data)[:200]}...")
                    raw_test_cases_str = response_data['choices'][0]['message']['content']
                    logger.info(f"成功获取测试用例字符串，内容长度:{len(raw_test_cases_str)}")
                    print(f"DeepSeek生成测试用例成功")
                    
                    parsed_test_cases = []
                    try:
                        import re
                        json_pattern = r'\[\s*\{.*?\}\s*\]' # Regex to find JSON array
                        json_match = re.search(json_pattern, raw_test_cases_str, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            parsed_test_cases = json.loads(json_str)
                            logger.info(f"成功解析为JSON，获取到{len(parsed_test_cases)}个测试用例")
                            while len(parsed_test_cases) < test_count:
                                default_case_dict = generate_default_test_case(test_type, as_dict=True)
                                new_case = default_case_dict.copy() # Make a copy to modify
                                new_case["name"] = f"{new_case.get('name', 'Default Test')} (复制 {len(parsed_test_cases) + 1})"
                                parsed_test_cases.append(new_case)
                        else:
                            logger.warning("DeepSeek响应中未找到有效的JSON数组，将使用原始字符串作为单个测试用例。")
                            # Fallback: treat raw string as a single test case description or part of one
                            parsed_test_cases = [generate_default_test_case(test_type, content=raw_test_cases_str)] 
                    except Exception as json_error:
                        logger.error(f"无法解析DeepSeek响应为JSON: {str(json_error)}，将使用原始字符串。")
                        parsed_test_cases = [generate_default_test_case(test_type, content=raw_test_cases_str)]
                    
                    return {
                        "success": True,
                        "test_cases": parsed_test_cases,
                        "outline": test_outline if outline_success else "",
                        "raw_response": response_data,
                        "model_used": "deepseek",
                        "outline_model_used": "tongyi" if outline_success else "none"
                    }
                else:
                    logger.error(f"DeepSeek API请求失败: {response.text}")
                    print(f"DeepSeek生成测试用例失败: {response.text}")
                    deepseek_error_message = f"DeepSeek API错误: {response.text}"
                    raise Exception(deepseek_error_message)
            except requests.exceptions.Timeout:
                logger.error("DeepSeek API请求超时")
                deepseek_error_message = "DeepSeek API请求超时"
                raise Exception(deepseek_error_message)
            except requests.exceptions.RequestException as e_req:
                logger.error(f"DeepSeek API请求异常: {str(e_req)}")
                deepseek_error_message = f"DeepSeek API请求异常: {str(e_req)}"
                raise Exception(deepseek_error_message)
                
        except Exception as deepseek_error_obj:
            if deepseek_error_message == "DeepSeek 未尝试或未记录错误":
                deepseek_error_message = str(deepseek_error_obj)
            logger.error(f"DeepSeek API处理异常或明确失败: {deepseek_error_message}")
            logger.info("尝试使用通义前问API作为备选")
            print(f"DeepSeek生成测试用例出错: {str(deepseek_error_obj)}")
            
            # 如果DeepSeek失败，使用通义千问作为备选
            return AIService._fallback_to_tongyi_for_testcases(tongyi_api_key, prompt, test_outline, test_type, test_count)
    
    @staticmethod
    def _fallback_to_tongyi_for_testcases(tongyi_api_key, prompt, outline, test_type, test_count):
        """通义千问测试用例生成备选方案"""
        logger.info("尝试使用通义千问API作为备选生成测试用例")
        print("尝试使用通义千问作为备选生成测试用例...")
        
        # 通义前问API请求
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的测试工程师，擅长编写全面的测试用例。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
            logger.info("发送请求到通义千问API")
            
            # 通义千问兼容模式API调用
            try:
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=180
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                raise
            
            # 记录API响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 提取响应内容
                raw_test_cases_str = ""
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    raw_test_cases_str = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        raw_test_cases_str = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        raw_test_cases_str = str(response_data)
                
                logger.info(f"成功获取测试用例字符串，内容长度:{len(raw_test_cases_str)}")
                print(f"通义千问生成测试用例成功")
                
                # 解析JSON
                parsed_test_cases = []
                try:
                    import re
                    json_pattern = r'\[\s*\{.*?\}\s*\]'
                    json_match = re.search(json_pattern, raw_test_cases_str, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        parsed_test_cases = json.loads(json_str)
                        logger.info(f"成功解析为JSON，获取到{len(parsed_test_cases)}个测试用例")
                        while len(parsed_test_cases) < test_count:
                            default_case_dict = generate_default_test_case(test_type, as_dict=True)
                            new_case = default_case_dict.copy()
                            new_case["name"] = f"{new_case.get('name', 'Default Test')} (复制 {len(parsed_test_cases) + 1})"
                            parsed_test_cases.append(new_case)
                    else:
                        logger.warning("通义千问响应中未找到有效的JSON数组")
                        parsed_test_cases = [generate_default_test_case(test_type, content=raw_test_cases_str)]
                except Exception as json_error:
                    logger.error(f"无法解析通义千问响应为JSON: {str(json_error)}")
                    parsed_test_cases = [generate_default_test_case(test_type, content=raw_test_cases_str)]
                
                return {
                    "success": True,
                    "test_cases": parsed_test_cases,
                    "outline": outline,
                    "raw_response": response_data,
                    "model_used": "tongyi",
                    "outline_model_used": "tongyi"
                }
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成测试用例失败: {response.text}")
                test_cases_result = [generate_default_test_case(test_type) for _ in range(test_count)]
                return {
                    "success": True, # Still success=True but with default cases
                    "test_cases": test_cases_result,
                    "outline": outline,
                    "error_message": f"所有API调用失败，使用默认测试用例。",
                    "model_used": "default"
                }
        
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成测试用例异常: {str(tongyi_error)}")
            test_cases_result = [generate_default_test_case(test_type) for _ in range(test_count)]
            return {
                "success": True, # Still success=True but with default cases
                "test_cases": test_cases_result,
                "outline": outline,
                "error_message": f"API调用异常，使用默认测试用例。错误: {str(tongyi_error)}",
                "model_used": "default"
            }

    @staticmethod
    def generate_deployment_steps(architecture_code):
        """
        根据架构代码生成部署步骤，先使用通义千问生成部署大纲，再使用DeepSeek生成具体部署步骤
        """
        api_config = get_api_config()
        deepseek_api_key = api_config.get('deepseek_api_key')
        tongyi_api_key = api_config.get('tongyi_api_key')
        
        logger.info(f"开始生成部署步骤，架构代码长度:{len(architecture_code)}")
        
        if len(architecture_code) > 10000:
            logger.info(f"架构代码过长，截取前10000个字符用于生成部署步骤")
            code_for_prompt = architecture_code[:10000] + "\n... [代码过长，已截断]"
        else:
            code_for_prompt = architecture_code
        
        # 第一步：使用通义千问生成部署大纲
        logger.info("尝试使用通义千问API生成部署大纲")
        logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
        
        outline_prompt = f"""
        请分析以下架构代码，生成项目部署大纲。大纲应包括：
        1. 系统部署架构
        2. 所需环境和依赖
        3. 主要部署步骤概述
        4. 部署前的准备工作
        5. 关键配置项
        6. 部署后的验证方法
        
        请输出JSON格式，确保格式正确可解析。
        
        架构代码:
        {code_for_prompt}
        """
        
        deployment_outline = ""
        outline_success = False
        
        # 尝试使用通义千问API生成大纲
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的DevOps工程师，擅长系统部署和配置。"},
                    {"role": "user", "content": outline_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            logger.info("发送请求到通义千问API生成部署大纲...")
            print("通义千问生成部署大纲......")
            
            # 使用兼容模式API
            try:
                openai_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
                logger.info("使用通义千问兼容模式API")
                
                response = requests.post(
                    openai_url,
                    headers=headers,
                    json=data,
                    timeout=180  # 延长超时时间到3分钟
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                print(f"通义千问生成部署大纲出错: {str(e)}")
                raise
            
            # 处理通义千问响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容（兼容模式API）
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    deployment_outline = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        deployment_outline = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        deployment_outline = str(response_data)
                
                logger.info(f"成功获取部署大纲，大纲长度:{len(deployment_outline)}")
                print(f"通义千问生成部署大纲成功，大纲内容:\n{deployment_outline}")
                outline_success = True
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成部署大纲失败: {response.text}")
                
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成部署大纲出错: {str(tongyi_error)}")

        # 第二步：使用DeepSeek生成详细的部署步骤
        logger.info("尝试使用DeepSeek API生成部署步骤")
        
        prompt = f"""
        请根据以下架构代码和部署大纲生成详细的部署步骤:
        
        架构代码:
        {code_for_prompt}
        
        部署大纲:
        {deployment_outline if outline_success else "请自行设计合适的部署步骤"}
        
        请提供完整的部署指南，包括环境配置、安装依赖、部署命令等。
        """
        
        deployment_steps_result = "" # Default value
        response_data = None
        deepseek_error_message = "DeepSeek 未尝试或未记录错误" # Default error message

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_api_key}"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一位专业的DevOps工程师，擅长系统部署和配置。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 3000
            }
            logger.info(f"DeepSeek API密钥: {deepseek_api_key[:5]}...{deepseek_api_key[-4:]}")
            logger.info("发送请求到DeepSeek API")
            print("DeepSeek生成部署步骤中...")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            logger.info(f"DeepSeek API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"DeepSeek API响应: {str(response_data)[:200]}...")
                deployment_steps_result = response_data['choices'][0]['message']['content']
                logger.info(f"成功获取部署步骤，内容长度:{len(deployment_steps_result)}")
                print(f"DeepSeek生成部署步骤成功")
                
                return {
                    "success": True,
                    "deployment_steps": deployment_steps_result,
                    "outline": deployment_outline if outline_success else "",
                    "raw_response": response_data,
                    "model_used": "deepseek",
                    "outline_model_used": "tongyi" if outline_success else "none"
                }
            else:
                logger.error(f"DeepSeek API请求失败: {response.text}")
                print(f"DeepSeek生成部署步骤失败: {response.text}")
                deepseek_error_message = f"DeepSeek API错误: {response.text}"
                raise Exception(deepseek_error_message)
                
        except Exception as deepseek_error_obj:
            if deepseek_error_message == "DeepSeek 未尝试或未记录错误":
                 deepseek_error_message = str(deepseek_error_obj)
            logger.error(f"DeepSeek API异常或明确失败: {deepseek_error_message}")
            logger.info("尝试使用通义前问API作为备选")
            print(f"DeepSeek生成部署步骤出错: {str(deepseek_error_obj)}")
            
            # 如果DeepSeek失败，使用通义千问作为备选
            return AIService._fallback_to_tongyi_for_deployment(tongyi_api_key, prompt, deployment_outline)
    
    @staticmethod
    def _fallback_to_tongyi_for_deployment(tongyi_api_key, prompt, outline):
        """通义千问部署步骤生成备选方案"""
        logger.info("尝试使用通义千问API作为备选生成部署步骤")
        print("尝试使用通义千问作为备选生成部署步骤...")
        
        # 通义前问API请求
        try:
            headers = {
                "Authorization": f"Bearer {tongyi_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-max",
                "messages": [
                    {"role": "system", "content": "你是一位专业的DevOps工程师，擅长系统部署和配置。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 3000
            }
            
            logger.info(f"通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
            logger.info("发送请求到通义千问API")
            
            # 通义千问兼容模式API调用
            try:
                response = requests.post(
                    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=180
                )
            except Exception as e:
                logger.error(f"通义千问API请求异常: {str(e)}")
                raise
            
            # 记录API响应
            logger.info(f"通义千问API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"通义千问API响应: {str(response_data)[:200]}...")
                
                # 根据API响应格式提取内容
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    deployment_steps_result = response_data['choices'][0]['message']['content']
                else:
                    # 如果没有找到兼容模式的响应格式，尝试其他格式
                    if 'output' in response_data and 'text' in response_data['output']:
                        deployment_steps_result = response_data['output']['text']
                    else:
                        # 尝试提取任何可能的文本内容
                        logger.warning(f"未识别的通义千问API响应格式: {str(response_data)[:300]}")
                        deployment_steps_result = str(response_data)
                
                logger.info(f"成功获取部署步骤，内容长度:{len(deployment_steps_result)}")
                print(f"通义千问生成部署步骤成功")
                
                return {
                    "success": True,
                    "deployment_steps": deployment_steps_result,
                    "outline": outline,
                    "raw_response": response_data,
                    "model_used": "tongyi",
                    "outline_model_used": "tongyi"
                }
            else:
                logger.error(f"通义千问API请求失败: {response.text}")
                print(f"通义千问生成部署步骤失败: {response.text}")
                deployment_steps_result = generate_default_deployment_steps()
                return {
                    "success": True,
                    "deployment_steps": deployment_steps_result,
                    "outline": outline,
                    "error_message": f"所有API调用失败，使用默认部署步骤。",
                    "model_used": "default"
                }
            
        except Exception as tongyi_error:
            logger.error(f"通义千问API异常: {str(tongyi_error)}")
            print(f"通义千问生成部署步骤异常: {str(tongyi_error)}")
            deployment_steps_result = generate_default_deployment_steps()
            return {
                "success": True,
                "deployment_steps": deployment_steps_result,
                "outline": outline,
                "error_message": f"API调用异常，使用默认部署步骤。错误: {str(tongyi_error)}",
                "model_used": "default"
            }

# 生成默认部署步骤的辅助函数
def generate_default_deployment_steps():
    """
    当所有API调用失败时，生成默认的部署步骤
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return f"""
# 部署步骤 (自动生成于 {current_time})

## 1. 环境准备

1. 安装必要的软件:
   - 安装 Git
   - 安装 Node.js 和 npm
   - 安装 Python 3.8+

2. 克隆代码仓库:
   ```
   git clone https://github.com/your-organization/your-project.git
   cd your-project
   ```

## 2. 后端部署

1. 创建并激活Python虚拟环境:
   ```
   python -m venv venv
   source venv/bin/activate  # 在Windows上使用: venv\\Scripts\\activate
   ```

2. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

3. 配置环境变量:
   - 创建.env文件并设置必要的环境变量
   - 包括数据库连接信息、API密钥等

4. 初始化数据库:
   ```
   python manage.py migrate
   ```

5. 启动后端服务:
   ```
   python manage.py runserver
   ```

## 3. 前端部署

1. 安装依赖:
   ```
   npm install
   ```

2. 构建前端资源:
   ```
   npm run build
   ```

3. 启动前端服务:
   ```
   npm start
   ```

## 4. 生产环境部署

1. 设置Nginx/Apache配置
2. 配置HTTPS证书
3. 设置数据库备份策略
4. 配置监控和日志系统
5. 设置CI/CD流程

## 注意事项
- 确保所有敏感信息使用环境变量或配置文件管理
- 生产环境部署前进行全面测试
- 设置定期备份机制
- 配置适当的防火墙规则

这是一个基本的部署流程模板，请根据实际项目架构和需求进行调整。
"""

# 生成默认测试用例的辅助函数
def generate_default_test_case(test_type):
    """
    当所有API调用失败时，生成一个简单的默认测试用例
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if test_type.lower() == 'unit':
        return f"""
# 单元测试用例 (自动生成于 {current_time})
import unittest

class DefaultUnitTest(unittest.TestCase):
    
    def setUp(self):
        # 测试准备工作
        self.test_data = "test_value"
    
    def test_basic_functionality(self):
        # 测试基本功能
        self.assertEqual(1 + 1, 2)
        self.assertTrue(len(self.test_data) > 0)
    
    def test_error_handling(self):
        # 测试错误处理
        with self.assertRaises(ValueError):
            int("not_a_number")
    
    def tearDown(self):
        # 测试清理工作
        pass

if __name__ == '__main__':
    unittest.main()
"""
    elif test_type.lower() == 'integration':
        return f"""
# 集成测试用例 (自动生成于 {current_time})
import unittest

class DefaultIntegrationTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # 设置测试环境
        cls.system_ready = True
    
    def test_component_interaction(self):
        # 测试组件交互
        self.assertTrue(self.system_ready)
        # 模拟组件A调用组件B
        result = "component_B_response"
        self.assertEqual(result, "component_B_response")
    
    def test_data_flow(self):
        # 测试数据流
        input_data = {"key": "value"}
        # 模拟数据通过系统流转
        output_data = {"key": "processed_value"}
        self.assertEqual(output_data["key"], "processed_value")
    
    @classmethod
    def tearDownClass(cls):
        # 清理测试环境
        pass

if __name__ == '__main__':
    unittest.main()
"""
    else:
        return f"""
# {test_type} 测试用例 (自动生成于 {current_time})

## 测试目标
- 验证系统功能是否正常工作
- 确保用户体验符合预期
- 检查性能是否满足要求

## 测试步骤
1. 准备测试环境和数据
2. 执行测试操作
3. 验证测试结果
4. 记录测试发现
5. 清理测试环境

## 预期结果
- 所有功能正常工作
- 无严重错误或异常
- 性能指标在可接受范围内

## 测试数据
- 测试输入: "示例输入数据"
- 预期输出: "示例预期结果"

## 附加说明
这是一个自动生成的默认测试用例，请根据实际项目需求进行调整和完善。
""" 