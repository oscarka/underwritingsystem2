from typing import List, Optional
from sqlalchemy.sql.expression import or_
from app.extensions import db
from app.models.business.channel import Channel
import logging
import traceback

logger = logging.getLogger(__name__)

class ChannelService:
    """渠道服务"""
    
    @staticmethod
    def get_channel_list(page: int = 1, 
                        page_size: int = 20, 
                        keyword: str = None,
                        status: str = None) -> tuple:
        """获取渠道列表"""
        # 构建查询
        query = Channel.query
        
        # 关键词过滤
        if keyword:
            query = query.filter(
                or_(
                    Channel.name.like(f'%{keyword}%'),
                    Channel.code.like(f'%{keyword}%')
                )
            )
        
        # 状态过滤
        if status:
            query = query.filter(Channel.status == status)
            
        # 分页查询
        pagination = query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )
        
        return pagination.items, pagination.total
    
    @staticmethod
    def get_channel_by_id(channel_id: int) -> Optional[Channel]:
        """根据ID获取渠道"""
        return Channel.query.get(channel_id)
    
    @staticmethod
    def create_channel(data: dict) -> Channel:
        """创建渠道"""
        try:
            logger.info('服务层 - 创建渠道开始，原始数据:')
            for key, value in data.items():
                logger.info(f'  原始数据 - {key}: {value}')
            
            # 检查code唯一性
            if Channel.query.filter_by(code=data.get('code')).first():
                logger.error(f'服务层 - 渠道创建失败: 渠道代码 {data.get("code")} 已存在')
                raise ValueError(f'渠道代码 {data.get("code")} 已存在')
            
            # 确保只包含模型支持的字段
            allowed_fields = {'name', 'code', 'description', 'status'}
            channel_data = {
                k: v for k, v in data.items() 
                if k in allowed_fields and v is not None
            }
            
            logger.info('服务层 - 创建渠道，过滤后的数据:')
            for key, value in channel_data.items():
                logger.info(f'  过滤后 - {key}: {value}')
            
            # 创建渠道实例
            logger.info('服务层 - 准备创建渠道实例，使用的数据:')
            for key, value in channel_data.items():
                logger.info(f'  实例化数据 - {key}: {value}')
            
            channel = Channel(**channel_data)
            logger.info(f'服务层 - 创建渠道实例成功: name={channel.name}, code={channel.code}')
            
            # 保存到数据库
            db.session.add(channel)
            db.session.commit()
            logger.info(f'服务层 - 渠道保存成功: id={channel.id}')
            
            return channel
        except Exception as e:
            logger.error(f'服务层 - 渠道创建失败: {str(e)}')
            logger.error(f'服务层 - 错误类型: {type(e).__name__}')
            logger.error(f'服务层 - 错误详情: {str(e)}')
            logger.error(traceback.format_exc())
            db.session.rollback()
            raise
    
    @staticmethod
    def update_channel(channel_id: int, data: dict) -> Optional[Channel]:
        """更新渠道"""
        channel = Channel.query.get(channel_id)
        if not channel:
            return None
            
        # 更新字段
        if 'name' in data:
            channel.name = data['name']
        if 'description' in data:
            channel.description = data['description']
            
        db.session.commit()
        return channel
    
    @staticmethod
    def update_channel_status(channel_id: int, status: str) -> Optional[Channel]:
        """更新渠道状态"""
        channel = Channel.query.get(channel_id)
        if not channel:
            return None
            
        channel.status = status
        db.session.commit()
        return channel
    
    @staticmethod
    def delete_channel(channel_id: int) -> bool:
        """删除渠道"""
        channel = Channel.query.get(channel_id)
        if not channel:
            return False
            
        db.session.delete(channel)
        db.session.commit()
        return True 