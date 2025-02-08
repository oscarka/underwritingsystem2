from flask import jsonify, request
from app.views.rules import rules
from app.models.rules.conclusion.conclusion import Conclusion
from app.models.rules.conclusion.conclusion_type import ConclusionType
from app import db

@rules.route('/conclusions', methods=['GET'])
def get_conclusions():
    """获取结论列表"""
    conclusions = Conclusion.query.all()
    return jsonify({
        'status': 'success',
        'data': [conclusion.to_dict() for conclusion in conclusions]
    })

@rules.route('/conclusion-types', methods=['GET'])
def get_conclusion_types():
    """获取结论类型列表"""
    types = ConclusionType.query.all()
    return jsonify({
        'status': 'success',
        'data': [t.to_dict() for t in types]
    }) 