import os
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps

# 全局变量用于跟踪初始化状态
_is_initialized = False

def singleton_init(func):
    """确保函数只执行一次的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global _is_initialized
        if not _is_initialized:
            _is_initialized = True
            return func(*args, **kwargs)
    return wrapper

@singleton_init
def init_logging(app):
    """初始化日志系统"""
    # 创建logs目录
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    # 设置日志文件
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240,
        backupCount=10
    )
    
    # 设置日志格式
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # 设置日志级别
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('日志系统初始化完成')

    # 配置Flask日志记录器
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    # 配置SQLAlchemy日志记录器
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # 配置Werkzeug日志记录器
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    
    # 设置根日志记录器级别
    logging.getLogger().setLevel(logging.INFO) 