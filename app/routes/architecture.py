from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Project, Requirement, ArchitectureCode
from app.utils import AIService
import json

architecture = Blueprint('architecture', __name__)

@architecture.route('/<int:project_id>')
@login_required
def architecture_page(project_id):
    """架构代码页面路由"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return "项目不存在或无权限访问", 404
    return render_template('architecture.html')

@architecture.route('/api/<int:project_id>', methods=['GET'])
@login_required
def get_architecture(project_id):
    """获取项目架构代码"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    architecture = ArchitectureCode.query.filter_by(project_id=project_id).first()
    
    if not architecture:
        return jsonify({
            'success': True,
            'message': '该项目尚未生成架构代码',
            'architecture': None
        })
    
    return jsonify({
        'success': True,
        'architecture': {
            'id': architecture.id,
            'code': architecture.code,
            'language': architecture.language,
            'architecture_type': architecture.architecture_type,
            'created_at': architecture.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@architecture.route('/api/<int:project_id>/generate', methods=['POST'])
@login_required
def generate_architecture(project_id):
    """生成架构代码"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    # 获取项目需求
    requirement = Requirement.query.filter_by(project_id=project_id).first()
    
    if not requirement:
        return jsonify({'success': False, 'message': '请先添加项目需求'}), 400
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    language = data.get('language')
    architecture_type = data.get('architecture_type')
    
    if not language or not architecture_type:
        return jsonify({'success': False, 'message': '请指定编程语言和架构类型'}), 400
    
    # 使用AI服务生成架构代码
    result = AIService.generate_architecture_code(requirement.content, language, architecture_type)
    
    if not result['success']:
        return jsonify({'success': False, 'message': '生成架构代码失败: ' + result.get('error', '未知错误')}), 500
    
    # 检查是否已经存在架构代码，如果存在则更新
    existing_architecture = ArchitectureCode.query.filter_by(project_id=project_id).first()
    
    if existing_architecture:
        existing_architecture.code = result['code']
        existing_architecture.language = language
        existing_architecture.architecture_type = architecture_type
        existing_architecture.api_response = json.dumps(str(result.get('raw_response', {})))
    else:
        # 创建新的架构代码
        architecture = ArchitectureCode(
            project_id=project_id,
            code=result['code'],
            language=language,
            architecture_type=architecture_type,
            api_response=json.dumps(str(result.get('raw_response', {})))
        )
        db.session.add(architecture)
    
    db.session.commit()
    
    # 返回生成的架构代码
    architecture = ArchitectureCode.query.filter_by(project_id=project_id).first()
    
    return jsonify({
        'success': True,
        'message': '架构代码生成成功',
        'architecture': {
            'id': architecture.id,
            'code': architecture.code,
            'language': architecture.language,
            'architecture_type': architecture.architecture_type
        }
    }) 