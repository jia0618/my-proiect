import requests
import json
import os
import sys
import logging

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('TongyiAPITest')

# 尝试从环境变量或指定位置获取API密钥
def get_tongyi_api_key():
    # 首先尝试从环境变量获取
    api_key = os.environ.get("TONGYI_API_KEY")
    if api_key:
        return api_key
    
    # 如果环境变量不存在，尝试从配置文件获取
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        api_key = config.get('API', 'tongyi_api_key', fallback=None)
        if api_key:
            return api_key
    except:
        pass
    
    # 硬编码的默认API密钥（仅用于测试）
    return "sk-1c44c33a881a43d98639c5993ce98164"

# 测试通义千问的标准API
def test_standard_api(api_key, requirement):
    logger.info("测试通义千问标准API (DashScope)")
    
    # v1 API端点
    url_v1 = "https://dashscope.aliyuncs.com/v1/services/aigc/text-generation/generation"
    
    # v2 API端点
    url_v2 = "https://dashscope.aliyuncs.com/v2/services/aigc/text-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
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
    
    data = {
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
    
    # 测试 v1 API
    try:
        logger.info("尝试通义千问 v1 API")
        response_v1 = requests.post(url_v1, headers=headers, json=data, timeout=120)
        logger.info(f"v1 API状态码: {response_v1.status_code}")
        
        if response_v1.status_code == 200:
            logger.info("v1 API调用成功！")
            logger.info(f"响应内容: {response_v1.text[:200]}...")
            return response_v1.json()
        else:
            logger.error(f"v1 API调用失败: {response_v1.text}")
    except Exception as e:
        logger.error(f"v1 API调用异常: {str(e)}")
    
    # 如果v1失败，测试v2 API
    try:
        logger.info("尝试通义千问 v2 API")
        response_v2 = requests.post(url_v2, headers=headers, json=data, timeout=120)
        logger.info(f"v2 API状态码: {response_v2.status_code}")
        
        if response_v2.status_code == 200:
            logger.info("v2 API调用成功！")
            logger.info(f"响应内容: {response_v2.text[:200]}...")
            return response_v2.json()
        else:
            logger.error(f"v2 API调用失败: {response_v2.text}")
    except Exception as e:
        logger.error(f"v2 API调用异常: {str(e)}")
    
    return None

# 测试通义千问的兼容模式API
def test_compatible_api(api_key, requirement):
    logger.info("测试通义千问兼容模式API")
    
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
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
    
    data = {
        "model": "qwen-max",
        "messages": [
            {"role": "system", "content": "你是一位专业的软件架构师，擅长设计符合需求的软件架构大纲。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        logger.info("尝试通义千问兼容模式API")
        response = requests.post(url, headers=headers, json=data, timeout=120)
        logger.info(f"兼容模式API状态码: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("兼容模式API调用成功！")
            logger.info(f"响应内容: {response.text[:200]}...")
            return response.json()
        else:
            logger.error(f"兼容模式API调用失败: {response.text}")
    except Exception as e:
        logger.error(f"兼容模式API调用异常: {str(e)}")
    
    return None

# 测试最新版本的DashScope API（可能是最新推荐的方式）
def test_latest_api(api_key, requirement):
    logger.info("测试通义千问最新API")
    
    # 最新的API可能已经更新，这里尝试不同的可能端点
    urls = [
        "https://api.dashscope.aliyuncs.com/v1/models/qwen-max/invoke",
        "https://api.dashscope.aliyuncs.com/v1/services/aigc/text-generation/generation"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
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
    
    # 尝试不同的API请求格式
    payloads = [
        {
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
        },
        {
            "input": prompt,
            "model": "qwen-max",
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.8,
                "max_tokens": 2000
            }
        }
    ]
    
    for url in urls:
        for payload in payloads:
            try:
                logger.info(f"尝试API端点: {url}")
                logger.info(f"使用请求体格式: {json.dumps(payload)[:100]}...")
                
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                logger.info(f"API状态码: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info("API调用成功！")
                    logger.info(f"响应内容: {response.text[:200]}...")
                    return response.json()
                else:
                    logger.error(f"API调用失败: {response.text}")
            except Exception as e:
                logger.error(f"API调用异常: {str(e)}")
    
    return None

def main():
    # 获取API密钥
    api_key = get_tongyi_api_key()
    if not api_key:
        logger.error("未找到通义千问API密钥")
        return
    
    logger.info(f"使用通义千问API密钥: {api_key[:5]}...{api_key[-4:]}")
    
    # 测试的需求文本
    requirement = """
    开发一个在线购物系统，实现商品浏览、购物车、订单管理和支付功能。
    系统需要支持用户注册、登录，商品分类和搜索，订单跟踪等功能。
    """
    
    # 测试标准API
    result = test_standard_api(api_key, requirement)
    if result:
        logger.info("标准API调用成功")
        return
    
    # 如果标准API失败，测试兼容模式API
    result = test_compatible_api(api_key, requirement)
    if result:
        logger.info("兼容模式API调用成功")
        return
    
    # 如果兼容模式API也失败，尝试最新API
    result = test_latest_api(api_key, requirement)
    if result:
        logger.info("最新API调用成功")
        return
    
    logger.error("所有API调用方式均失败")

if __name__ == "__main__":
    main() 