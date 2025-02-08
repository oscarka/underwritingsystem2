from flask import jsonify, request
from app.views.rules import rules
from app.models.rules.ai.ai_parameter import AIParameter
from app.models.rules.ai.ai_parameter_type import AIParameterType
from app import db
from flask_login import login_required

@rules.route('/ai/parameters')
@login_required
def ai_parameter_list():
    """AI参数列表页面"""
    return render_template('rules/ai/parameters.html')

@rules.route('/api/ai/parameters', methods=['GET'])
@login_required
def get_ai_parameters():
    """获取AI参数列表"""
    parameters = AIParameter.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'rule': p.rule.name if p.rule else '',
        'tenant': p.tenant.name if p.tenant else ''
    } for p in parameters])

@rules.route('/ai-parameter-types', methods=['GET'])
def get_ai_parameter_types():
    """获取AI参数类型列表"""
    types = AIParameterType.query.all()
    return jsonify({
        'status': 'success',
        'data': [t.to_dict() for t in types]
    }) 