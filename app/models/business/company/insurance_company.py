from app.extensions import db
from app.models.base.model import BaseModel
from app.models.base.mixins.status import StatusMixin
from app.models.base.enums import StatusEnum
from typing import List, Tuple

class InsuranceCompany(BaseModel, StatusMixin):
    """保险公司模型"""
    __tablename__ = 'insurance_companies'
    
    id = db.Column(db.Integer, primary_key=True)  # 添加主键
    name = db.Column(db.String(64), nullable=False)  # 公司名称
    code = db.Column(db.String(32), unique=True, nullable=False)  # 公司编码
    description = db.Column(db.Text)  # 描述
    contact = db.Column(db.String(32))  # 联系人
    phone = db.Column(db.String(32))  # 联系电话
    address = db.Column(db.String(256))  # 地址
    remark = db.Column(db.Text)  # 备注
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证数据"""
        errors = []
        if not self.name:
            errors.append('保险公司名称不能为空')
        if not self.code:
            errors.append('保险公司编码不能为空')
        return len(errors) == 0, errors
    
    def validate_create(self) -> Tuple[bool, List[str]]:
        return self.validate()
    
    def validate_update(self) -> Tuple[bool, List[str]]:
        return self.validate()
        
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'contact': self.contact,
            'phone': self.phone,
            'address': self.address,
            'remark': self.remark,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        } 