from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Project, ArchitectureCode, Deployment
from app.utils import AIService
import json

deployment = Blueprint('deployment', __name__)

@deployment.route('/<int:project_id>')
@login_required
def deployment_page(project_id):
    """部署页面路由"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return "项目不存在或无权限访问", 404
    return render_template('deployment.html')

@deployment.route('/api/<int:project_id>', methods=['GET'])
@login_required
def get_deployment(project_id):
    """获取项目部署信息"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    deployment = Deployment.query.filter_by(project_id=project_id).first()
    
    if not deployment:
        return jsonify({
            'success': True,
            'message': '该项目尚未配置部署',
            'deployment': None
        })
    
    return jsonify({
        'success': True,
        'deployment': {
            'id': deployment.id,
            'environment': deployment.environment,
            'status': deployment.status,
            'deploy_steps': deployment.deploy_steps,
            'log': deployment.log,
            'created_at': deployment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@deployment.route('/api/<int:project_id>/generate', methods=['POST'])
@login_required
def generate_deployment(project_id):
    """生成部署步骤"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    # 获取架构代码
    architecture = ArchitectureCode.query.filter_by(project_id=project_id).first()
    
    if not architecture:
        return jsonify({'success': False, 'message': '请先生成架构代码'}), 400
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    environment = data.get('environment')
    
    if not environment:
        return jsonify({'success': False, 'message': '请指定部署环境'}), 400
    
    # 使用AI服务生成部署步骤
    result = AIService.generate_deployment_steps(architecture.code)
    
    if not result['success']:
        return jsonify({'success': False, 'message': '生成部署步骤失败: ' + result.get('error', '未知错误')}), 500
    
    # 检查是否已经存在部署配置，如果存在则更新
    existing_deployment = Deployment.query.filter_by(project_id=project_id).first()
    
    if existing_deployment:
        existing_deployment.environment = environment
        existing_deployment.deploy_steps = result['deployment_steps']
        existing_deployment.status = '待部署'
    else:
        # 创建新的部署配置
        deployment = Deployment(
            project_id=project_id,
            environment=environment,
            deploy_steps=result['deployment_steps'],
            status='待部署',
            log=''
        )
        db.session.add(deployment)
    
    db.session.commit()
    
    # 返回生成的部署配置
    deployment = Deployment.query.filter_by(project_id=project_id).first()
    
    return jsonify({
        'success': True,
        'message': '部署步骤生成成功',
        'deployment': {
            'id': deployment.id,
            'environment': deployment.environment,
            'deploy_steps': deployment.deploy_steps,
            'status': deployment.status
        }
    })

@deployment.route('/api/<int:project_id>/execute', methods=['POST'])
@login_required
def execute_deployment(project_id):
    """执行部署（模拟）"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    deployment = Deployment.query.filter_by(project_id=project_id).first()
    
    if not deployment:
        return jsonify({'success': False, 'message': '请先生成部署步骤'}), 400
    
    if deployment.status == '部署中':
        return jsonify({'success': False, 'message': '部署已在进行中，请等待完成'}), 400
    
    # 模拟部署过程，实际中应该执行真实的部署命令
    import random
    import time
    
    # 模拟部署日志
    log = f"""
[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始部署到环境：{deployment.environment}
[{time.strftime('%Y-%m-%d %H:%M:%S')}] 执行环境准备...
[{time.strftime('%Y-%m-%d %H:%M:%S')}] 安装依赖项...
[{time.strftime('%Y-%m-%d %H:%M:%S')}] 构建项目...
[{time.strftime('%Y-%m-%d %H:%M:%S')}] 执行部署...
"""
    
    # 随机模拟成功或失败
    success = random.choice([True, True, True, False])  # 75%成功率
    
    if success:
        log += f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 部署成功！应用已在{deployment.environment}环境启动。"
        status = '已部署'
    else:
        log += f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误：部署失败。原因：模拟的随机错误。"
        status = '部署失败'
    
    deployment.log = log
    deployment.status = status
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '部署执行完成',
        'result': {
            'status': deployment.status,
            'log': deployment.log
        }
    })

@deployment.route('/api/<int:project_id>/update', methods=['PUT'])
@login_required
def update_deployment(project_id):
    """手动更新部署配置"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    # 检查是否已经存在部署配置，如果不存在则创建
    deployment = Deployment.query.filter_by(project_id=project_id).first()
    
    if not deployment:
        deployment = Deployment(
            project_id=project_id,
            environment='开发环境',
            status='待部署',
            deploy_steps='',
            log=''
        )
        db.session.add(deployment)
    
    # 更新部署信息
    if 'environment' in data:
        deployment.environment = data['environment']
    
    if 'deploy_steps' in data:
        deployment.deploy_steps = data['deploy_steps']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '部署配置更新成功',
        'deployment': {
            'id': deployment.id,
            'environment': deployment.environment,
            'deploy_steps': deployment.deploy_steps,
            'status': deployment.status
        }
    }) 