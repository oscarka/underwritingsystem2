from app import db
from datetime import datetime

class TimestampMixin:
    """时间戳混入类"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    @property
    def created_at_str(self) -> str:
        """创建时间字符串"""
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''

    @property
    def updated_at_str(self) -> str:
        """更新时间字符串"""
        return self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
    
    @property
    def created_date(self) -> str:
        """创建日期字符串"""
        return self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
    
    @property
    def updated_date(self) -> str:
        """更新日期字符串"""
        return self.updated_at.strftime('%Y-%m-%d') if self.updated_at else '' 