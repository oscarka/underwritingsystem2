from app.extensions import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)  # 为所有模型添加默认主键
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        logger.info(f'BaseModel.__init__ 开始，模型类: {self.__class__.__name__}')
        logger.info('原始参数:')
        for key, value in kwargs.items():
            logger.info(f'  {key}: {value}')
        
        # 移除不支持的字段
        valid_fields = {c.name for c in self.__table__.columns}
        logger.info(f'有效字段: {valid_fields}')
        
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}
        logger.info('过滤后的参数:')
        for key, value in filtered_kwargs.items():
            logger.info(f'  {key}: {value}')
        
        # 调用父类的__init__方法
        try:
            super().__init__(**filtered_kwargs)
            logger.info('BaseModel.__init__ 完成')
        except Exception as e:
            logger.error(f'BaseModel.__init__ 失败: {str(e)}')
            logger.error(f'错误类型: {type(e).__name__}')
            raise

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 