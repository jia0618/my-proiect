import os
import dotenv
from typing import Dict, Any

# 尝试加载.env文件（如果存在）
dotenv.load_dotenv()

# API密钥（如果.env文件不存在或未包含这些变量，使用默认值）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-8612f8702df64fd3b2c66f7486ce5845")
TONGYI_API_KEY = os.environ.get("TONGYI_API_KEY", "sk-1c44c33a881a43d98639c5993ce98164")
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", TONGYI_API_KEY)  # 兼容DashScope调用

# 设置环境变量（如果尚未设置）
if "DEEPSEEK_API_KEY" not in os.environ:
    os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY
if "TONGYI_API_KEY" not in os.environ:
    os.environ["TONGYI_API_KEY"] = TONGYI_API_KEY
if "DASHSCOPE_API_KEY" not in os.environ:
    os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

def get_api_config() -> Dict[str, str]:
    """获取API配置"""
    return {
        "deepseek_api_key": DEEPSEEK_API_KEY,
        "tongyi_api_key": TONGYI_API_KEY,
        "dashscope_api_key": DASHSCOPE_API_KEY
    }

def get_openai_client_config() -> Dict[str, Any]:
    """获取OpenAI客户端配置"""
    return {
        "api_key": DASHSCOPE_API_KEY,
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }

def get_available_models() -> Dict[str, str]:
    """获取可用的模型列表"""
    return {
        "deepseek": "deepseek-chat",#提供模型标识符
        "tongyi": "qwen-max",
        "tongyi_openai": "qwen-max-latest"  # 使用OpenAI兼容接口的模型
    }

if __name__ == "__main__":
    # 测试配置是否正确加载
    config = get_api_config()
    for key, value in config.items():
        # 仅显示密钥的前10个字符和后4个字符，中间用***替代
        masked_value = value[:10] + "***" + value[-4:] if value else "未设置"
        print(f"{key}: {masked_value}")
    
    print("\n可用模型:")
    for name, model in get_available_models().items():
        print(f"{name}: {model}") 