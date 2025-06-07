from flask import Blueprint, jsonify
from app.models import SystemConfig

# 创建蓝图
system_config = Blueprint('system_config', __name__)

@system_config.route('/api/configs/<config_type>', methods=['GET'])
@system_config.route('/configs/<config_type>', methods=['GET'])
def get_configs(config_type):
    """获取指定类型的系统配置项列表"""
    valid_types = [
        'architecture_language',
        'architecture_type',
        'database_type',
        'module_language',
        'module_type',
        'test_type',
        'deployment_environment'
    ]
    
    if config_type not in valid_types:
        return jsonify({
            'success': False,
            'message': f'无效的配置类型: {config_type}'
        }), 400
    
    configs = SystemConfig.get_config_items(config_type)
    
    # 转换为前端可用的格式
    config_items = [item.to_dict() for item in configs]
    
    return jsonify({
        'success': True,
        'items': config_items
    })

@system_config.route('/api/configs/defaults', methods=['GET'])
@system_config.route('/configs/defaults', methods=['GET'])
def get_default_configs():
    """获取所有类型的默认配置项"""
    config_types = [
        'architecture_language',
        'architecture_type',
        'database_type',
        'module_language',
        'module_type',
        'test_type',
        'deployment_environment'
    ]
    
    defaults = {}
    for config_type in config_types:
        default_item = SystemConfig.get_default_item(config_type)
        if default_item:
            defaults[config_type] = default_item.to_dict()
    
    return jsonify({
        'success': True,
        'defaults': defaults
    }) 