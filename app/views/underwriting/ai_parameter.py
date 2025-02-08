from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.rules.ai.ai_parameter import AIParameter
from app.models.rules.ai.ai_parameter_type import AIParameterType
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.decorators import login_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('ai_parameter', __name__, url_prefix='/api/v1/underwriting/ai-parameter')

@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': 'test ok'
    })

@bp.route('/public/types', methods=['GET'])
def get_public_parameter_types():
    """获取智核参数类型列表(公开接口,用于测试)"""
    logger.info('公开接口 - 开始获取参数类型列表')
    try:
        types = AIParameterType.query.all()
        logger.info(f'公开接口 - 查询到 {len(types)} 个参数类型')
        for t in types:
            logger.info(f'参数类型: id={t.id}, name={t.name}, code={t.code}')
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': [item.to_dict() for item in types]
        })
    except Exception as e:
        logger.error(f'公开接口 - 获取参数类型列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取参数类型列表失败: {str(e)}'
        })

@bp.route('/public', methods=['GET'])
def get_public_parameters():
    """获取智核参数列表(公开接口,用于测试)"""
    try:
        # 获取查询参数
        name = request.args.get('name', '')
        parameter_type_id = request.args.get('parameter_type_id')
        rule_id = request.args.get('rule_id')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        
        logger.info(f'公开接口 - 获取智核参数列表, 参数: name={name}, type_id={parameter_type_id}, rule_id={rule_id}, page={page}, page_size={page_size}')
        
        # 构建查询
        query = AIParameter.query
        if name:
            query = query.filter(AIParameter.name.like(f'%{name}%'))
        if parameter_type_id:
            query = query.filter(AIParameter.parameter_type_id == parameter_type_id)
        if rule_id:
            query = query.filter(AIParameter.rule_id == rule_id)
        
        # 分页查询
        pagination = query.order_by(AIParameter.created_at.desc()).paginate(page=page, per_page=page_size, error_out=False)
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': {
                'list': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pageSize': page_size
            }
        }
        logger.info(f'公开接口 - 获取智核参数列表成功: total={pagination.total}')
        return jsonify(response_data)
    except Exception as e:
        logger.error(f'公开接口 - 获取智核参数列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取参数列表失败: {str(e)}'
        })

@bp.route('/', methods=['GET'])
@login_required
def get_parameters():
    """获取智核参数列表"""
    logger.info('开始获取参数列表')
    try:
        # 记录数据库连接信息
        logger.info(f'数据库URI: {db.engine.url}')
        logger.info(f'数据库连接池状态: {db.engine.pool.status()}')
        
        # 获取查询参数
        name = request.args.get('name', '')
        parameter_type_id = request.args.get('parameter_type_id')
        rule_id = request.args.get('rule_id')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        
        logger.info(f'查询参数: name={name}, type_id={parameter_type_id}, rule_id={rule_id}, page={page}, page_size={page_size}')
        
        # 先检查参数类型表中的数据
        type_count = AIParameterType.query.count()
        logger.info(f'参数类型表中的记录数: {type_count}')
        
        # 检查参数表中的数据
        param_count = AIParameter.query.count()
        logger.info(f'参数表中的记录数: {param_count}')
        
        # 构建查询
        query = AIParameter.query
        if name:
            query = query.filter(AIParameter.name.like(f'%{name}%'))
        if parameter_type_id:
            query = query.filter(AIParameter.parameter_type_id == parameter_type_id)
        if rule_id:
            query = query.filter(AIParameter.rule_id == rule_id)
        
        # 添加SQL日志
        logger.info(f'SQL查询: {query}')
        
        # 分页查询
        pagination = query.order_by(AIParameter.created_at.desc()).paginate(
            page=page, per_page=page_size, error_out=False)
        
        logger.info(f'查询结果: 总数={pagination.total}, 当前页={pagination.page}, 每页条数={page_size}')
        
        # 记录每条数据的详细信息
        for item in pagination.items:
            logger.info(f'参数数据: id={item.id}, name={item.name}, '
                       f'type_id={item.parameter_type_id}, rule_id={item.rule_id}, '
                       f'type_name={item.parameter_type.name if item.parameter_type else "None"}, '
                       f'rule_name={item.rule.name if item.rule else "None"}')
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'list': [item.to_dict() for item in pagination.items],
                'total': pagination.total,
                'page': pagination.page,
                'pageSize': page_size
            }
        })
    except Exception as e:
        logger.error(f'获取参数列表失败: {str(e)}')
        logger.error(f'错误详情: {e.__class__.__name__}', exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'获取参数列表失败: {str(e)}'
        })

