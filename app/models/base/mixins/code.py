from app import db
from sqlalchemy import event
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class CodeMixin:
    """编码混入类"""
    code = db.Column(db.String(32), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        logger.info('CodeMixin.__init__ 开始')
        logger.info('原始参数:')
        for key, value in kwargs.items():
            logger.info(f'  {key}: {value}')
        
        # 设置code字段
        if 'code' in kwargs:
            logger.info(f'设置 code 字段: {kwargs["code"]}')
            self.code = kwargs.pop('code')  # 使用 pop 而不是直接访问，这样会移除该字段
        else:
            logger.warning('未找到 code 字段')
        
        # 调用父类的__init__方法
        try:
            logger.info('调用父类 __init__')
            super().__init__(*args, **kwargs)
            logger.info('CodeMixin.__init__ 完成')
        except Exception as e:
            logger.error(f'CodeMixin.__init__ 失败: {str(e)}')
            logger.error(f'错误类型: {type(e).__name__}')
            raise

    @classmethod
    def find_by_code(cls, code: str) -> Optional[Any]:
        """通过编码查找"""
        return cls.query.filter_by(code=code).first()

    @classmethod
    def exists_code(cls, code: str) -> bool:
        """检查编码是否存在"""
        return cls.query.filter_by(code=code).count() > 0

    def validate_code(self) -> bool:
        """验证编码是否唯一"""
        if not self.code:
            return False
        
        # 查询同名记录
        query = self.__class__.query.filter_by(code=self.code)
        if self.id:
            query = query.filter(self.__class__.id != self.id)
        
        return query.first() is None
    
    def get_by_code(self, code: str) -> Optional[Any]:
        """获取指定编码的实例"""
        return self.find_by_code(code) 