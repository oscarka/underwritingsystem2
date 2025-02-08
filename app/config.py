import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('RAILWAY_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # 数据库配置
    if all(os.environ.get(var) for var in ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE']):
        # 使用Railway标准PostgreSQL环境变量
        database_url = (
            f"postgresql://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}"
            f"@{os.environ['PGHOST']}:{os.environ['PGPORT']}/{os.environ['PGDATABASE']}"
        )
    else:
        # 回退到DATABASE_URL
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'app.db'))
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLAlchemy连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'application_name': 'underwriting_system',
            'client_encoding': 'utf8',
            'sslmode': 'require'
        }
    }
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # 文件上传配置
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
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, DevelopmentConfig) 