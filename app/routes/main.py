from flask import Blueprint, render_template, redirect, url_for, session, current_app
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """首页路由"""
    # 打印调试信息
    print(f"首页访问 - 用户认证状态: {current_user.is_authenticated}")
    if not current_user.is_authenticated:
        print("用户未登录，重定向到登录页面")
        return redirect(url_for('auth.login_page'))
    return render_template('index.html')

@main.route('/index.html')
def index_html():
    """首页HTML路由"""
    print(f"index.html访问 - 用户认证状态: {current_user.is_authenticated}")
    if not current_user.is_authenticated:
        print("用户未登录，重定向到登录页面")
        return redirect(url_for('auth.login_page'))
    return render_template('index.html')

@main.route('/project/new')
@login_required
def new_project():
    """新建项目页面路由"""
    return render_template('project_new.html') 