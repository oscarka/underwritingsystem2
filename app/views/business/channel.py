from flask import Blueprint, request, jsonify
from app.models.business.channel import Channel
from app import db
from app.utils.logging import get_logger
from app.decorators import login_required
import logging

logger = get_logger(__name__)

bp = Blueprint('channel', __name__, url_prefix='/api/v1/business/channels')

@bp.route('/', methods=['GET'])
@login_required
def list_channels():
    """获取渠道列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    # 计算分页
    pagination = Channel.query.paginate(page=page, per_page=page_size, error_out=False)
    
    return jsonify({
        "code": 200,
        "data": {
            "list": [channel.to_dict() for channel in pagination.items],
            "total": pagination.total,
            "page": page,
            "pageSize": page_size
        },
        "message": "success"
    })

@bp.route('/', methods=['POST'])
@login_required
def create_channel():
    """创建新渠道"""
    data = request.get_json()
    try:
        channel = Channel(**data)
        db.session.add(channel)
        db.session.commit()
        return jsonify({
            "code": 200,
            "data": channel.to_dict(),
            "message": "success"
        })
    except Exception as e:
        logger.error(f"创建渠道失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            "code": 400,
            "message": f"创建渠道失败: {str(e)}"
        }), 400

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_channel(id):
    """获取特定渠道"""
    channel = Channel.query.get_or_404(id)
    return jsonify({
        "code": 200,
        "data": channel.to_dict(),
        "message": "success"
    })

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_channel(id):
    """更新渠道"""
    channel = Channel.query.get_or_404(id)
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(channel, key, value)
        db.session.commit()
        return jsonify({
            "code": 200,
            "data": channel.to_dict(),
            "message": "success"
        })
    except Exception as e:
        logger.error(f"更新渠道失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            "code": 400,
            "message": f"更新渠道失败: {str(e)}"
        }), 400

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_channel(id):
    """删除渠道"""
    channel = Channel.query.get_or_404(id)
    try:
        db.session.delete(channel)
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "删除成功"
        })
    except Exception as e:
        logger.error(f"删除渠道失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            "code": 400,
            "message": f"删除渠道失败: {str(e)}"
        }), 400
