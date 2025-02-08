from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='启用')
    permissions = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='tenant', lazy='dynamic')

    def __repr__(self):
        return f'<Tenant {self.name}>'

class Channel(db.Model):
    __tablename__ = 'channels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 定义反向关系
    products = db.relationship('Product', backref='channel_ref', lazy='dynamic')

    def __repr__(self):
        return f'<Channel {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), unique=True)
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_types.id'))
    insurance_company_id = db.Column(db.Integer, db.ForeignKey('insurance_companies.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))
    ai_parameter_id = db.Column(db.Integer, db.ForeignKey('ai_parameters.id'))
    risk_pool_id = db.Column(db.Integer, db.ForeignKey('risk_pools.id'))
    interaction_flow = db.Column(db.String(50))
    status = db.Column(db.String(20), default='启用')
    product_url = db.Column(db.String(255))
    qr_code_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 定义关系 - 移除所有backref
    channel = db.relationship('Channel')
    product_type = db.relationship('ProductType')
    insurance_company = db.relationship('InsuranceCompany')
    ai_parameter = db.relationship('AIParameter')
    risk_pool = db.relationship('RiskPool')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'product_code': self.product_code,
            'product_type_id': self.product_type_id,
            'product_type_name': self.product_type.name if self.product_type else None,
            'insurance_company_id': self.insurance_company_id,
            'insurance_company_name': self.insurance_company.name if self.insurance_company else None,
            'channel_id': self.channel_id,
            'channel_name': self.channel.name if self.channel else None,
            'ai_parameter_id': self.ai_parameter_id,
            'ai_parameter_name': self.ai_parameter.name if self.ai_parameter else None,
            'interaction_flow': self.interaction_flow,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class AIParameter(db.Model):
    __tablename__ = 'ai_parameters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    param_type = db.Column(db.String(50))
    value = db.Column(db.JSON)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='启用')
    rule_id = db.Column(db.Integer, db.ForeignKey('underwriting_rules.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 定义反向关系
    products = db.relationship('Product', backref='ai_parameter_ref', lazy='dynamic')

    def __repr__(self):
        return f'<AIParameter {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'param_type': self.param_type,
            'description': self.description,
            'rule_id': self.rule_id,
            'rule_name': self.rule.name if self.rule else None,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class InsuranceCompany(db.Model):
    __tablename__ = 'insurance_companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 定义反向关系
    products = db.relationship('Product', backref='insurance_company_ref', lazy='dynamic')

    def __repr__(self):
        return f'<InsuranceCompany {self.name}>'

class ProductType(db.Model):
    __tablename__ = 'product_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 定义反向关系
    products = db.relationship('Product', backref='product_type_ref', lazy='dynamic')

    def __repr__(self):
        return f'<ProductType {self.name}>'

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_code = db.Column(db.String(50))
    content = db.Column(db.Text)
    attribute = db.Column(db.String(20))  # P普通/G归类
    question_type = db.Column(db.String(20))  # 1单选/0多选/2录入
    remark = db.Column(db.Text)  # 问题解释
    rule_id = db.Column(db.Integer, db.ForeignKey('underwriting_rules.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'question_code': self.question_code,
            'content': self.content,
            'attribute': self.attribute,
            'question_type': self.question_type,
            'remark': self.remark,
            'rule_id': self.rule_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class RiskPool(db.Model):
    __tablename__ = 'risk_pools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 定义反向关系
    products = db.relationship('Product', backref='risk_pool_ref', lazy='dynamic')