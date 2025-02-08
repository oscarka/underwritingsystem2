"""Rules views package."""
from flask import Blueprint

bp = Blueprint('rules', __name__)

def init_app(app):
    # 导入视图模块
    from .underwriting import bp as underwriting_bp
    from .disease import bp as disease_bp
    from .question import bp as question_bp
    from .import_views import bp as import_bp
    from . import routes
    
    # 注册核保规则蓝图
    app.register_blueprint(underwriting_bp, url_prefix='/rules/underwriting')
    
    # 注册疾病蓝图
    app.register_blueprint(disease_bp, url_prefix='/rules/disease')
    
    # 注册问题蓝图
    app.register_blueprint(question_bp, url_prefix='/rules/question')
    
    # 注册导入蓝图
    app.register_blueprint(import_bp, url_prefix='/rules')

    # 注册主蓝图
    app.register_blueprint(bp, url_prefix='/rules')

# 导入视图函数
from app.views.rules.underwriting import *
from app.views.rules.disease import *
from app.views.rules.question import * 