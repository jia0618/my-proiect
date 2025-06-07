from app import create_app, db
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import sys

# 加载环境变量
load_dotenv()

app = create_app()

# 确保在app上下文中创建和初始化migrate对象
with app.app_context():
    migrate = Migrate(app, db)

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    # 获取命令行参数
    args = sys.argv[1:]
    use_reloader = False  # 默认禁用自动重载
    
    # 如果传入了--with-reload参数，则启用自动重载（用于开发调试）
    if '--with-reload' in args:
        use_reloader = True
        args.remove('--with-reload')
    
    # 设置忽略的文件类型和目录
    ignored_dirs = ['__pycache__', '.git', 'migrations', 'venv', 'env']
    ignored_files = ['.pyc', '.pyo', '.pyd', '.git', '.env', '.flaskenv', '.DS_Store']
    
    # 运行应用，禁用自动重载
    app.run(
        debug=True,
        use_reloader=use_reloader,  # 默认禁用自动重载
        threaded=True,
        host='127.0.0.1',
        port=5000
    ) 