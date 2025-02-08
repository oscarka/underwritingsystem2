import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    @staticmethod
    def get_database_config():
        """获取数据库配置，根据不同环境返回不同配置"""
        if os.environ.get('FLASK_ENV') == 'development':
            # 开发环境使用 SQLite
            return {
                'url': 'sqlite:///' + os.path.join(basedir, 'app.db'),
                'connect_args': {},
                'engine_options': {
                    'pool_pre_ping': True
                }
            }
        elif os.environ.get('FLASK_ENV') == 'testing':
            # 测试环境使用内存数据库
            return {
                'url': 'sqlite://',
                'connect_args': {},
                'engine_options': {
                    'pool_pre_ping': True
                }
            }
        else:
            # 生产环境使用 Docker 环境变量
            # 构建数据库 URL
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
                'connect_args': {
                    'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT', '10')),
                    'keepalives': int(os.environ.get('DB_KEEPALIVES', '1')),
                    'keepalives_idle': int(os.environ.get('DB_KEEPALIVES_IDLE', '30')),
                    'keepalives_interval': int(os.environ.get('DB_KEEPALIVES_INTERVAL', '10')),
                    'keepalives_count': int(os.environ.get('DB_KEEPALIVES_COUNT', '5')),
                    'client_encoding': os.environ.get('DB_CLIENT_ENCODING', 'utf8'),
                    'application_name': os.environ.get('DB_APPLICATION_NAME', 'underwriting_system'),
                    'sslmode': os.environ.get('DB_SSL_MODE', 'require')
                },
                'engine_options': {
                    'pool_size': int(os.environ.get('DB_POOL_SIZE', '5')),
                    'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '10')),
                    'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
                    'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '1800')),
                    'pool_pre_ping': os.environ.get('DB_POOL_PRE_PING', 'true').lower() == 'true',
                    'echo': os.environ.get('DB_ECHO', 'false').lower() == 'true'
                }
            }
    
    # 获取数据库配置
    db_config = get_database_config()
    SQLALCHEMY_DATABASE_URI = db_config['url']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {**db_config['engine_options'], 'connect_args': db_config['connect_args']}
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
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

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, DevelopmentConfig) 