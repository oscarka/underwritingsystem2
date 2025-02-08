from app.extensions import db
from app.models.base.model import BaseModel
from app.models.base.status_mixin import StatusMixin

class Tenant(BaseModel):
    __tablename__ = 'tenant'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='enabled') 