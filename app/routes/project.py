from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Project

project = Blueprint('project', __name__)

@project.route('/api/list', methods=['GET'])
@login_required
def get_projects():
    """获取当前用户所有项目"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    projects_data = []
    
    for proj in projects:
        projects_data.append({
            'id': proj.id,
            'name': proj.name,
            'description': proj.description,
            'created_at': proj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'success': True,
        'projects': projects_data
    })

@project.route('/api/create', methods=['POST'])
@login_required
def create_project():
    """创建新项目"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    name = data.get('name')
    description = data.get('description')
    
    if not name:
        return jsonify({'success': False, 'message': '项目名称不能为空'}), 400
    
    # 创建项目
    project = Project(
        name=name,
        description=description,
        user_id=current_user.id
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '项目创建成功',
        'project': {
            'id': project.id,
            'name': project.name,
            'description': project.description
        }
    })

@project.route('/api/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """获取项目详情"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    return jsonify({
        'success': True,
        'project': {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': project.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@project.route('/api/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """更新项目信息"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    # 更新项目信息
    if 'name' in data:
        project.name = data['name']
    
    if 'description' in data:
        project.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '项目更新成功',
        'project': {
            'id': project.id,
            'name': project.name,
            'description': project.description
        }
    })

@project.route('/api/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """删除项目"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '项目删除成功'
    }) 