import os
from dotenv import load_dotenv
from datetime import timedelta
import logging

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

logger = logging.getLogger(__name__)

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    @staticmethod
    def get_database_config():
        """获取数据库配置，根据不同环境返回不同配置"""
        env = os.environ.get('FLASK_ENV', 'development')
        
        # 测试环境使用内存数据库
        if env == 'testing':
            return {
                'url': 'sqlite://',
                'connect_args': {},
                'engine_options': {
                    'pool_pre_ping': True
                }
            }
            
        # 生产环境 (Railway)
        if env == 'production':
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                logger.error('生产环境缺少 DATABASE_URL')
                raise ValueError('生产环境需要配置 DATABASE_URL')
                
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
                
            safe_url = database_url.replace(database_url.split('@')[0], '****:****')
            logger.info(f'生产环境数据库URL: {safe_url}')
                
            return {
                'url': database_url,
                'connect_args': {'sslmode': 'require'},
                'engine_options': {
                    'pool_size': 5,
                    'pool_recycle': 1800,
                    'pool_pre_ping': True
                }
            }
        
        # 开发环境
        if all(os.environ.get(var) for var in ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']):
            database_url = (
                f"postgresql://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}"
                f"@{os.environ['PGHOST']}:{os.environ['PGPORT']}/{os.environ['PGDATABASE']}"
            )
        else:
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'app.db'))
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        return {
            'url': database_url,
            'connect_args': {},
            'engine_options': {
                'pool_size': 5,
                'pool_recycle': 1800,
                'pool_pre_ping': True
            }
        }
    
    # 获取数据库配置
    db_config = get_database_config.__func__()
    SQLALCHEMY_DATABASE_URI = db_config['url']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {**db_config['engine_options'], 'connect_args': db_config['connect_args']}
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 日志配置
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'true').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True

def get_config():
    return Config 