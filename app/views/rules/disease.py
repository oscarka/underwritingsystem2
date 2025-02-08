from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.views.rules import bp
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.base.enums import StatusEnum
from app.extensions import db
from app.models.rules.disease.disease import Disease
from app.models.rules.disease.disease_category import DiseaseCategory
from sqlalchemy import or_

@bp.route('/diseases')
@login_required
def disease_list():
    """疾病列表页面"""
    return render_template('rules/disease/index.html')

@bp.route('/diseases/create')
@login_required
def disease_create():
    """创建疾病页面"""
    return render_template('rules/disease/create.html')

@bp.route('/diseases/edit/<int:id>')
@login_required
def disease_edit(id):
    """编辑疾病页面"""
    disease = Disease.query.get_or_404(id)
    return render_template('rules/disease/edit.html', disease=disease)

@bp.route('/diseases/view/<int:id>')
@login_required
def disease_view(id):
    """查看疾病详情"""
    disease = Disease.query.get_or_404(id)
    return render_template('rules/disease/view.html', disease=disease)

# API路由
@bp.route('/api/diseases/list')
@login_required
def disease_get_list():
    """获取疾病列表"""
    name = request.args.get('name', '')
    category_id = request.args.get('category_id')
    rule_id = request.args.get('rule_id')
    
    query = Disease.query
    if name:
        query = query.filter(Disease.name.like(f'%{name}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if rule_id:
        query = query.filter_by(rule_id=rule_id)
        
    diseases = query.order_by(Disease.created_at.desc()).all()
    return jsonify([disease.to_dict() for disease in diseases])

@bp.route('/api/diseases', methods=['POST'])
@login_required
def disease_create_api():
    """创建疾病"""
    try:
        data = request.get_json()
        
        # 验证数据
        if not data.get('name'):
            return jsonify({'status': 'error', 'message': '疾病名称不能为空'})
        if not data.get('category_id'):
            return jsonify({'status': 'error', 'message': '疾病分类不能为空'})
        if not data.get('rule_id'):
            return jsonify({'status': 'error', 'message': '所属规则不能为空'})
        if not data.get('risk_level'):
            return jsonify({'status': 'error', 'message': '风险等级不能为空'})
            
        # 创建疾病
        disease = Disease(
            name=data['name'],
            category_id=data['category_id'],
            rule_id=data['rule_id'],
            risk_level=data['risk_level'],
            description=data.get('description', '')
        )
        
        # 验证数据
        is_valid, errors = disease.validate_create()
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': '、'.join(errors)
            })
        
        db.session.add(disease)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '创建成功',
            'data': disease.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/api/diseases/<int:id>', methods=['PUT'])
@login_required
def disease_update(id):
    """更新疾病"""
    try:
        disease = Disease.query.get_or_404(id)
        data = request.get_json()
        
        # 验证数据
        if not data.get('name'):
            return jsonify({'status': 'error', 'message': '疾病名称不能为空'})
        if not data.get('category_id'):
            return jsonify({'status': 'error', 'message': '疾病分类不能为空'})
        if not data.get('rule_id'):
            return jsonify({'status': 'error', 'message': '所属规则不能为空'})
        if not data.get('risk_level'):
            return jsonify({'status': 'error', 'message': '风险等级不能为空'})
            
        # 更新数据
        disease.name = data['name']
        disease.category_id = data['category_id']
        disease.rule_id = data['rule_id']
        disease.risk_level = data['risk_level']
        disease.description = data.get('description', '')
        
        # 验证数据
        is_valid, errors = disease.validate_update()
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': '、'.join(errors)
            })
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '更新成功',
            'data': disease.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/api/diseases/<int:id>', methods=['DELETE'])
@login_required
def disease_delete(id):
    """删除疾病"""
    try:
        disease = Disease.query.get_or_404(id)
        db.session.delete(disease)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })