import os
from flask import Flask, jsonify, redirect, url_for, send_from_directory
from flask_cors import CORS
from app.config import get_config
from app.logging import init_logging
from app.extensions import db, login_manager, migrate
from app.api.business import bp as business_bp
from app.api.auth import bp as auth_bp
from app.views.business import init_app as init_business_views
from app.views.underwriting import bp as underwriting_bp
from app.views.underwriting.ai_parameter import bp as ai_parameter_bp
from app.models.auth.user import User
import logging
from logging.handlers import RotatingFileHandler
import psutil
from sqlalchemy import text, inspect
import psycopg2
from urllib.parse import urlparse
import sqlalchemy as sa
import time

logger = logging.getLogger(__name__)

def create_app(config_class=None):
    logger.info('开始创建Flask应用...')
    app = Flask(__name__, static_folder='static')
    
    # 配置基础设置
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    logger.info(f'已加载配置: {config_class.__name__}')
    
    # 初始化日志
    init_logging(app)
    logger.info('日志系统初始化完成')
    
    # 添加健康检查端点 (最优先)
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Service is healthy"
        }), 200
    
    # 添加根路由
    @app.route('/')
    def index():
        return jsonify({
            "status": "ok",
            "message": "Service is running"
        }), 200
    
    # 添加静态文件路由
    @app.route('/admin')
    @app.route('/admin/')
    def admin_index():
        return send_from_directory('static/admin', 'index.html')
    
    @app.route('/login.html')
    def login_page():
        return send_from_directory('static/admin', 'index.html')
    
    @app.route('/admin/<path:path>')
    def serve_admin(path):
        return send_from_directory('static/admin', path)
    
    # 移动端资源文件路由
    @app.route('/product/assets/<path:path>')
    def serve_mobile_assets(path):
        return send_from_directory('static/mobile/assets', path)
        
    # 移动端产品路由
    @app.route('/product/<path:path>')
    def serve_mobile_product(path=None):
        return send_from_directory('static/mobile', 'index.html')
    
    # 配置 CORS
    CORS(app)
    logger.info('CORS配置完成')
    
    # 确保上传目录存在
    upload_dir = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        logger.info(f'创建上传目录: {upload_dir}')
    
    # 配置数据库
    try:
        logger.info('初始化数据库...')
        db.init_app(app)
        migrate.init_app(app, db)
        logger.info('数据库和迁移初始化完成')
        
        with app.app_context():
            if os.environ.get('FLASK_DEBUG') == '0':  # 生产环境
                # 生产环境 (Railway)
                retry_count = 3
                for attempt in range(retry_count):
                    try:
                        conn = db.engine.connect()
                        result = conn.execute(sa.text('SELECT 1')).scalar()
                        conn.close()
                        logger.info('数据库连接成功')
                        break
                    except Exception as e:
                        if attempt == retry_count - 1:
                            logger.error(f'数据库连接失败: {str(e)}')
                            raise
                        logger.warning(f'第 {attempt + 1} 次连接尝试失败，将重试...')
                        time.sleep(2)
                
                # 检查数据库表
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                logger.info(f'现有数据库表: {", ".join(tables)}')
            else:
                # 开发环境保持原有逻辑
                database_url = os.environ.get('RAILWAY_DATABASE_URL') or os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(app.root_path, 'app.db'))
                if database_url.startswith('postgres://'):
                    database_url = database_url.replace('postgres://', 'postgresql://', 1)
                
                # 检查是否有单独设置的数据库密码
                postgres_password = os.environ.get('POSTGRES_PASSWORD')
                
                # 解析数据库URL
                parsed = urlparse(database_url)
                
                # 如果没有用户名，使用默认用户名
                if not parsed.username:
                    logger.info('未检测到用户名，使用默认用户名postgres')
                    parsed = parsed._replace(username='postgres')
                
                # 使用环境变量中的密码或URL中的密码
                db_password = postgres_password if postgres_password else parsed.password
                if not db_password:
                    logger.error('未找到数据库密码')
                    raise ValueError('数据库密码未设置')
                
                # 重构数据库URL
                database_url = f"postgresql://{parsed.username}:{db_password}@{parsed.hostname}:{parsed.port or 5432}{parsed.path}"
                
                app.config['SQLALCHEMY_DATABASE_URI'] = database_url
                db.init_app(app)
                
                # 测试连接
                conn = db.engine.connect()
                result = conn.execute(sa.text('SELECT 1')).scalar()
                conn.close()
                logger.info('数据库连接成功')
    
    except Exception as e:
        logger.error(f'数据库初始化失败: {str(e)}')
        if hasattr(e, 'orig'):
            logger.error(f'原始错误: {e.orig}')
        if os.environ.get('FLASK_ENV') == 'production':
            raise
        else:
            logger.warning('切换到SQLite数据库...')
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'app.db')
            db.init_app(app)
    
    # 初始化其他扩展
    try:
        login_manager.init_app(app)
        logger.info('扩展初始化完成')
    except Exception as e:
        logger.error(f'扩展初始化失败: {str(e)}')
    
    # 配置user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册错误处理器
    from app.errors import not_found_error, internal_error
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)
    logger.info('错误处理器注册完成')
    
    # 注册主蓝图
    from app.views import main
    app.register_blueprint(main)
    logger.info('主蓝图注册完成')
    
    # 注册智核参数蓝图
    logger.info(f'开始注册智核参数蓝图: name={ai_parameter_bp.name}, url_prefix={ai_parameter_bp.url_prefix}')
    app.register_blueprint(ai_parameter_bp)
    logger.info('智核参数蓝图注册完成')
    
    # 注册认证API蓝图
    logger.info(f'开始注册认证API蓝图: name={auth_bp.name}, url_prefix=/api/auth')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    logger.info('认证API蓝图注册完成')
    
    # 注册业务API蓝图
    logger.info(f'开始注册业务API蓝图: name={business_bp.name}, url_prefix=/api/v1/business')
    app.register_blueprint(business_bp, url_prefix='/api/v1/business')
    logger.info('业务API蓝图注册完成')
    
    # 注册视图蓝图
    logger.info('开始注册业务视图蓝图...')
    init_business_views(app)
    logger.info('业务视图蓝图注册完成')

    # 注册核保规则蓝图
    logger.info(f'开始注册核保规则蓝图: name={underwriting_bp.name}, url_prefix=/api/v1/underwriting')
    app.register_blueprint(underwriting_bp, url_prefix='/api/v1/underwriting')
    logger.info('核保规则蓝图注册完成')

    # 配置日志
    if not app.debug and not app.testing:
        if os.environ.get('LOG_TO_STDOUT', 'true').lower() == 'true':
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                'logs/app.log',
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('应用启动')
    
    logger.info('应用初始化完成')
    return app

# 创建应用实例
app = create_app() 