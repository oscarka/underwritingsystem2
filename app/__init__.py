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
        database_url = os.environ.get('RAILWAY_DATABASE_URL') or os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(app.root_path, 'app.db'))
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info(f'尝试连接数据库: {database_url}')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ECHO'] = True
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,  # 减小连接池大小
            'max_overflow': 10,  # 减小最大溢出连接数
            'pool_timeout': 30,  # 连接池超时时间
            'pool_recycle': 1800,  # 连接回收时间改为30分钟
            'pool_pre_ping': True,  # 启用连接池预检
            'connect_args': {
                'connect_timeout': 10,  # 连接超时时间
                'keepalives': 1,  # 启用 TCP keepalive
                'keepalives_idle': 30,  # TCP keepalive 空闲时间
                'keepalives_interval': 10,  # TCP keepalive 间隔
                'keepalives_count': 5  # TCP keepalive 重试次数
            }
        }
        
        # 初始化数据库和迁移
        db.init_app(app)
        migrate.init_app(app, db)
        
        with app.app_context():
            # 检查数据库连接
            try:
                db.engine.connect().close()
                logger.info('数据库连接测试成功')
                
                # 检查表是否存在
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                if not existing_tables:
                    logger.info('数据库表不存在，开始创建...')
                    db.create_all()
                    logger.info('数据库表创建完成')
                else:
                    logger.info(f'发现现有表: {", ".join(existing_tables)}')
            except Exception as conn_error:
                logger.error(f'数据库连接测试失败: {str(conn_error)}')
                raise
                
        logger.info('数据库初始化完成')
        
    except Exception as e:
        logger.error(f'数据库初始化失败: {str(e)}')
        logger.error(f'错误类型: {type(e).__name__}')
        if hasattr(e, '__dict__'):
            logger.error(f'错误详情: {str(e.__dict__)}')
        if os.environ.get('FLASK_ENV') == 'production':
            logger.error('生产环境数据库连接失败，终止应用启动')
            raise
        else:
            logger.warning('切换到SQLite数据库...')
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'app.db')
            db.init_app(app)
            migrate.init_app(app, db)
    
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