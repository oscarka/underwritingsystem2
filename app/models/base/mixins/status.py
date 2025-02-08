from app.extensions import db

class StatusMixin:
    """状态混入类"""
    status = db.Column(db.String(20), default='active')  # active/inactive
    
    @property
    def is_active(self) -> bool:
        """是否激活"""
        return self.status == 'active' 