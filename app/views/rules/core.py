from flask import jsonify, request, render_template
from flask_login import login_required
from app.views.rules import bp
from app.models import UnderwritingRule
from app.models.base.enums import StatusEnum
from app.extensions import db

@bp.route('/rules')
@login_required
def rule_list():
    """规则列表页面"""
    # 获取查询参数
    filters = {}
    name = request.args.get('name')
    version = request.args.get('version')
    status = request.args.get('status')
    
    if name:
        filters['name'] = name
    if version:
        filters['version'] = version
    if status:
        filters['status'] = status
        
    # 获取规则列表
    query = UnderwritingRule.query
    if filters.get('name'):
        query = query.filter(UnderwritingRule.name.like(f"%{filters['name']}%"))
    if filters.get('version'):
        query = query.filter(UnderwritingRule.version.like(f"%{filters['version']}%"))
    if filters.get('status'):
        query = query.filter(UnderwritingRule.status == filters['status'])
    
    rules = query.order_by(UnderwritingRule.created_at.desc()).all()
    
    return render_template('rules/rule_list.html', rules=rules)

@bp.route('/rules/create')
@login_required
def create_rule():
    """创建规则页面"""
    return render_template('rules/rule_create.html')

@bp.route('/api/rules', methods=['GET'])
@login_required
def get_rules():
    """获取规则列表API"""
    filters = {}
    name = request.args.get('name')
    version = request.args.get('version')
    status = request.args.get('status')
    
    if name:
        filters['name'] = name
    if version:
        filters['version'] = version
    if status:
        filters['status'] = status
        
    query = UnderwritingRule.query
    if filters.get('name'):
        query = query.filter(UnderwritingRule.name.like(f"%{filters['name']}%"))
    if filters.get('version'):
        query = query.filter(UnderwritingRule.version.like(f"%{filters['version']}%"))
    if filters.get('status'):
        query = query.filter(UnderwritingRule.status == filters['status'])
    
    rules = query.order_by(UnderwritingRule.created_at.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [rule.to_dict() for rule in rules]
    })

@bp.route('/api/rules', methods=['POST'])
@login_required
def create_rule_api():
    """创建规则API"""
    data = request.get_json()
    
    # 创建新规则
    rule = UnderwritingRule(
        name=data.get('name'),
        version=data.get('version'),
        description=data.get('description'),
        status=StatusEnum.DRAFT.value
    )
    
    try:
        db.session.add(rule)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': '创建成功',
            'data': rule.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/api/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """更新规则"""
    data = request.get_json()
    rule, error = UnderwritingRuleService.update_rule(rule_id, data)
    
    if error:
        return jsonify({
            'status': 'error',
            'message': error
        })
        
    return jsonify({
        'status': 'success',
        'message': '更新成功',
        'data': rule.to_dict()
    })

@bp.route('/api/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """删除规则"""
    success, error = UnderwritingRuleService.delete_rule(rule_id)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': error
        })
        
    return jsonify({
        'status': 'success',
        'message': '删除成功'
    })

@bp.route('/rules/<int:rule_id>')
def view_rule(rule_id):
    """查看规则"""
    rule = UnderwritingRuleService.get_rule_by_id(rule_id)
    if not rule:
        return render_template('errors/404.html'), 404
    return render_template('rules/rule_view.html', rule=rule)

@bp.route('/api/rules/<int:rule_id>/status', methods=['PUT'])
def update_rule_status(rule_id):
    """更新规则状态"""
    data = request.get_json()
    status = data.get('status')
    
    if not status:
        return jsonify({
            'status': 'error',
            'message': '状态不能为空'
        })
        
    rule, error = UnderwritingRuleService.update_rule_status(rule_id, status)
    
    if error:
        return jsonify({
            'status': 'error',
            'message': error
        })
        
    return jsonify({
        'status': 'success',
        'message': '状态更新成功',
        'data': rule.to_dict()
    })

@bp.route('/api/rules/<int:rule_id>/diseases', methods=['PUT'])
def associate_diseases(rule_id):
    """关联疾病到规则"""
    data = request.get_json()
    disease_ids = data.get('disease_ids', [])
    
    if not disease_ids:
        return jsonify({
            'status': 'error',
            'message': '疾病ID列表不能为空'
        })
        
    success, error = UnderwritingRuleService.associate_diseases(rule_id, disease_ids)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': error
        })
        
    return jsonify({
        'status': 'success',
        'message': '疾病关联成功'
    })

@bp.route('/api/rules/<int:rule_id>/export', methods=['GET'])
def export_rule(rule_id):
    """导出规则"""
    data, error = UnderwritingRuleService.export_rule(rule_id)
    
    if error:
        return jsonify({
            'status': 'error',
            'message': error
        })
        
    return jsonify({
        'status': 'success',
        'data': data
    })

@bp.route('/api/rules/import', methods=['POST'])
def import_rule():
    """导入规则"""
    data = request.get_json()
    rule, error = UnderwritingRuleService.import_rule(data)
    
    if error:
        return jsonify({
            'status': 'error',
            'message': error
        })
        
    return jsonify({
        'status': 'success',
        'message': '导入成功',
        'data': rule.to_dict()
    }) 