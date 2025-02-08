# 空文件，用于包导入 
from flask import Blueprint, request
from .channel import (
    get_channels, get_channel, create_channel, 
    update_channel, update_channel_status, 
    delete_channel, get_public_channels
)
from .company import (
    get_companies, get_company, create_company,
    update_company, delete_company
)
from .product_type import get_product_types, get_product_type
from .product import get_products, get_product, create_product, update_product, delete_product
import logging

logger = logging.getLogger(__name__)

# 创建业务蓝图，指定url_prefix
bp = Blueprint('business_api', __name__, url_prefix='/api/v1/business')
logger.info(f'创建业务API蓝图: {bp.name}, url_prefix={bp.url_prefix}')

# 注册渠道路由，把public路由放在最前面
logger.info('开始注册渠道路由...')
bp.add_url_rule('/channels/public', view_func=get_public_channels, methods=['GET'])
bp.add_url_rule('/channels', view_func=get_channels, methods=['GET'])
bp.add_url_rule('/channels/<int:id>', view_func=get_channel, methods=['GET'])
bp.add_url_rule('/channels', view_func=create_channel, methods=['POST'])
bp.add_url_rule('/channels/<int:id>', view_func=update_channel, methods=['PUT'])
bp.add_url_rule('/channels/<int:id>/status', view_func=update_channel_status, methods=['PATCH'])
bp.add_url_rule('/channels/<int:id>', view_func=delete_channel, methods=['DELETE'])
logger.info('渠道路由注册完成')

# 注册保险公司路由
logger.info('开始注册保险公司路由...')
bp.add_url_rule('/companies', view_func=get_companies, methods=['GET'])
bp.add_url_rule('/companies/<int:id>', view_func=get_company, methods=['GET'])
bp.add_url_rule('/companies', view_func=create_company, methods=['POST'])
bp.add_url_rule('/companies/<int:id>', view_func=update_company, methods=['PUT'])
bp.add_url_rule('/companies/<int:id>', view_func=delete_company, methods=['DELETE'])
logger.info('保险公司路由注册完成')

# 注册产品类型路由
logger.info('开始注册产品类型路由...')
bp.add_url_rule('/product-types', view_func=get_product_types, methods=['GET'])
bp.add_url_rule('/product-types/<int:id>', view_func=get_product_type, methods=['GET'])
logger.info('产品类型路由注册完成')

# 注册产品路由
logger.info('开始注册产品路由...')
bp.add_url_rule('/products', view_func=get_products, methods=['GET'])
bp.add_url_rule('/products/<int:id>', view_func=get_product, methods=['GET'])
bp.add_url_rule('/products', view_func=create_product, methods=['POST'])
bp.add_url_rule('/products/<int:id>', view_func=update_product, methods=['PUT'])
bp.add_url_rule('/products/<int:id>', view_func=delete_product, methods=['DELETE'])
logger.info('产品路由注册完成')

# 添加请求前的日志记录
@bp.before_request
def log_request():
    logger.info(f'收到请求: {request.method} {request.path}')
    logger.info(f'请求参数: {request.args}')
    if request.is_json:
        logger.info(f'JSON数据: {request.get_json()}')

# 添加请求后的日志记录
@bp.after_request
def log_response(response):
    logger.info(f'响应状态码: {response.status_code}')
    return response 