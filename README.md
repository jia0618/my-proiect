# AI软件管理平台

基于DeepSeek和通义前问大模型的软件需求分析与代码生成工具，支持从需求文档到系统架构、数据库脚本和代码的自动生成。

## 功能特点

1. **系统架构大纲生成**：基于通义千问模型，从需求文档生成系统架构大纲
2. **代码生成**：基于DeepSeek模型，生成各模块代码实现
3. **数据库设计**：自动生成MySQL数据库脚本
4. **测试用例生成**：根据需求和代码生成测试用例
5. **部署指南生成**：自动生成系统部署文档

```bash

```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 创建.env文件并设置API密钥

```
DEEPSEEK_API_KEY=your_deepseek_api_key
TONGYI_API_KEY=your_tongyi_api_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ai_platform
DB_PORT=3306
```

4. 创建数据库

```sql
CREATE DATABASE ai_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 使用方法

### 命令行使用

```bash
python main.py -r path/to/requirement.md -p "项目名称" -o ./output
```

参数说明：

- `-r, --requirement`：需求文档路径（必需）
- `-p, --project_name`：项目名称（默认为"新项目"）
- `-o, --output`：输出目录（默认为"./output"）
- `--deepseek_key`：DeepSeek API密钥（可选，优先使用环境变量）
- `--tongyi_key`：通义前问API密钥（可选，优先使用环境变量）

### 编程接口使用

```python
import asyncio
from main import AIModelPlatform

async def process_project():
    platform = AIModelPlatform()
    result = await platform.process_requirement("我的项目", "requirement.md")
    print(f"项目ID: {result['project_id']}")
    platform.export_results(result["project_id"], "./output")

if __name__ == "__main__":
    asyncio.run(process_project())
```

## 输出文件

处理完成后，输出目录将包含：

- `requirement.md`：原始需求文档
- `outline.json`：系统架构大纲
- `database.sql`：数据库脚本
- `code/`：生成的代码文件
