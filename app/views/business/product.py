from flask import Blueprint, jsonify, request
from app.decorators import login_required
from app.models.business.product.product import Product
from sqlalchemy import or_
from app import db
from app.utils.logging import get_logger

logger = get_logger(__name__)

bp = Blueprint('product', __name__, url_prefix='/api/v1/business/products')

@bp.route('/', methods=['GET'])
@login_required
def get_products():
    """获取产品列表
    
    Query参数:
    - page: 页码，默认1
    - pageSize: 每页条数，默认10
    - code: 产品编码，模糊匹配
    - channel: 渠道筛选
    - status: 状态筛选
    """
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        code = request.args.get('code', '')
        channel = request.args.get('channel', '')
        status = request.args.get('status', '')
        
        logger.info(f'获取产品列表, 参数: page={page}, pageSize={page_size}, code={code}, channel={channel}, status={status}')
        
        # 构建查询
        query = Product.query\
            .outerjoin(Product.channel)\
            .outerjoin(Product.product_type)\
            .outerjoin(Product.insurance_company)\
            .outerjoin(Product.ai_parameter)
        if code:
            query = query.filter(Product.product_code.like(f'%{code}%'))
        if channel:
            query = query.filter(Product.channel_id == channel)
        if status:
            query = query.filter(Product.status == status)
            
        # 执行分页查询
        pagination = query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )
        
        # 转换数据
        products = [{
            'id': p.id,
            'name': p.name,
            'code': p.product_code,
            'productType': {
                'id': p.product_type.id,
                'name': p.product_type.name,
                'code': p.product_type.code
            } if p.product_type else None,
            'insuranceCompany': {
                'id': p.insurance_company.id,
                'name': p.insurance_company.name,
                'code': p.insurance_company.code
            } if p.insurance_company else None,
            'channel': {
                'id': p.channel.id,
                'name': p.channel.name,
                'code': p.channel.code
            } if p.channel else None,
            'aiParameter': {
                'id': p.ai_parameter.id,
                'name': p.ai_parameter.name,
                'rule': {
                    'id': p.ai_parameter.rule.id,
                    'name': p.ai_parameter.rule.name
                } if hasattr(p.ai_parameter, 'rule') and p.ai_parameter.rule else None
            } if p.ai_parameter else None,
            'status': p.status,
            'createdAt': p.created_at_str,
            'updatedAt': p.updated_at_str
        } for p in pagination.items]
        
        logger.info(f'获取产品列表成功, 总数: {pagination.total}')
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'list': products,
                'total': pagination.total,
                'page': page,
                'pageSize': page_size
            }
        })
    except Exception as e:
        logger.error(f'获取产品列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取产品列表失败: {str(e)}'
        })

@bp.route('/', methods=['POST'])
@login_required
def create_product():
    """创建产品
    
    请求体:
    {
        "code": "PRODUCT_001",  # 必填，产品编码，大写字母数字下划线
        "channel": "CHANNEL_001",  # 必填，渠道编码
        "underwritingRule": "RULE_001",  # 必填，核保规则编码
        "description": "产品描述",  # 可选
        "status": "enabled"  # 可选，默认enabled
    }
    """
    try:
        data = request.get_json()
        logger.info(f'创建产品, 数据: {data}')
        
        # 参数验证
        if not data.get('code'):
            return jsonify({
                'code': 400,
                'message': '产品编码不能为空'
            })
        if not data.get('channel'):
            return jsonify({
                'code': 400,
                'message': '渠道不能为空'
            })
            
        # 检查编码是否已存在
        if Product.query.filter_by(product_code=data['code']).first():
            return jsonify({
                'code': 400,
                'message': '产品编码已存在'
            })
            
        # 创建产品
        product = Product(
            product_code=data['code'],
            channel_id=data['channel'],
            status=data.get('status', 'enabled')
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f'创建产品成功: {product.id}')
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': {
                'id': product.id,
                'code': product.product_code,
                'channel': product.channel.code if product.channel else None,
                'status': product.status,
                'createdAt': product.created_at_str,
                'updatedAt': product.updated_at_str
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'创建产品失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'创建产品失败: {str(e)}'
        })

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    """更新产品"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({
                'code': 404,
                'message': '产品不存在'
            })
            
        data = request.get_json()
        logger.info(f'更新产品 {id}, 数据: {data}')
        
        # 更新字段
        if 'channel' in data:
            product.channel_id = data['channel']
        if 'description' in data:
            product.description = data['description']
        if 'status' in data:
            product.status = data['status']
            
        db.session.commit()
        
        logger.info(f'更新产品成功: {id}')
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': product.id,
                'code': product.product_code,
                'channel': product.channel.code if product.channel else None,
                'status': product.status,
                'createdAt': product.created_at_str,
                'updatedAt': product.updated_at_str
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'更新产品失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'更新产品失败: {str(e)}'
        })

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    """删除产品"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({
                'code': 404,
                'message': '产品不存在'
            })
            
        logger.info(f'删除产品: {id}')
        
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f'删除产品成功: {id}')
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除产品失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'删除产品失败: {str(e)}'
        })