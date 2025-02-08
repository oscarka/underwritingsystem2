from flask import Blueprint, request, jsonify
from app.models import InsuranceCompany
from app import db
from app.utils.logging import get_logger
from app.decorators import login_required
import logging
import traceback

logger = get_logger(__name__)

bp = Blueprint('company', __name__, url_prefix='/api/v1/business/companies')

@bp.route('', methods=['GET'])
@login_required
def list_companies():
    """获取保司列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        name = request.args.get('name', '')
        code = request.args.get('code', '')
        
        # 构建查询
        query = InsuranceCompany.query
        if name:
            query = query.filter(InsuranceCompany.name.like(f'%{name}%'))
        if code:
            query = query.filter(InsuranceCompany.code.like(f'%{code}%'))
            
        # 计算分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        logger.info(f'获取保司列表成功: 页码={page}, 每页条数={page_size}, 总条数={pagination.total}')
        return jsonify({
            "code": 200,
            "data": {
                "list": [company.to_dict() for company in pagination.items],
                "total": pagination.total,
                "page": page,
                "pageSize": page_size
            },
            "message": "success"
        })
    except Exception as e:
        logger.error(f'获取保司列表失败: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            "code": 500,
            "message": f"获取保司列表失败: {str(e)}"
        }), 500

@bp.route('', methods=['POST'])
@login_required
def create_company():
    """创建新保司"""
    data = request.get_json()
    logger.info(f'创建保司请求数据: {data}')
    
    try:
        # 检查必填字段
        if not data.get('name'):
            return jsonify({
                "code": 400,
                "message": "保司名称不能为空"
            }), 400
        if not data.get('code'):
            return jsonify({
                "code": 400,
                "message": "保司代码不能为空"
            }), 400
            
        # 检查代码是否重复
        if InsuranceCompany.query.filter_by(code=data['code']).first():
            return jsonify({
                "code": 400,
                "message": "保司代码已存在"
            }), 400
            
        company = InsuranceCompany(**data)
        db.session.add(company)
        db.session.commit()
        
        logger.info(f'创建保司成功: {company.to_dict()}')
        return jsonify({
            "code": 200,
            "data": company.to_dict(),
            "message": "success"
        })
    except Exception as e:
        logger.error(f'创建保司失败: {str(e)}\n{traceback.format_exc()}')
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"创建保司失败: {str(e)}"
        }), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_company(id):
    """获取特定保司"""
    try:
        company = InsuranceCompany.query.get_or_404(id)
        logger.info(f'获取保司详情成功: {company.to_dict()}')
        return jsonify({
            "code": 200,
            "data": company.to_dict(),
            "message": "success"
        })
    except Exception as e:
        logger.error(f'获取保司详情失败: {str(e)}\n{traceback.format_exc()}')
        return jsonify({
            "code": 500,
            "message": f"获取保司详情失败: {str(e)}"
        }), 500

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_company(id):
    """更新保司"""
    try:
        company = InsuranceCompany.query.get_or_404(id)
        data = request.get_json()
        logger.info(f'更新保司请求数据: {data}')
        
        # 检查代码是否重复
        if data.get('code') and data['code'] != company.code:
            if InsuranceCompany.query.filter_by(code=data['code']).first():
                return jsonify({
                    "code": 400,
                    "message": "保司代码已存在"
                }), 400
        
        # 过滤掉不允许修改的字段
        valid_fields = {c.name for c in InsuranceCompany.__table__.columns} - {'id', 'created_at', 'updated_at'}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        for key, value in filtered_data.items():
            setattr(company, key, value)
        db.session.commit()
        
        logger.info(f'更新保司成功: {company.to_dict()}')
        return jsonify({
            "code": 200,
            "data": company.to_dict(),
            "message": "success"
        })
    except Exception as e:
        logger.error(f'更新保司失败: {str(e)}\n{traceback.format_exc()}')
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"更新保司失败: {str(e)}"
        }), 500

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_company(id):
    """删除保司"""
    try:
        company = InsuranceCompany.query.get_or_404(id)
        logger.info(f'准备删除保司: {company.to_dict()}')
        
        db.session.delete(company)
        db.session.commit()
        
        logger.info(f'删除保司成功: id={id}')
        return jsonify({
            "code": 200,
            "message": "删除成功"
        })
    except Exception as e:
        logger.error(f'删除保司失败: {str(e)}\n{traceback.format_exc()}')
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"删除保司失败: {str(e)}"
        }), 500 