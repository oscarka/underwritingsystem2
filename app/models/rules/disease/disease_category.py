from app import db
from app.models.base.model import BaseModel

class DiseaseCategory(BaseModel):
    """疾病大类模型"""
    __tablename__ = 'disease_categories'
    __table_args__ = {'extend_existing': True}
    
    code = db.Column(db.String(50), unique=True, nullable=False)  # 疾病大类编码
    name = db.Column(db.String(50), nullable=False)  # 疾病大类名称
    parent_id = db.Column(db.Integer, db.ForeignKey('disease_categories.id'))  # 父级分类ID
    level = db.Column(db.Integer)  # 层级
    sort_order = db.Column(db.Integer)  # 排序
    description = db.Column(db.String(500))  # 描述
    status = db.Column(db.String(20), nullable=False, default='active')  # 状态
    rule_id = db.Column(db.Integer, db.ForeignKey('underwriting_rules.id'), nullable=True)  # 所属规则ID
    
    # 关系
    rule = db.relationship('UnderwritingRule', backref='disease_categories')
    
    def __repr__(self):
        return f'<DiseaseCategory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'parent_id': self.parent_id,
            'level': self.level,
            'sort_order': self.sort_order,
            'description': self.description,
            'status': self.status,
            'rule_id': self.rule_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
    @classmethod
    def get_by_rule_id(cls, rule_id):
        """通过规则ID获取疾病大类列表"""
        return cls.query.filter_by(rule_id=rule_id).all() 