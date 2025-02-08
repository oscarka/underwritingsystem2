from app.models.base.model import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime

class ConclusionType(BaseModel):
    __tablename__ = 'conclusion_types'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)  # 类型编码
    name = Column(String(100), nullable=False)  # 类型名称
    description = Column(String(200))  # 描述
    input_type = Column(String(50), nullable=False)  # 输入类型(text/select/radio/checkbox等)
    options = Column(JSON)  # 选项配置(JSON格式)
    validation_rules = Column(JSON)  # 验证规则(JSON格式)
    status = Column(String(20), nullable=False, default='active')  # 状态
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    # conclusions = relationship('Conclusion', back_populates='conclusion_type')
    
    def __init__(self, code, name, input_type, options=None, validation_rules=None, description=None):
        self.code = code
        self.name = name
        self.input_type = input_type
        self.options = options or {}
        self.validation_rules = validation_rules or {}
        self.description = description
        
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'input_type': self.input_type,
            'options': self.options,
            'validation_rules': self.validation_rules,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 