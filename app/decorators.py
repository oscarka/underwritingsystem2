from functools import wraps
from flask import request
from app.utils.response import error_response
import jwt
import datetime
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        # 检查是否有Authorization头
        if not auth_header:
            logger.warning("请求未包含Authorization头")
            return error_response(401, '未登录')
            
        # 检查token格式
        try:
            if not auth_header.startswith('Bearer '):
                logger.warning("无效的token格式")
                return error_response(401, '无效的token格式')
                
            token = auth_header.split(' ')[1]
            
            # 验证token
            try:
                payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
                
                # 检查token是否过期
                if 'exp' in payload:
                    exp = datetime.datetime.fromtimestamp(payload['exp'])
                    if exp < datetime.datetime.utcnow():
                        logger.warning("token已过期")
                        return error_response(401, 'token已过期')
                    
                # 设置当前用户信息
                request.current_user = {
                    'user_id': payload.get('id'),  # 使用id字段
                    'username': payload.get('username'),
                    'is_admin': payload.get('is_admin'),
                    'tenant_id': payload.get('tenant_id')
                }
                
                logger.info(f"用户 {payload.get('username')} 的token验证通过")
                return f(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                logger.warning("token已过期")
                return error_response(401, 'token已过期')
            except jwt.InvalidTokenError:
                logger.warning("无效的token")
                return error_response(401, '无效的token')
                
        except Exception as e:
            logger.error(f"验证token时发生错误: {str(e)}")
            return error_response(401, '验证token时发生错误')
            
    return decorated_function 