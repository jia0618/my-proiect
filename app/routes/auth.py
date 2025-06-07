from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET'])
def login_page():
    """登录页面路由"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')

@auth.route('/api/login', methods=['POST'])
def login():
    """处理登录请求的API"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user is None or not user.verify_password(password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    # 登录用户
    login_user(user)
    
    # 生成简单的token (实际项目中应使用更复杂的JWT)
    import hashlib
    token = hashlib.md5((str(user.id) + user.username + str(user.created_at)).encode()).hexdigest()
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })

@auth.route('/api/logout')
@login_required
def logout():
    """处理登出请求的API"""
    logout_user()
    return jsonify({'success': True, 'message': '登出成功'})

@auth.route('/api/register', methods=['POST'])
def register():
    """处理注册请求的API"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    if email and User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
    
    # 创建新用户
    user = User(username=username, email=email)
    user.password = password  # 设置密码（会自动哈希）
    
    db.session.add(user)
    db.session.commit()
    
    # 登录新用户
    login_user(user)
    
    return jsonify({
        'success': True,
        'message': '注册成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }) 