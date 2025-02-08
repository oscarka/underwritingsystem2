from flask import jsonify
from datetime import datetime

def success_response(data=None, message='success'):
    """成功响应"""
    return jsonify({
        'code': 200,
        'message': message,
        'data': data,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

def error_response(code, message, data=None):
    """错误响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), code 