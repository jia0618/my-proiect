import sys
import os
import asyncio
import json

# 添加项目根目录到Python路径，以便导入项目模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入项目模块
from tongyi_client import TongyiClient
from api_config import get_api_config

async def test_tongyi_outline():
    """测试通义千问客户端的大纲生成功能"""
    # 获取API配置
    config = get_api_config()
    tongyi_api_key = config.get("tongyi_api_key")
    
    print(f"使用通义千问API密钥: {tongyi_api_key[:5]}...{tongyi_api_key[-4:]}")
    
    # 创建通义千问客户端
    # 设置use_openai_client=True使用兼容模式API
    client = TongyiClient(api_key=tongyi_api_key, use_openai_client=True)
    
    # 测试需求
    requirement = """
    开发一个在线购物系统，实现商品浏览、购物车、订单管理和支付功能。
    系统需要支持用户注册、登录，商品分类和搜索，订单跟踪等功能。
    """
    
    print("开始测试生成架构大纲...")
    
    # 调用generate_outline方法生成大纲
    try:
        result = await client.generate_outline(requirement)
        
        if "error" in result:
            print(f"生成大纲失败: {result['error']}")
        else:
            print("生成大纲成功!")
            if "parsed_outline" in result:
                print(f"\n大纲内容:\n{json.dumps(result['parsed_outline'], ensure_ascii=False, indent=2)}")
            else:
                print(f"\n大纲原始文本:\n{result['outline_text'][:500]}...")
    except Exception as e:
        print(f"发生异常: {str(e)}")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_tongyi_outline()) 