"""Views package."""
from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    """主页"""
    return render_template('dashboard.html')

# 导入路由
from . import routes 