"""
数据库迁移工具辅助脚本
用于初始化数据库、创建表和应用迁移
"""
import os
import click
from flask_migrate import Migrate, init, migrate, upgrade
from app import create_app, db
from app.models import User, Project, Requirement, ArchitectureCode, DatabaseDesign, ModuleCode, TestCase, Deployment
from werkzeug.security import generate_password_hash

app = create_app()
migrate = Migrate(app, db)

@click.group()
def cli():
    """数据库迁移和初始化命令工具"""
    pass

@cli.command('init-db')
def init_db():
    """初始化数据库并创建表"""
    with app.app_context():
        db.create_all()
        click.echo('数据库表创建成功!')

@cli.command('create-admin')
@click.option('--username', default='admin', help='管理员用户名')
@click.option('--password', default='admin', help='管理员密码')
@click.option('--email', default='admin@example.com', help='管理员邮箱')
def create_admin(username, password, email):
    """创建管理员账户"""
    with app.app_context():
        admin = User.query.filter_by(username=username).first()
        if admin:
            click.echo(f'管理员 {username} 已存在!')
            return
            
        admin = User(
            username=username,
            email=email
        )
        admin.password = password
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f'管理员 {username} 创建成功!')

@cli.command('apply-migrations')
def apply_migrations():
    """应用数据库迁移"""
    with app.app_context():
        # 初始化迁移仓库
        try:
            init()
            click.echo('迁移仓库初始化成功!')
        except:
            click.echo('迁移仓库已存在，跳过初始化')
        
        # 创建迁移
        migrate(message='自动生成迁移')
        click.echo('数据库迁移创建成功!')
        
        # 应用迁移
        upgrade()
        click.echo('数据库迁移应用成功!')

@cli.command('update-schema')
def update_schema():
    """更新数据库表结构（添加新字段）"""
    with app.app_context():
        try:
            # 对接现有数据库，添加缺少的表和字段
            db.engine.execute("""
            -- 修改requirements表，添加缺失字段
            ALTER TABLE requirements 
            ADD COLUMN requirement_type VARCHAR(50) NULL,
            ADD COLUMN priority INT NULL;
            """)
            click.echo('requirements表更新成功!')
        except Exception as e:
            click.echo(f'requirements表更新失败或已经更新: {str(e)}')

        try:
            # 添加module_codes表的dependencies字段
            db.engine.execute("""
            ALTER TABLE module_codes 
            ADD COLUMN dependencies TEXT NULL;
            """)
            click.echo('module_codes表更新成功!')
        except Exception as e:
            click.echo(f'module_codes表更新失败或已经更新: {str(e)}')

        try:
            # 确保users表的password_hash字段名称正确
            db.engine.execute("""
            ALTER TABLE users 
            CHANGE COLUMN password password_hash VARCHAR(255) NOT NULL;
            """)
            click.echo('users表更新成功!')
        except Exception as e:
            click.echo(f'users表更新失败或已经更新: {str(e)}')

if __name__ == '__main__':
    cli() 