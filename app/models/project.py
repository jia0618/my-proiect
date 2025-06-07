from app import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 与其他表建立关系
    requirements = db.relationship('Requirement', backref='project', lazy=True, cascade='all, delete-orphan')
    architecture_codes = db.relationship('ArchitectureCode', backref='project', lazy=True, cascade='all, delete-orphan')
    database_designs = db.relationship('DatabaseDesign', backref='project', lazy=True, cascade='all, delete-orphan')
    module_codes = db.relationship('ModuleCode', backref='project', lazy=True, cascade='all, delete-orphan')
    test_cases = db.relationship('TestCase', backref='project', lazy=True, cascade='all, delete-orphan')
    deployments = db.relationship('Deployment', backref='project', lazy=True, cascade='all, delete-orphan')
    
class Requirement(db.Model):
    __tablename__ = 'requirements'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
class ArchitectureCode(db.Model):
    __tablename__ = 'architecture_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    architecture_type = db.Column(db.String(50), nullable=False)
    api_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
class DatabaseDesign(db.Model):
    __tablename__ = 'database_designs'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    script = db.Column(db.Text, nullable=False)
    tables = db.Column(db.Text)
    relationships = db.Column(db.Text)
    api_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
class ModuleCode(db.Model):
    __tablename__ = 'module_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Text, nullable=False)
    module_type = db.Column(db.String(50))
    language = db.Column(db.String(50))  # 存储模块使用的编程语言
    dependencies = db.Column(db.Text)  # 存储模块依赖项，可为JSON格式
    api_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
class TestCase(db.Model):
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    test_type = db.Column(db.String(50))
    test_content = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text)
    test_result = db.Column(db.String(50))
    api_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
class Deployment(db.Model):
    __tablename__ = 'deployments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    environment = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    deploy_steps = db.Column(db.Text)
    log = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now) 