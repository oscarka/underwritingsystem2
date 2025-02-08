"""Business views package."""
from flask import Blueprint
from .channel import bp as channel_bp
from .product import bp as product_bp
from .company import bp as company_bp
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('business', __name__, url_prefix='/business')
logger.info(f'创建业务视图主蓝图: name={bp.name}, url_prefix={bp.url_prefix}')

def init_app(app):
    """初始化业务模块"""
    # 注册主蓝图
    logger.info('开始注册业务视图主蓝图...')
    app.register_blueprint(bp)
    logger.info('业务视图主蓝图注册完成')
    
    # 注册渠道蓝图
    logger.info('开始注册渠道视图蓝图...')
    app.register_blueprint(channel_bp)
    logger.info('渠道视图蓝图注册完成')
    
    # 注册产品蓝图
    logger.info('开始注册产品视图蓝图...')
    app.register_blueprint(product_bp)
    logger.info('产品视图蓝图注册完成')
    
    # 注册保司蓝图
    logger.info('开始注册保司视图蓝图...')
    app.register_blueprint(company_bp)
    logger.info('保司视图蓝图注册完成') 