@bp.route('/types', methods=['GET'])
@login_required
def get_parameter_types():
    """获取智核参数类型列表"""
    logger.info('开始获取参数类型列表')
    try:
        # 记录请求信息
        logger.info('请求头信息: %s', request.headers)
        
        # 查询数据
        types = AIParameterType.query.all()
        logger.info(f'查询到 {len(types)} 个参数类型')
        
        # 记录每个参数类型的详细信息
        for t in types:
            logger.info('参数类型详情: %s', {
                'id': t.id,
                'name': t.name,
                'code': t.code,
                'value_type': t.value_type,
                'status': t.status
            })
        
        # 转换响应数据
        response_data = {
            'code': 200,
            'message': 'success',
            'data': [item.to_dict() for item in types]
        }
        logger.info('响应数据: %s', response_data)
        
        return jsonify(response_data)
    except Exception as e:
        logger.error('获取参数类型列表失败: %s', str(e), exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'获取参数类型列表失败: {str(e)}'
        })

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_parameter(id):
    """获取智核参数详情"""
    parameter = AIParameter.query.get_or_404(id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': parameter.to_dict()
    })

@bp.route('/', methods=['POST'])
@login_required
def create_parameter():
    """创建智核参数"""
    logger.info('开始创建智核参数')
    try:
        data = request.get_json()
        logger.info('请求数据: %s', data)
        
        # 检查必要字段
        required_fields = ['name', 'parameter_type_id', 'rule_id', 'value']
        for field in required_fields:
            if not data.get(field):
                logger.error(f'缺少必要字段: {field}')
                return jsonify({
                    'code': 400,
                    'message': f'缺少必要字段: {field}'
                })
        
        # 验证参数类型是否存在
        parameter_type = AIParameterType.query.get(data.get('parameter_type_id'))
        if not parameter_type:
            logger.error('参数类型不存在: %s', data.get('parameter_type_id'))
            return jsonify({
                'code': 400,
                'message': '参数类型不存在'
            })
            
        # 验证规则是否存在
        rule = UnderwritingRule.query.get(data.get('rule_id'))
        if not rule:
            logger.error('规则不存在: %s', data.get('rule_id'))
            return jsonify({
                'code': 400,
                'message': '规则不存在'
            })
        
        # 创建参数
        parameter = AIParameter(
            name=data.get('name'),
            parameter_type_id=data.get('parameter_type_id'),
            rule_id=data.get('rule_id'),
            value=data.get('value'),
            description=data.get('description'),
            status=data.get('status', 'enabled')  # 设置默认状态为enabled
        )
        
        # 验证数据
        is_valid, errors = parameter.validate()
        if not is_valid:
            logger.error('参数验证失败: %s', errors)
            return jsonify({
                'code': 400,
                'message': '参数验证失败',
                'data': errors
            })
        
        # 保存数据
        logger.info('开始保存参数数据')
        db.session.add(parameter)
        db.session.commit()
        logger.info('参数创建成功: id=%s, name=%s', parameter.id, parameter.name)
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': parameter.to_dict()
        })
    except Exception as e:
        logger.error('创建参数失败: %s', str(e), exc_info=True)
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建参数失败: {str(e)}'
        })

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_parameter(id):
    """更新智核参数"""
    parameter = AIParameter.query.get_or_404(id)
    data = request.get_json()
    
    # 更新字段
    for key, value in data.items():
        if hasattr(parameter, key):
            setattr(parameter, key, value)
    
    # 验证数据
    is_valid, errors = parameter.validate()
    if not is_valid:
        return jsonify({
            'code': 400,
            'message': '参数验证失败',
            'data': errors
        })
    
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': parameter.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_parameter(id):
    """删除智核参数"""
    parameter = AIParameter.query.get_or_404(id)
    
    try:
        db.session.delete(parameter)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': str(e)
        }) 