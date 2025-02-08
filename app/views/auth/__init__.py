from flask import Blueprint

bp = Blueprint('auth_view', __name__, url_prefix='/auth')

from . import views 