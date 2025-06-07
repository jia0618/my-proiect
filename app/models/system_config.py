from app import db
from datetime import datetime

class SystemConfig(db.Model):
    """系统配置模型，用于存储各种下拉选项的配置"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    config_type = db.Column(db.String(50), nullable=False)
    config_key = db.Column(db.String(50), nullable=False)
    config_value = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 确保config_type和config_key的组合是唯一的
    __table_args__ = (
        db.UniqueConstraint('config_type', 'config_key', name='type_key'),
    )
    
    @staticmethod
    def get_config_items(config_type):
        """获取指定类型的所有配置项"""
        return SystemConfig.query.filter_by(config_type=config_type).order_by(SystemConfig.sort_order).all()
    
    @staticmethod
    def get_default_item(config_type):
        """获取指定类型的默认配置项"""
        default_item = SystemConfig.query.filter_by(
            config_type=config_type, 
            is_default=True
        ).first()
        
        # 如果没有默认项，则返回该类型的第一项
        if not default_item:
            default_item = SystemConfig.query.filter_by(
                config_type=config_type
            ).order_by(SystemConfig.sort_order).first()
        
        return default_item
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'key': self.config_key,
            'value': self.config_value,
            'is_default': self.is_default
        } 