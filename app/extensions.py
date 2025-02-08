"""Flask扩展实例"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# 数据库ORM扩展
db = SQLAlchemy()  # 用于数据库操作，提供ORM功能

# 数据库迁移扩展
migrate = Migrate()  # 用于处理数据库版本迁移

# 用户登录管理扩展
login_manager = LoginManager()  # 处理用户认证
login_manager.login_view = 'auth.login'  # 设置登录页面的端点 
login_manager.login_message = '请先登录'  # 自定义未登录时的提示消息 