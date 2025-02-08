from app.extensions import db
from app.models.base import BaseModel, CodeMixin
from app.models.base.enums import StatusEnum
from datetime import datetime
from typing import Dict, Any

class AIParameterType(BaseModel, CodeMixin):
    """智核参数类型模型"""
    __tablename__ = 'ai_parameter_types'
    
    name = db.Column(db.String(100), nullable=False, comment='类型名称')
    description = db.Column(db.String(500), comment='类型描述')
    value_type = db.Column(db.String(20))  # 值类型：string/number/boolean/json
    default_value = db.Column(db.JSON)  # 默认值
    validation_rules = db.Column(db.JSON)  # 验证规则
    status = db.Column(db.String(20), default=StatusEnum.ENABLED.value)  # 状态

    def __repr__(self):
        return f'<AIParameterType {self.name}>'

    @property
    def created_at_str(self) -> str:
        """创建时间字符串"""
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''

    @property
    def updated_at_str(self) -> str:
        """更新时间字符串"""
        return self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'value_type': self.value_type,
            'default_value': self.default_value,
            'validation_rules': self.validation_rules,
            'status': self.status,
            'created_at_str': self.created_at_str,
            'updated_at_str': self.updated_at_str
        }

    def validate(self) -> tuple[bool, list[str]]:
        """验证数据"""
        errors = []
        if not self.name:
            errors.append('类型名称不能为空')
        if not self.code:
            errors.append('类型编码不能为空')
        if not self.validate_code():
            errors.append('类型编码已存在')
        if not self.value_type:
            errors.append('值类型不能为空')
        return len(errors) == 0, errors

    def validate_create(self) -> tuple[bool, list[str]]:
        """验证创建数据"""
        return self.validate()

    def validate_update(self) -> tuple[bool, list[str]]:
        """验证更新数据"""
        return self.validate() 