from app import db
from app.models.base.model import BaseModel
from app.models.base.mixins.status import StatusMixin
from typing import List, Tuple, Dict, Any
from datetime import datetime

class ChannelConfig(BaseModel, StatusMixin):
    """渠道配置模型"""
    __tablename__ = 'channel_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))
    config_key = db.Column(db.String(50), nullable=False)
    config_value = db.Column(db.JSON)
    description = db.Column(db.Text)
    effective_time = db.Column(db.DateTime)    # 生效时间
    expiration_time = db.Column(db.DateTime)   # 失效时间
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证数据"""
        errors = []
        if not self.channel_id:
            errors.append('渠道ID不能为空')
        if not self.config_key:
            errors.append('配置键不能为空')
        if self.effective_time and self.expiration_time:
            if self.effective_time >= self.expiration_time:
                errors.append('生效时间必须早于失效时间')
        return len(errors) == 0, errors
    
    def validate_create(self) -> Tuple[bool, List[str]]:
        return self.validate()
    
    def validate_update(self) -> Tuple[bool, List[str]]:
        return self.validate()
    
    @property
    def is_effective(self) -> bool:
        """是否在有效期内"""
        now = datetime.utcnow()
        if not self.effective_time:
            return True
        if not self.expiration_time:
            return now >= self.effective_time
        return self.effective_time <= now <= self.expiration_time 