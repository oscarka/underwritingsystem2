from flask import jsonify
from app.utils.response import error_response

def not_found_error(error):
    """404错误处理"""
    return error_response(404, '资源不存在')

def internal_error(error):
    """500错误处理"""
    return error_response(500, '服务器内部错误')

# 导出错误处理器
__all__ = ['not_found_error', 'internal_error']

# 确保这些函数可以被导入
if __name__ != '__main__':
    from app.extensions import db  # 导入数据库实例用于回滚 