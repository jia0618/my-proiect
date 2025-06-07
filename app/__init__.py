from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建数据库实例
db = SQLAlchemy()
# 创建登录管理实例
login_manager = LoginManager()

def create_app():
    # 创建Flask应用实例
    app = Flask(__name__, 
                static_folder='../web',  # 静态文件指向前端代码
                static_url_path='',      # 静态文件URL前缀设置为空
                template_folder='../web')  # 模板指向前端代码
    
    # 配置应用
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    # 从环境变量中读取数据库URL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/ai_software_platform')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 会话配置
    app.config['SESSION_COOKIE_NAME'] = 'ai_software_platform'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 会话有效期24小时
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 设置登录相关配置
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = '请先登录'
    login_manager.session_protection = 'strong'
    
    # 由于是同域应用，不需要CORS
    # CORS(app)
    
    # 注册蓝图
    from app.routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.routes.project import project as project_blueprint
    app.register_blueprint(project_blueprint, url_prefix='/project')
    
    from app.routes.requirement import requirement as requirement_blueprint
    app.register_blueprint(requirement_blueprint, url_prefix='/requirement')
    
    from app.routes.architecture import architecture as architecture_blueprint
    app.register_blueprint(architecture_blueprint, url_prefix='/architecture')
    
    from app.routes.database_design import database_design as database_design_blueprint
    app.register_blueprint(database_design_blueprint, url_prefix='/database')
    
    from app.routes.module import module as module_blueprint
    app.register_blueprint(module_blueprint, url_prefix='/module')
    
    from app.routes.test_case import test_case as test_case_blueprint
    app.register_blueprint(test_case_blueprint, url_prefix='/test')
    
    from app.routes.deployment import deployment as deployment_blueprint
    app.register_blueprint(deployment_blueprint, url_prefix='/deployment')
    
    from app.routes.system_config import system_config as system_config_blueprint
    app.register_blueprint(system_config_blueprint, url_prefix='/system')
    
    return app 