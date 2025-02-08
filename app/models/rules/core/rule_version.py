from app import db
from app.models.base.model import BaseModel
from app.models.base.enums import StatusEnum

class RuleVersion(BaseModel):
    """规则版本模型"""
    __tablename__ = 'rule_versions'
    __table_args__ = {'extend_existing': True}
    
    name = db.Column(db.String(100), nullable=False)  # 规则名称
    code = db.Column(db.String(50), unique=True, index=True)  # 规则编码
    version = db.Column(db.String(50))  # 版本号
    description = db.Column(db.Text)  # 描述
    status = db.Column(db.String(20), default=StatusEnum.ENABLED.value)  # 状态

    # 暂时注释掉关联关系
    # underwriting_rules = db.relationship('UnderwritingRule', back_populates='rule_version')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'version': self.version,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @property
    def status_display(self):
        """获取状态的显示文本"""
        status_map = {
            StatusEnum.ENABLED.value: '已启用',
            StatusEnum.DISABLED.value: '已禁用',
            StatusEnum.DELETED.value: '已删除'
        }
        return status_map.get(self.status, self.status) 