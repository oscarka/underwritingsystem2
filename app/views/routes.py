from flask import jsonify
from app.views import main

@main.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Service is running'
    }) 