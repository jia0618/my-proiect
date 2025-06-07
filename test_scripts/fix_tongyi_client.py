import sys
import os
import requests
import json
import logging

# 添加项目根目录到Python路径，以便导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('FixTongyiClient')

# 尝试导入项目模块
try:
    from api_config import get_api_config
    from tongyi_client import TongyiClient
except ImportError as e:
    logger.error(f"导入项目模块失败: {e}")
    sys.exit(1)

# 测试通义千问的最新正确API端点
def test_tongyi_api():
    """测试通义千问API调用，并提供修复建议"""
    # 获取API配置
    config = get_api_config()
    tongyi_api_key = config.get("tongyi_api_key")
    
    if not tongyi_api_key:
        logger.error("未找到通义千问API密钥")
        return
    
    logger.info(f"使用通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")

    # 测试需求
    requirement = """
    开发一个在线购物系统，实现商品浏览、购物车、订单管理和支付功能。
    系统需要支持用户注册、登录，商品分类和搜索，订单跟踪等功能。
    """

    # 测试可能的API端点
    api_endpoints = [
        "https://dashscope.aliyuncs.com/v1/services/aigc/text-generation/generation",
        "https://dashscope.aliyuncs.com/v2/services/aigc/text-generation/generation",
        "https://api.dashscope.aliyuncs.com/v1/services/aigc/text-generation/generation",
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    ]
    
    # 提示信息
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

    # 测试标准API格式
    standard_data = {
        "model": "qwen-max",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一位专业的软件架构师，擅长设计符合需求的软件架构大纲。"},
                {"role": "user", "content": prompt}
            ]
        },
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.8,
            "max_tokens": 2000
        }
    }
    
    # 测试兼容模式API格式
    compatible_data = {
        "model": "qwen-max",
        "messages": [
            {"role": "system", "content": "你是一位专业的软件架构师，擅长设计符合需求的软件架构大纲。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    # 测试每个API端点
    working_endpoint = None
    working_format = None
    working_response = None
    
    # 标准格式测试
    for endpoint in api_endpoints:
        headers = {
            "Authorization": f"Bearer {tongyi_api_key}",
            "Content-Type": "application/json"
        }
        
        # 是否为兼容模式API
        is_compatible = "compatible-mode" in endpoint
        data = compatible_data if is_compatible else standard_data
        
        try:
            logger.info(f"尝试API端点: {endpoint}")
            logger.info(f"使用{'兼容模式' if is_compatible else '标准'}请求格式")
            
            response = requests.post(endpoint, headers=headers, json=data, timeout=30)
            logger.info(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("API调用成功！")
                logger.info(f"响应内容: {response.text[:200]}...")
                working_endpoint = endpoint
                working_format = "compatible" if is_compatible else "standard"
                working_response = response.json()
                break
            else:
                logger.error(f"API调用失败: {response.text}")
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")

    # 输出测试结果和修复建议
    if working_endpoint:
        logger.info("=" * 80)
        logger.info(f"找到有效的API端点: {working_endpoint}")
        logger.info(f"使用的请求格式: {working_format}")
        logger.info("=" * 80)
        logger.info("建议修改 tongyi_client.py 中的 API 端点和格式:")
        
        # 构建修复建议
        if working_format == "standard":
            logger.info("""
修改建议:
1. 在 tongyi_client.py 文件中，更新 _generate_text_dashscope 方法的 API URL:
   self.api_url = "{working_endpoint}"

2. 确保请求体格式如下:
   data = {{
       "model": self.model,
       "input": {{
           "messages": [{{role: "user", content: prompt}}]
       }},
       "parameters": {{
           "temperature": temperature,
           "max_tokens": max_tokens
       }}
   }}
""".format(working_endpoint=working_endpoint))
        else:
            logger.info("""
修改建议:
1. 在 tongyi_client.py 文件中，将默认的 use_openai_client 设置为 True
2. 确保 openai_client 的 base_url 设置为:
   base_url = "{working_endpoint}"
""".format(working_endpoint=working_endpoint))

        # 手动创建新的客户端进行测试
        try:
            client = TongyiClient(api_key=tongyi_api_key, use_openai_client=(working_format == "compatible"))
            # 覆盖API URL
            if working_format == "standard":
                client.api_url = working_endpoint
            else:
                # 如果是兼容模式，我们需要创建新的OpenAI客户端
                import openai
                client.client = openai.OpenAI(
                    api_key=tongyi_api_key,
                    base_url=working_endpoint.split("/compatible-mode")[0] + "/compatible-mode/v1"
                )
                
            logger.info("测试修复后的客户端...")
            
            # 异步测试，我们需要创建一个简单的异步环境
            import asyncio
            
            async def test_client():
                result = await client.generate_outline(requirement)
                return result
            
            result = asyncio.run(test_client())
            
            if "error" not in result:
                logger.info("修复后的客户端测试成功!")
                logger.info(f"大纲内容: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            else:
                logger.error(f"修复后的客户端测试失败: {result['error']}")
        except Exception as e:
            logger.error(f"修复后的客户端测试异常: {str(e)}")
    else:
        logger.error("所有API端点测试均失败，请检查API密钥是否正确或者查看通义千问官方文档获取最新的API端点")

if __name__ == "__main__":
    test_tongyi_api() 