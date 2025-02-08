from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import db
from app.models.business.channel import Channel
from app.models.base.enums import StatusEnum

bp = Blueprint('business', __name__, url_prefix='/business')

@bp.route('/channels')
def channel_list():
    """渠道配置列表"""
    channels = Channel.query.all()
    return render_template('business/channel_list.html', channels=channels)

@bp.route('/channels/add', methods=['POST'])
def add_channel():
    """添加渠道"""
    data = request.get_json()
    
    # 验证数据
    if not data.get('name') or not data.get('code'):
        return jsonify({'status': 'error', 'message': '名称和代码不能为空'})
        
    # 检查代码是否已存在
    if Channel.query.filter_by(code=data['code']).first():
        return jsonify({'status': 'error', 'message': '渠道代码已存在'})
    
    # 创建新渠道
    channel = Channel(
        name=data['name'],
        code=data['code'],
        description=data.get('description'),
        status=StatusEnum.ENABLED.value
    )
    
    try:
        db.session.add(channel)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}) 