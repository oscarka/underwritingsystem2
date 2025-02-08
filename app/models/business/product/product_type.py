from app import db
from app.models.base.model import BaseModel
from app.models.base.enums import StatusEnum

class ProductType(BaseModel):
    """产品类型模型"""
    __tablename__ = 'product_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default=StatusEnum.ENABLED.value)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        } 