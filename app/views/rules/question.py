from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.views.rules import bp
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.base.enums import StatusEnum
from app.extensions import db
from app.models.rules.question.question import Question
from app.models.rules.question.question_type import QuestionType
from sqlalchemy import or_

@bp.route('/questions')
@login_required
def question_list():
    """问题列表页面"""
    return render_template('rules/question/index.html')

@bp.route('/questions/create')
@login_required
def question_create():
    """创建问题页面"""
    return render_template('rules/question/create.html')

@bp.route('/questions/edit/<int:id>')
@login_required
def question_edit(id):
    """编辑问题页面"""
    question = Question.query.get_or_404(id)
    return render_template('rules/question/edit.html', question=question)

@bp.route('/questions/view/<int:id>')
@login_required
def question_view(id):
    """查看问题详情"""
    question = Question.query.get_or_404(id)
    return render_template('rules/question/view.html', question=question)

# API路由
@bp.route('/api/questions/list')
@login_required
def question_get_list():
    """获取问题列表"""
    content = request.args.get('content', '')
    type_id = request.args.get('type_id')
    rule_id = request.args.get('rule_id')
    
    query = Question.query
    if content:
        query = query.filter(Question.content.like(f'%{content}%'))
    if type_id:
        query = query.filter_by(type_id=type_id)
    if rule_id:
        query = query.filter_by(rule_id=rule_id)
        
    questions = query.order_by(Question.order.asc(), Question.created_at.desc()).all()
    return jsonify([question.to_dict() for question in questions])

@bp.route('/api/questions', methods=['POST'])
@login_required
def question_create_api():
    """创建问题"""
    try:
        data = request.get_json()
        
        # 验证数据
        if not data.get('content'):
            return jsonify({'status': 'error', 'message': '问题内容不能为空'})
        if not data.get('type_id'):
            return jsonify({'status': 'error', 'message': '问题类型不能为空'})
        if not data.get('rule_id'):
            return jsonify({'status': 'error', 'message': '所属规则不能为空'})
            
        # 创建问题
        question = Question(
            content=data['content'],
            type_id=data['type_id'],
            rule_id=data['rule_id'],
            options=data.get('options', []),
            order=data.get('order', 0),
            required=data.get('required', True)
        )
        
        # 验证数据
        is_valid, errors = question.validate_create()
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': '、'.join(errors)
            })
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '创建成功',
            'data': question.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/api/questions/<int:id>', methods=['PUT'])
@login_required
def question_update(id):
    """更新问题"""
    try:
        question = Question.query.get_or_404(id)
        data = request.get_json()
        
        # 验证数据
        if not data.get('content'):
            return jsonify({'status': 'error', 'message': '问题内容不能为空'})
        if not data.get('type_id'):
            return jsonify({'status': 'error', 'message': '问题类型不能为空'})
        if not data.get('rule_id'):
            return jsonify({'status': 'error', 'message': '所属规则不能为空'})
            
        # 更新数据
        question.content = data['content']
        question.type_id = data['type_id']
        question.rule_id = data['rule_id']
        question.options = data.get('options', [])
        question.order = data.get('order', 0)
        question.required = data.get('required', True)
        
        # 验证数据
        is_valid, errors = question.validate_update()
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': '、'.join(errors)
            })
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '更新成功',
            'data': question.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/api/questions/<int:id>', methods=['DELETE'])
@login_required
def question_delete(id):
    """删除问题"""
    try:
        question = Question.query.get_or_404(id)
        db.session.delete(question)
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