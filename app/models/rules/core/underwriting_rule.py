from app import db
from app.models.base.model import BaseModel
from app.models.base.enums import StatusEnum

class UnderwritingRule(BaseModel):
    """核保规则模型"""
    __tablename__ = 'underwriting_rules'
    __table_args__ = {'extend_existing': True}
    
    name = db.Column(db.String(100), nullable=False)  # 规则名称
    version = db.Column(db.String(50))  # 版本号
    description = db.Column(db.Text)  # 描述
    status = db.Column(db.String(20), default=StatusEnum.DRAFT.value)  # 默认为草稿状态
    
    # 关系
    conclusions = db.relationship('Conclusion', back_populates='underwriting_rule', cascade='all, delete-orphan')
    diseases = db.relationship('Disease', backref='rule', lazy='dynamic')  # 添加与Disease的关系

    def __repr__(self):
        return f'<UnderwritingRule {self.name}>'

    @property
    def has_imported_data(self):
        """判断是否有导入的数据"""
        return bool(self.diseases.count())

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'status': self.status,
            'conclusions': [c.to_dict() for c in self.conclusions],
            'diseases': [d.to_dict() for d in self.diseases],  # 添加diseases字段
            'has_data': self.has_imported_data,  # 使用属性方法
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @property
    def status_display(self):
        """获取状态的显示文本"""
        status_map = {
            StatusEnum.DRAFT.value: '草稿',
            StatusEnum.ENABLED.value: '已启用',
            StatusEnum.DISABLED.value: '已禁用',
            StatusEnum.DELETED.value: '已删除',
            StatusEnum.IMPORTED.value: '已导入'
        }
        return status_map.get(self.status, self.status) 