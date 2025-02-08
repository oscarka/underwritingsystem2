from app.extensions import db
from app.models.base.model import BaseModel

class Product(BaseModel):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_types.id'))
    insurance_company_id = db.Column(db.Integer, db.ForeignKey('insurance_companies.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))
    ai_parameter_id = db.Column(db.Integer, db.ForeignKey('ai_parameters.id'))
    status = db.Column(db.String(20), default='enabled')

    # 关系
    product_type = db.relationship('ProductType', backref='products')
    insurance_company = db.relationship('InsuranceCompany', backref='products')
    channel = db.relationship('Channel', backref='products')
    ai_parameter = db.relationship('AIParameter', backref='products')

    @property
    def created_at_str(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''

    @property
    def updated_at_str(self):
        return self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.product_code,
            'productType': {
                'id': self.product_type.id,
                'name': self.product_type.name,
                'code': self.product_type.code
            } if self.product_type else None,
            'insuranceCompany': {
                'id': self.insurance_company.id,
                'name': self.insurance_company.name,
                'code': self.insurance_company.code
            } if self.insurance_company else None,
            'channel': {
                'id': self.channel.id,
                'name': self.channel.name,
                'code': self.channel.code
            } if self.channel else None,
            'aiParameter': {
                'id': self.ai_parameter.id,
                'name': self.ai_parameter.name,
                'rule': {
                    'id': self.ai_parameter.rule.id,
                    'name': self.ai_parameter.rule.name
                } if hasattr(self.ai_parameter, 'rule') and self.ai_parameter.rule else None
            } if self.ai_parameter else None,
            'status': self.status,
            'createdAt': self.created_at_str,
            'updatedAt': self.updated_at_str
        }