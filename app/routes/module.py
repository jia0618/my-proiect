from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Project, Requirement, ArchitectureCode, ModuleCode
from app.utils import AIService
import json

module = Blueprint('module', __name__)

@module.route('/<int:project_id>')
@login_required
def module_page(project_id):
    """模块代码页面路由"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return "项目不存在或无权限访问", 404
    return render_template('module.html')

@module.route('/api/<int:project_id>', methods=['GET'])
@login_required
def get_modules(project_id):
    """获取项目模块代码列表"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    modules = ModuleCode.query.filter_by(project_id=project_id).all()
    modules_data = []
    
    for mod in modules:
        modules_data.append({
            'id': mod.id,
            'module_name': mod.module_name,
            'module_type': mod.module_type,
            'created_at': mod.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'success': True,
        'modules': modules_data
    })

@module.route('/api/<int:module_id>/detail', methods=['GET'])
@login_required
def get_module_detail(module_id):
    """获取模块代码详情"""
    module = ModuleCode.query.get(module_id)
    
    if not module:
        return jsonify({'success': False, 'message': '模块不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=module.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该模块'}), 403
    
    return jsonify({
        'success': True,
        'module': {
            'id': module.id,
            'module_name': module.module_name,
            'module_type': module.module_type,
            'code': module.code,
            'dependencies': module.dependencies,
            'created_at': module.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@module.route('/api/<int:project_id>/generate', methods=['POST'])
@login_required
def generate_module(project_id):
    """生成模块代码"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    # 获取项目需求和架构代码
    requirement = Requirement.query.filter_by(project_id=project_id).first()
    architecture = ArchitectureCode.query.filter_by(project_id=project_id).first()
    
    if not requirement:
        return jsonify({'success': False, 'message': '请先添加项目需求'}), 400
    
    if not architecture:
        return jsonify({'success': False, 'message': '请先生成架构代码'}), 400
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    module_name = data.get('module_name')
    module_type = data.get('module_type')
    dependencies = data.get('dependencies', '')
    language = data.get('language', '')  # 获取编程语言参数
    
    if not module_name or not module_type:
        return jsonify({'success': False, 'message': '请指定模块名称和类型'}), 400
    
    # 记录请求信息
    print(f"生成模块代码请求：项目ID={project_id}, 模块名称={module_name}, 模块类型={module_type}, 语言={language}")
    
    # 使用AI服务生成模块代码
    result = AIService.generate_module_code(requirement.content, architecture.code, module_type)
    
    if not result['success']:
        return jsonify({'success': False, 'message': '生成模块代码失败: ' + result.get('error', '未知错误')}), 500
    
    # 创建新的模块代码
    module = ModuleCode(
        project_id=project_id,
        module_name=module_name,
        code=result['code'],
        module_type=module_type,
        dependencies=dependencies,
        language=language,  # 保存语言信息
        api_response=json.dumps(str(result.get('raw_response', {})))
    )
    db.session.add(module)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '模块代码生成成功',
        'module': {
            'id': module.id,
            'module_name': module.module_name,
            'module_type': module.module_type,
            'language': module.language,  # 返回语言信息
            'code': module.code
        }
    })

@module.route('/api/<int:module_id>', methods=['PUT'])
@login_required
def update_module(module_id):
    """更新模块代码"""
    module = ModuleCode.query.get(module_id)
    
    if not module:
        return jsonify({'success': False, 'message': '模块不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=module.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该模块'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    # 更新模块信息
    if 'module_name' in data:
        module.module_name = data['module_name']
    
    if 'code' in data:
        module.code = data['code']
        
    if 'dependencies' in data:
        module.dependencies = data['dependencies']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '模块更新成功',
        'module': {
            'id': module.id,
            'module_name': module.module_name,
            'module_type': module.module_type,
            'code': module.code
        }
    })

@module.route('/api/<int:module_id>', methods=['DELETE'])
@login_required
def delete_module(module_id):
    """删除模块"""
    module = ModuleCode.query.get(module_id)
    
    if not module:
        return jsonify({'success': False, 'message': '模块不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=module.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该模块'}), 403
    
    db.session.delete(module)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '模块删除成功'
    }) 