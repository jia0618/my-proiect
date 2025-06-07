from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Project, Requirement, DatabaseDesign
from app.utils import AIService
import json

database_design = Blueprint('database_design', __name__)

@database_design.route('/<int:project_id>')
@login_required
def database_page(project_id):
    """数据库设计页面路由"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        return "项目不存在或无权限访问", 404
    return render_template('database.html')

@database_design.route('/api/<int:project_id>', methods=['GET'])
@login_required
def get_database_design(project_id):
    """获取项目数据库设计"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    database_design = DatabaseDesign.query.filter_by(project_id=project_id).first()
    
    if not database_design:
        return jsonify({
            'success': True,
            'message': '该项目尚未生成数据库设计',
            'database_design': None
        })
    
    return jsonify({
        'success': True,
        'database_design': {
            'id': database_design.id,
            'script': database_design.script,
            'tables': database_design.tables,
            'relationships': database_design.relationships,
            'created_at': database_design.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@database_design.route('/api/<int:project_id>/generate', methods=['POST'])
@login_required
def generate_database_design(project_id):
    """生成数据库设计"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    # 获取项目需求
    requirement = Requirement.query.filter_by(project_id=project_id).first()
    
    if not requirement:
        return jsonify({'success': False, 'message': '请先添加项目需求'}), 400
    
    # 使用AI服务生成数据库设计
    result = AIService.generate_database_design(requirement.content)
    
    if not result['success']:
        return jsonify({'success': False, 'message': '生成数据库设计失败: ' + result.get('error', '未知错误')}), 500
    
    design_text = result['design']
    
    # 尝试解析设计文本，提取表结构和关系
    try:
        # 初始化处理结果
        tables = ""
        relationships = ""
        script = ""
        
        # 记录处理步骤，方便调试
        print(f"开始处理数据库设计文本，长度: {len(design_text)}")
        
        # 提取SQL脚本 - 检查代码块
        sql_pattern_found = False
        sql_patterns = ["```sql", "```mysql", "```SQL", "```MySQL"]
        for pattern in sql_patterns:
            if pattern in design_text:
                sql_pattern_found = True
                print(f"找到SQL代码块标记: {pattern}")
                sql_start = design_text.find(pattern)
                sql_end = design_text.find("```", sql_start + len(pattern))
                if sql_start != -1 and sql_end != -1:
                    script = design_text[sql_start + len(pattern):sql_end].strip()
                    print(f"提取到SQL脚本，长度: {len(script)}")
                    break
        
        # 如果没有找到代码块，但内容包含CREATE TABLE，尝试直接提取
        if not sql_pattern_found and "CREATE TABLE" in design_text:
            print("未找到SQL代码块，但发现CREATE TABLE语句")
            # 查找第一个CREATE TABLE
            create_start = design_text.find("CREATE TABLE")
            if create_start != -1:
                # 尝试提取所有CREATE TABLE语句
                script_parts = []
                current_pos = create_start
                while current_pos != -1:
                    next_create = design_text.find("CREATE TABLE", current_pos + 12)
                    # 如果找到下一个CREATE TABLE，提取到那里
                    # 否则提取到结尾或下一个明显的分隔符
                    if next_create != -1:
                        # 查找这个CREATE TABLE语句的结束位置
                        semi_pos = design_text.rfind(";", current_pos, next_create)
                        if semi_pos != -1:
                            script_parts.append(design_text[current_pos:semi_pos+1])
                        else:
                            # 如果没有找到分号，取整个部分
                            script_parts.append(design_text[current_pos:next_create])
                        current_pos = next_create
                    else:
                        # 最后一个CREATE TABLE，提取到结尾
                        script_parts.append(design_text[current_pos:])
                        break
                
                script = "\n\n".join(script_parts)
                print(f"直接提取CREATE TABLE语句，提取到 {len(script_parts)} 个表，总长度: {len(script)}")
        
        # 如果脚本为空，使用整个文本作为脚本
        if not script and design_text.strip():
            print("未能提取到SQL脚本，使用完整文本")
        script = design_text
        
        # 确保SQL使用正确的字符集和排序规则
        if "ENGINE=InnoDB" in script and "DEFAULT CHARSET=utf8mb4" not in script:
            script = script.replace("ENGINE=InnoDB", "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")
            print("添加字符集和排序规则")
        
        # 如果脚本中包含utf8mb4_0900_ai_ci，替换为utf8mb4_unicode_ci
        if "utf8mb4_0900_ai_ci" in script:
            script = script.replace("utf8mb4_0900_ai_ci", "utf8mb4_unicode_ci")
            print("将utf8mb4_0900_ai_ci替换为utf8mb4_unicode_ci")
        
        # 提取JSON结构
        # 先查找```json标记
        json_found = False
        if "```json" in design_text:
            print("找到JSON代码块标记")
            json_start = design_text.find("```json")
            json_end = design_text.find("```", json_start + 7)
            if json_start != -1 and json_end != -1:
                json_text = design_text[json_start + 7:json_end].strip()
                print(f"从JSON代码块提取到内容，长度: {len(json_text)}")
                try:
                    json_data = json.loads(json_text)
                    json_found = True
                    if "tables" in json_data:
                        tables = json.dumps(json_data["tables"], ensure_ascii=False)
                        print(f"提取到表信息，表数量: {len(json_data['tables'])}")
                    if "relationships" in json_data:
                        relationships = json.dumps(json_data["relationships"], ensure_ascii=False)
                        print(f"提取到关系信息，关系数量: {len(json_data['relationships'])}")
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
        
        # 如果没有找到JSON代码块，尝试提取任何JSON结构
        if not json_found:
            print("未找到JSON代码块，尝试直接查找JSON结构")
            json_patterns = [
                ('{', '}'),   # 标准JSON
                ('{"tables":', '}')  # 表结构JSON
            ]
            
            for start_pat, end_pat in json_patterns:
                json_start = design_text.find(start_pat)
                if json_start != -1:
                    json_end = design_text.rfind(end_pat)
                    if json_end != -1 and json_end > json_start:
                        # 确保结束位置包含结束符号
                        json_end += len(end_pat)
                        json_text = design_text[json_start:json_end].strip()
                        print(f"找到可能的JSON结构，长度: {len(json_text)}")
                        
                        # 尝试修复常见的JSON错误
                        try:
                            # 替换中文引号为英文引号
                            json_text = json_text.replace('"', '"').replace('"', '"')
                            # 替换中文冒号为英文冒号
                            json_text = json_text.replace('：', ':')
                            # 尝试解析
                            json_data = json.loads(json_text)
                            json_found = True
                            if "tables" in json_data:
                                tables = json.dumps(json_data["tables"], ensure_ascii=False)
                                print(f"提取到表信息，表数量: {len(json_data['tables'])}")
                            if "relationships" in json_data:
                                relationships = json.dumps(json_data["relationships"], ensure_ascii=False)
                                print(f"提取到关系信息，关系数量: {len(json_data['relationships'])}")
                            break
                        except json.JSONDecodeError as e:
                            print(f"JSON解析错误: {e}")
        
        # 如果仍未提取到表结构，但有SQL脚本，尝试基于SQL脚本生成基本表结构
        if not tables and script:
            print("未提取到表结构，尝试从SQL脚本生成基本表结构")
            # 提取所有CREATE TABLE语句中的表名
            import re
            table_matches = re.finditer(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?', script, re.IGNORECASE)
            
            tables_data = []
            for match in table_matches:
                table_name = match.group(1)
                # 提取表注释
                comment_match = re.search(r"COMMENT\s*=\s*['\"](.+?)['\"]", script[match.start():], re.IGNORECASE)
                description = comment_match.group(1) if comment_match else table_name
                
                # 创建基本表结构
                table_data = {
                    "name": table_name,
                    "description": description,
                    "fields": [
                        {"name": "id", "type": "INT", "description": "主键ID", "constraints": "NOT NULL AUTO_INCREMENT"}
                    ],
                    "primary_key": ["id"]
                }
                tables_data.append(table_data)
            
            if tables_data:
                tables = json.dumps(tables_data, ensure_ascii=False)
                print(f"从SQL脚本生成了基本表结构，表数量: {len(tables_data)}")
        
        print(f"处理完成。表信息长度: {len(tables)}，关系信息长度: {len(relationships)}，SQL脚本长度: {len(script)}")
    except Exception as e:
        print(f"解析数据库设计时出错: {str(e)}")
        # 解析失败，使用原始文本
        script = design_text
        tables = ""
        relationships = ""
    
    # 检查是否已经存在数据库设计，如果存在则更新
    existing_design = DatabaseDesign.query.filter_by(project_id=project_id).first()
    
    if existing_design:
        existing_design.script = script
        existing_design.tables = tables
        existing_design.relationships = relationships
        existing_design.api_response = json.dumps(str(result.get('raw_response', {})))
    else:
        # 创建新的数据库设计
        design = DatabaseDesign(
            project_id=project_id,
            script=script,
            tables=tables,
            relationships=relationships,
            api_response=json.dumps(str(result.get('raw_response', {})))
        )
        db.session.add(design)
    
    db.session.commit()
    
    # 返回生成的数据库设计
    database_design = DatabaseDesign.query.filter_by(project_id=project_id).first()
    
    return jsonify({
        'success': True,
        'message': '数据库设计生成成功',
        'database_design': {
            'id': database_design.id,
            'script': database_design.script,
            'tables': database_design.tables,
            'relationships': database_design.relationships
        }
    })

@database_design.route('/api/<int:project_id>/update', methods=['PUT'])
@login_required
def update_database_script(project_id):
    """手动更新数据库脚本"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    
    if not project:
        return jsonify({'success': False, 'message': '项目不存在或无权限访问'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '没有提供数据'}), 400
    
    script = data.get('script')
    tables = data.get('tables', '')
    relationships = data.get('relationships', '')
    
    if not script:
        return jsonify({'success': False, 'message': '脚本内容不能为空'}), 400
    
    # 检查是否已经存在数据库设计，如果不存在则创建
    database_design = DatabaseDesign.query.filter_by(project_id=project_id).first()
    
    if not database_design:
        database_design = DatabaseDesign(project_id=project_id)
        db.session.add(database_design)
    
    database_design.script = script
    database_design.tables = tables
    database_design.relationships = relationships
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '数据库脚本更新成功',
        'database_design': {
            'id': database_design.id,
            'script': database_design.script,
            'tables': database_design.tables,
            'relationships': database_design.relationships
        }
    }) 