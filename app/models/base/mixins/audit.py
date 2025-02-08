from app import db
from datetime import datetime
from typing import Optional
from flask_login import current_user

class AuditMixin:
    """审计信息混入类"""
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def set_created_by(self, user_id: Optional[int] = None) -> None:
        """设置创建者"""
        if user_id:
            self.created_by = user_id
        elif current_user and not current_user.is_anonymous:
            self.created_by = current_user.id
    
    def set_updated_by(self, user_id: Optional[int] = None) -> None:
        """设置更新者"""
        if user_id:
            self.updated_by = user_id
        elif current_user and not current_user.is_anonymous:
            self.updated_by = current_user.id
            
    @property
    def creator(self) -> Optional['User']:
        """获取创建者"""
        if self.created_by:
            from app.models import User
            return User.query.get(self.created_by)
        return None
        
    @property
    def updater(self) -> Optional['User']:
        """获取更新者"""
        if self.updated_by:
            from app.models import User
            return User.query.get(self.updated_by)
        return None 