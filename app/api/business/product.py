from flask import Blueprint, request
from app.utils.response import success_response, error_response
from app.services.business.product import ProductService
from app.decorators import login_required
import logging
import traceback

logger = logging.getLogger(__name__)

bp = Blueprint('product', __name__)

@bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """获取产品列表"""
    try:
        # 记录请求参数
        params = request.args.to_dict()
        logger.info(f'[产品列表] 接收到请求参数: {params}')
        
        # 获取分页参数
        page = int(params.get('page', 1))
        page_size = int(params.get('pageSize', 10))
        name = params.get('name')
        code = params.get('code')
        status = params.get('status')
        
        logger.info(f'[产品列表] 解析后的参数: page={page}, page_size={page_size}, name={name}, code={code}, status={status}')
        
        # 调用服务层
        logger.info('[产品列表] 开始调用 ProductService.get_all_products()')
        products = ProductService.get_all_products()
        logger.info(f'[产品列表] ProductService返回原始数据数量: {len(products) if products else 0}')
        
        if products is None:
            logger.error('[产品列表] ProductService返回None')
            return error_response('获取产品列表失败')
            
        # 转换数据
        try:
            response_data = []
            for p in products:
                product_dict = p.to_dict()
                logger.debug(f'[产品列表] 产品数据转换: {product_dict}')
                response_data.append(product_dict)
            
            logger.info(f'[产品列表] 最终返回数据: 总数={len(response_data)}')
            return success_response(data={
                'list': response_data,
                'total': len(response_data),
                'page': page,
                'pageSize': page_size
            })
        except Exception as e:
            logger.error(f'[产品列表] 数据转换失败: {str(e)}')
            logger.error(traceback.format_exc())
            return error_response('数据转换失败')
            
    except Exception as e:
        logger.error(f'[产品列表] 处理请求失败: {str(e)}')
        logger.error(traceback.format_exc())
        return error_response(str(e))

@bp.route('/products/<int:id>', methods=['GET'])
@login_required
def get_product(id):
    """获取单个产品"""
    try:
        logger.info(f'获取产品详情: id={id}')
        product = ProductService.get_product_by_id(id)
        if product:
            return success_response(data=product.to_dict())
        return error_response("产品不存在", code=404)
    except Exception as e:
        logger.error(f'获取产品详情失败: {str(e)}')
        return error_response(str(e))

@bp.route('/products', methods=['POST'])
@login_required
def create_product():
    """创建产品"""
    try:
        logger.info('创建产品')
        data = request.get_json()
        logger.info(f'请求数据: {data}')
        product = ProductService.create_product(data)
        return success_response(data=product.to_dict(), message="创建成功")
    except Exception as e:
        logger.error(f'创建产品失败: {str(e)}')
        return error_response(str(e))

@bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    """更新产品"""
    try:
        logger.info(f'更新产品: id={id}')
        data = request.get_json()
        logger.info(f'请求数据: {data}')
        product = ProductService.update_product(id, data)
        if product:
            return success_response(data=product.to_dict(), message="更新成功")
        return error_response("产品不存在", code=404)
    except Exception as e:
        logger.error(f'更新产品失败: {str(e)}')
        return error_response(str(e))

@bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    """删除产品"""
    try:
        logger.info(f'删除产品: id={id}')
        result = ProductService.delete_product(id)
        if result:
            return success_response(message="删除成功")
        return error_response("产品不存在", code=404)
    except Exception as e:
        logger.error(f'删除产品失败: {str(e)}')
        return error_response(str(e)) 