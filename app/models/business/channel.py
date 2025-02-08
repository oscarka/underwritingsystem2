from app import db
from app.models.base.model import BaseModel
from app.models.base.mixins.code import CodeMixin
from app.models.base.enums import StatusEnum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Channel(CodeMixin, BaseModel):
    """渠道模型"""
    __tablename__ = 'channels'

    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default=StatusEnum.ENABLED.value)

    def __init__(self, **kwargs):
        logger.info('Channel.__init__ 开始')
        logger.info('原始参数:')
        for key, value in kwargs.items():
            logger.info(f'  {key}: {value}')
            
        # 设置默认状态
        kwargs.setdefault('status', StatusEnum.ENABLED.value)
        
        # 调用父类的初始化方法
        try:
            super().__init__(**kwargs)
            logger.info('Channel.__init__ 完成')
        except Exception as e:
            logger.error(f'Channel.__init__ 失败: {str(e)}')
            logger.error(f'错误类型: {type(e).__name__}')
            raise

    @property
    def created_at_str(self):
        """格式化创建时间"""
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''

    @property
    def updated_at_str(self):
        """格式化更新时间"""
        return self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at_str,
            'updated_at': self.updated_at_str
        } 