from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel
from app.models.base.mixins import StatusMixin
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.rules.ai.ai_parameter_type import AIParameterType

class AIParameter(BaseModel, StatusMixin):
    """智核参数模型"""
    __tablename__ = 'ai_parameters'
    
    name = db.Column(db.String(100), nullable=False, comment='参数名称')
    parameter_type_id = db.Column(db.Integer, db.ForeignKey('ai_parameter_types.id'), nullable=False, comment='参数类型ID')
    rule_id = db.Column(db.Integer, db.ForeignKey('underwriting_rules.id'), nullable=False, comment='核保规则ID')
    value = db.Column(db.String(500), nullable=False, comment='参数值')
    description = db.Column(db.String(500), comment='参数描述')
    
    # 关联关系
    parameter_type = db.relationship('AIParameterType', backref='parameters')
    rule = db.relationship('UnderwritingRule', backref='ai_parameters')
    
    def __repr__(self):
        return f'<AIParameter {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'parameter_type_id': self.parameter_type_id,
            'parameter_type_name': self.parameter_type.name if self.parameter_type else None,
            'rule_id': self.rule_id,
            'rule_name': self.rule.name if self.rule else None,
            'value': self.value,
            'description': self.description,
            'status': self.status if hasattr(self, 'status') else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def validate(self) -> tuple[bool, list[str]]:
        """验证数据"""
        errors = []
        if not self.name:
            errors.append('参数名称不能为空')
        if not self.parameter_type_id:
            errors.append('参数类型不能为空')
        if not self.rule_id:
            errors.append('所属规则不能为空')
        if not self.value:
            errors.append('参数值不能为空')
        return len(errors) == 0, errors

    def validate_create(self) -> tuple[bool, list[str]]:
        """验证创建数据"""
        return self.validate()

    def validate_update(self) -> tuple[bool, list[str]]:
        """验证更新数据"""
        return self.validate() 