from flask import Blueprint, request
from app.utils.response import success_response, error_response
from app.models.business.product.product_type import ProductType
from app.decorators import login_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('product_type', __name__)

@bp.route('/product-types', methods=['GET'])
@login_required
def get_product_types():
    """获取产品类型列表"""
    try:
        logger.info('[产品类型] 开始获取产品类型列表')
        product_types = ProductType.query.all()
        logger.info(f'[产品类型] 查询到 {len(product_types)} 条记录')
        
        # 转换数据
        type_list = []
        for pt in product_types:
            type_dict = pt.to_dict()
            logger.debug(f'[产品类型] 数据转换: {type_dict}')
            type_list.append(type_dict)
            
        logger.info(f'[产品类型] 返回数据总数: {len(type_list)}')
        return success_response(data={
            'list': type_list,
            'total': len(type_list),
            'page': 1,
            'pageSize': len(type_list)
        })
    except Exception as e:
        logger.error(f'[产品类型] 获取产品类型列表失败: {str(e)}')
        return error_response(str(e))

@bp.route('/product-types/<int:id>', methods=['GET'])
@login_required
def get_product_type(id):
    """获取单个产品类型"""
    try:
        logger.info(f'[产品类型] 获取产品类型详情: id={id}')
        product_type = ProductType.query.get_or_404(id)
        return success_response(data=product_type.to_dict())
    except Exception as e:
        logger.error(f'[产品类型] 获取产品类型详情失败: {str(e)}')
        return error_response(str(e)) 