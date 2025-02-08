from app import db
from datetime import datetime

class StatusMixin:
    """状态管理混入类"""
    status = db.Column(db.String(20), default='enabled')
    
    def activate(self):
        self.status = 'enabled'
        db.session.commit()
        
    def deactivate(self):
        self.status = 'disabled'
        db.session.commit()
        
    @property
    def is_active(self):
        return self.status == 'enabled'

class CodeMixin:
    """编码管理混入类"""
    code = db.Column(db.String(50), unique=True, index=True)
    name = db.Column(db.String(100), nullable=False)

class TimestampMixin:
    """时间戳混入类"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow) 