from flask import request, jsonify
from app.services.business.channel import ChannelService
from app.utils.response import success_response, error_response
from app.decorators import login_required
import traceback
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

channel_service = ChannelService()

@login_required
def get_channels():
    """获取渠道列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')
        
        logger.info(f'获取渠道列表请求参数: page={page}, page_size={page_size}, keyword={keyword}, status={status}')
        
        # 获取数据
        items, total = channel_service.get_channel_list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status
        )
        
        # 返回结果
        result = {
            'list': [item.to_dict() for item in items],
            'pagination': {
                'current': page,
                'pageSize': page_size,
                'total': total
            }
        }
        logger.info(f'获取渠道列表成功: total={total}')
        return success_response(result)
    except Exception as e:
        logger.error(f'获取渠道列表失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'获取渠道列表失败: {str(e)}')

@login_required
def get_channel(id):
    """获取渠道详情"""
    try:
        logger.info(f'获取渠道详情: id={id}')
        channel = channel_service.get_channel_by_id(id)
        if not channel:
            logger.warning(f'渠道不存在: id={id}')
            return error_response(404, '渠道不存在')
        
        logger.info(f'获取渠道详情成功: id={id}')
        return success_response(channel.to_dict())
    except Exception as e:
        logger.error(f'获取渠道详情失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'获取渠道详情失败: {str(e)}')

@login_required
def create_channel():
    """创建渠道"""
    try:
        data = request.get_json()
        logger.info('API层 - 创建渠道，原始请求数据:')
        for key, value in data.items():
            logger.info(f'  {key}: {value}')
        
        # 参数验证
        if not data.get('name'):
            logger.warning('API层 - 创建渠道失败 - 渠道名称为空')
            return error_response(400, '渠道名称不能为空')
        if not data.get('code'):
            logger.warning('API层 - 创建渠道失败 - 渠道代码为空')
            return error_response(400, '渠道代码不能为空')
        
        # 创建渠道
        try:
            channel = channel_service.create_channel(data)
            logger.info(f'API层 - 渠道创建成功: id={channel.id}')
            return success_response(channel.to_dict())
        except Exception as e:
            logger.error(f'API层 - 渠道创建失败: {str(e)}')
            logger.error(traceback.format_exc())
            db.session.rollback()
            return error_response(500, f'创建渠道失败: {str(e)}')
    except Exception as e:
        logger.error(f'API层 - 处理创建渠道请求失败: {str(e)}')
        logger.error(traceback.format_exc())
        return error_response(500, f'处理创建渠道请求失败: {str(e)}')

@login_required
def update_channel(id):
    """更新渠道"""
    try:
        data = request.get_json()
        logger.info(f'更新渠道请求数据: id={id}, data={data}')
        
        channel = channel_service.update_channel(id, data)
        if not channel:
            logger.warning(f'渠道不存在: id={id}')
            return error_response(404, '渠道不存在')
        
        logger.info(f'更新渠道成功: id={id}')
        return success_response(channel.to_dict())
    except Exception as e:
        logger.error(f'更新渠道失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'更新渠道失败: {str(e)}')

@login_required
def update_channel_status(id):
    """更新渠道状态"""
    try:
        data = request.get_json()
        logger.info(f'更新渠道状态请求数据: id={id}, data={data}')
        
        if 'status' not in data:
            return error_response(400, '状态不能为空')
        
        channel = channel_service.update_channel_status(id, data['status'])
        if not channel:
            logger.warning(f'渠道不存在: id={id}')
            return error_response(404, '渠道不存在')
        
        logger.info(f'更新渠道状态成功: id={id}, status={data["status"]}')
        return success_response(channel.to_dict())
    except Exception as e:
        logger.error(f'更新渠道状态失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'更新渠道状态失败: {str(e)}')

@login_required
def delete_channel(id):
    """删除渠道"""
    try:
        logger.info(f'删除渠道: id={id}')
        result = channel_service.delete_channel(id)
        if not result:
            logger.warning(f'渠道不存在: id={id}')
            return error_response(404, '渠道不存在')
        
        logger.info(f'删除渠道成功: id={id}')
        return success_response()
    except Exception as e:
        logger.error(f'删除渠道失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'删除渠道失败: {str(e)}')

def get_public_channels():
    """获取公开渠道列表（测试用）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', '')
        
        logger.info(f'获取公开渠道列表请求参数: page={page}, page_size={page_size}, keyword={keyword}, status={status}')
        
        # 获取数据
        items, total = channel_service.get_channel_list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status
        )
        
        # 返回结果
        result = {
            'list': [item.to_dict() for item in items],
            'pagination': {
                'current': page,
                'pageSize': page_size,
                'total': total
            }
        }
        logger.info(f'获取公开渠道列表成功: total={total}')
        return success_response(result)
    except Exception as e:
        logger.error(f'获取公开渠道列表失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'获取公开渠道列表失败: {str(e)}') 