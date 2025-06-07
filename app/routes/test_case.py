from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Project, ModuleCode, TestCase, ArchitectureCode
from app.utils import AIService
import json
from datetime import datetime

test_case = Blueprint('test_case', __name__)

@test_case.route('/<int:project_id>')
@login_required
def test_page(project_id):
    """测试用例页面路由"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return "项目不存在或无权限访问", 404
    return render_template('testcase.html')

@test_case.route('/api/<int:project_id>', methods=['GET'])
@login_required
def get_test_cases(project_id):
    """获取项目测试用例列表"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    test_cases = TestCase.query.filter_by(project_id=project_id).all()
    test_cases_data = []
    
    for tc in test_cases:
        test_cases_data.append({
            'id': tc.id,
            'test_name': tc.test_name,
            'test_type': tc.test_type,
            'test_content': tc.test_content,  # 返回完整的测试内容，不限制长度
            'test_result': tc.test_result,
            'created_at': tc.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'success': True,
        'test_cases': test_cases_data
    })

@test_case.route('/api/<int:test_id>/detail', methods=['GET'])
@login_required
def get_test_detail(test_id):
    """获取测试用例详情"""
    test_case = TestCase.query.get(test_id)
    
    if not test_case:
        return jsonify({'success': False, 'message': '测试用例不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=test_case.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该测试用例'}), 403
    
    return jsonify({
        'success': True,
        'test_case': {
            'id': test_case.id,
            'test_name': test_case.test_name,
            'test_type': test_case.test_type,
            'test_content': test_case.test_content,
            'expected_result': test_case.expected_result,
            'test_result': test_case.test_result,
            'created_at': test_case.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@test_case.route('/api/<int:project_id>/generate', methods=['POST'])
@login_required
def generate_test_case(project_id):
    """生成测试用例"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    test_name = data.get('test_name')
    test_type = data.get('test_type')
    module_id = data.get('module_id')  # 模块ID变为可选参数
    test_count = data.get('test_count', 3)  # 默认生成3个测试用例
    
    if not test_name or not test_type:
        return jsonify({'success': False, 'message': '请指定测试名称和类型'}), 400
    
    # 测试代码内容，如果提供了模块ID则使用对应模块的代码，否则使用默认测试代码
    test_code = None
    
    if module_id:
        # 获取模块代码
        module = ModuleCode.query.filter_by(id=module_id, project_id=project_id).first()
        
        if not module:
            return jsonify({'success': False, 'message': '指定的模块不存在或不属于当前项目'}), 404
        
        test_code = module.code
    else:
        # 获取项目的架构代码，用于生成通用测试用例
        architecture = ArchitectureCode.query.filter_by(project_id=project_id).first()
        if architecture:
            test_code = architecture.code
        else:
            # 使用默认测试代码模板
            test_code = f"""
            // 这是一个通用的{test_type}测试代码模板
            // 软件项目: {project.name}
            // 测试类型: {test_type}
            // 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            public class TestSuite {{{{
                // 测试方法
                public void testFeature() {{{{
                    // 测试逻辑
                }}}}
            }}}}
            """
    
    # 使用AI服务生成测试用例
    result = AIService.generate_test_cases(test_code, test_type, test_count)
    
    if not result['success']:
        return jsonify({'success': False, 'message': '生成测试用例失败: ' + result.get('error', '未知错误')}), 500
    
    # 创建多个测试用例
    generated_test_cases = []
    
    for i in range(min(test_count, len(result['test_cases']) if isinstance(result['test_cases'], list) else 1)):
        if isinstance(result['test_cases'], list):
            test_content = result['test_cases'][i]
        else:
            test_content = result['test_cases']
        
        # 确保测试内容是有效的JSON格式
        if isinstance(test_content, dict):
            # 已经是字典格式，确保包含必要的字段
            if 'steps' not in test_content:
                test_content['steps'] = ["步骤1: 准备测试环境", "步骤2: 执行测试操作", "步骤3: 验证测试结果"]
            if 'name' not in test_content:
                test_content['name'] = f"{test_name}_{i+1}"
            if 'purpose' not in test_content:
                test_content['purpose'] = f"测试{test_type}功能"
            if 'expected_result' not in test_content:
                test_content['expected_result'] = "测试通过，符合预期"
                
            # 转换为JSON字符串
            test_content_json = json.dumps(test_content, ensure_ascii=False)
        else:
            # 尝试从文本中提取JSON
            try:
                # 如果是字符串，尝试解析为JSON
                import re
                json_pattern = r'\{.*\}'
                json_match = re.search(json_pattern, test_content, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(0)
                    parsed_content = json.loads(json_str)
                    
                    # 确保包含必要的字段
                    if 'steps' not in parsed_content:
                        parsed_content['steps'] = ["步骤1: 准备测试环境", "步骤2: 执行测试操作", "步骤3: 验证测试结果"]
                    if 'name' not in parsed_content:
                        parsed_content['name'] = f"{test_name}_{i+1}"
                    if 'purpose' not in parsed_content:
                        parsed_content['purpose'] = f"测试{test_type}功能"
                    if 'expected_result' not in parsed_content:
                        parsed_content['expected_result'] = "测试通过，符合预期"
                    
                    test_content_json = json.dumps(parsed_content, ensure_ascii=False)
                else:
                    # 创建默认的测试用例对象
                    default_test = {
                        'name': f"{test_name}_{i+1}",
                        'purpose': f"测试{test_type}功能",
                        'steps': ["步骤1: 准备测试环境", "步骤2: 执行测试操作", "步骤3: 验证测试结果"],
                        'expected_result': "测试通过，符合预期"
                    }
                    test_content_json = json.dumps(default_test, ensure_ascii=False)
            except Exception as e:
                print(f"解析测试内容失败: {e}")
                # 创建默认的测试用例对象
                default_test = {
                    'name': f"{test_name}_{i+1}",
                    'purpose': f"测试{test_type}功能",
                    'steps': ["步骤1: 准备测试环境", "步骤2: 执行测试操作", "步骤3: 验证测试结果"],
                    'expected_result': "测试通过，符合预期"
                }
                test_content_json = json.dumps(default_test, ensure_ascii=False)
            
        test_case = TestCase(
            project_id=project_id,
            test_name=f"{test_name}_{i+1}",
            test_type=test_type,
            test_content=test_content_json,
            expected_result='',
            test_result='待执行',
            api_response=json.dumps(str(result.get('raw_response', {})))
        )
        db.session.add(test_case)
        generated_test_cases.append({
            'test_name': test_case.test_name,
            'test_type': test_case.test_type,
            'test_content': test_case.test_content
        })
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'成功生成{len(generated_test_cases)}个测试用例',
        'test_cases': generated_test_cases
    })

@test_case.route('/api/<int:test_id>/update', methods=['PUT'])
@login_required
def update_test_case(test_id):
    """更新测试用例"""
    test_case = TestCase.query.get(test_id)
    
    if not test_case:
        return jsonify({'success': False, 'message': '测试用例不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=test_case.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该测试用例'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    # 更新测试用例信息
    if 'test_name' in data:
        test_case.test_name = data['test_name']
    
    if 'test_content' in data:
        test_case.test_content = data['test_content']
        
    if 'expected_result' in data:
        test_case.expected_result = data['expected_result']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '测试用例更新成功',
        'test_case': {
            'id': test_case.id,
            'test_name': test_case.test_name,
            'test_type': test_case.test_type,
            'test_content': test_case.test_content,
            'expected_result': test_case.expected_result
        }
    })

@test_case.route('/api/<int:test_id>/execute', methods=['POST'])
@login_required
def execute_test_case(test_id):
    """执行测试用例（模拟）"""
    test_case = TestCase.query.get(test_id)
    
    if not test_case:
        return jsonify({'success': False, 'message': '测试用例不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=test_case.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该测试用例'}), 403
    
    # 模拟测试执行结果，实际中应该运行测试并获取结果
    import random
    result = random.choice(['通过', '失败'])
    
    test_case.test_result = result
    
    # 添加错误信息
    error_message = ""
    if result == '失败':
        # 生成随机的错误信息作为示例
        error_messages = [
            "验证失败：预期结果与实际结果不匹配",
            "接口返回超时",
            "数据库连接失败",
            "权限验证失败",
            "数据格式错误"
        ]
        error_message = random.choice(error_messages)
        
        # 将错误信息更新到测试内容中
        try:
            content = json.loads(test_case.test_content)
            content['error_message'] = error_message
            test_case.test_content = json.dumps(content, ensure_ascii=False)
        except Exception as e:
            # 如果无法解析JSON，则创建一个新的
            print(f"更新测试内容失败: {e}")
            test_case.test_content = json.dumps({
                'name': test_case.test_name,
                'result': result,
                'error_message': error_message
            }, ensure_ascii=False)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '测试用例执行完成',
        'result': {
            'test_result': test_case.test_result,
            'error_message': error_message
        }
    })

@test_case.route('/api/<int:test_id>', methods=['DELETE'])
@login_required
def delete_test_case(test_id):
    """删除测试用例"""
    test_case = TestCase.query.get(test_id)
    
    if not test_case:
        return jsonify({'success': False, 'message': '测试用例不存在'}), 404
    
    # 验证权限
    project = Project.query.filter_by(id=test_case.project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'success': False, 'message': '无权限访问该测试用例'}), 403
    
    db.session.delete(test_case)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '测试用例删除成功'
    }) 