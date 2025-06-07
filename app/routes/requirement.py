from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Project, Requirement

requirement = Blueprint('requirement', __name__)

@requirement.route('/<int:project_id>')
@login_required
def requirement_page(project_id):
    """需求页面路由"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return "项目不存在或无权限访问", 404
    return render_template('requirement.html')

@requirement.route('/api/<int:project_id>', methods=['GET'])
@login_required
def get_requirements(project_id):
    """获取项目需求"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    requirements = Requirement.query.filter_by(project_id=project_id).all()
    requirements_data = []
    
    for req in requirements:
        requirements_data.append({
            'id': req.id,
            'content': req.content,
            'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'success': True,
        'requirements': requirements_data
    })

@requirement.route('/api/<int:project_id>/create', methods=['POST'])
@login_required
def create_requirement(project_id):
    """创建需求"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    content = data.get('content')
    
    if not content:
        return jsonify({'success': False, 'message': '需求内容不能为空'}), 400
    
    # 创建需求
    requirement = Requirement(
        project_id=project_id,
        content=content
    )
    
    db.session.add(requirement)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '需求创建成功',
        'requirement': {
            'id': requirement.id,
            'content': requirement.content
        }
    })

@requirement.route('/api/<int:requirement_id>', methods=['PUT'])
@login_required
def update_requirement(requirement_id):
    """更新需求"""
    requirement = Requirement.query.get(requirement_id)
    
    if not requirement:
        return jsonify({'success': False, 'message': '需求不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=requirement.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该需求'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    # 更新需求信息
    if 'content' in data:
        requirement.content = data['content']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '需求更新成功',
        'requirement': {
            'id': requirement.id,
            'content': requirement.content
        }
    })

@requirement.route('/api/<int:requirement_id>', methods=['DELETE'])
@login_required
def delete_requirement(requirement_id):
    """删除需求"""
    requirement = Requirement.query.get(requirement_id)
    
    if not requirement:
        return jsonify({'success': False, 'message': '需求不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=requirement.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该需求'}), 403
    
    db.session.delete(requirement)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '需求删除成功'
    }) 