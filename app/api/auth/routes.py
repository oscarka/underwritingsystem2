from flask import jsonify, request
from flask_login import login_user, logout_user, login_required
from app.models.auth.user import User
from app.utils.response import success_response, error_response
from . import bp
import jwt
import datetime
import logging

logger = logging.getLogger(__name__)

@bp.route('/login', methods=['POST', 'HEAD'])
def login():
    if request.method == 'HEAD':
        return '', 200
        
    try:
        logger.info("收到登录请求")
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"用户尝试登录: {username}")
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"用户 {username} 登录成功")
            
            # 生成JWT token
            token = jwt.encode({
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
                'tenant_id': user.tenant_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, 'your-secret-key', algorithm='HS256')
            
            return success_response(data={
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'is_admin': user.is_admin,
                    'tenant_id': user.tenant_id
                }
            }, message="登录成功")
            
        logger.warning(f"用户 {username} 登录失败：用户名或密码错误")
        return error_response(message="用户名或密码错误", code=401)
        
    except Exception as e:
        logger.error(f"登录过程发生错误: {str(e)}")
        return error_response(message="登录失败", code=500)

@bp.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        logger.info("用户已退出登录")
        return success_response(message="退出成功")
    except Exception as e:
        logger.error(f"退出登录时发生错误: {str(e)}")
        return error_response(str(e)) 