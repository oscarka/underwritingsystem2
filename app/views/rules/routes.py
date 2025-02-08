from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.rules.core.rule_version import RuleVersion
from app.models.base.enums import StatusEnum
from app.models.rules.ai.ai_parameter import AIParameter
from app.models.rules.ai.ai_parameter_type import AIParameterType
from app.extensions import db
from flask_login import login_required
from app.models.rules.disease.disease_category import DiseaseCategory
from app.models.rules.disease.disease import Disease

# 导入视图模块
from . import underwriting
from . import disease
from . import question

bp = Blueprint('rules', __name__)

@bp.route('/')
@login_required
def index():
    """规则列表页面"""
    return redirect(url_for('rules.underwriting_list'))

@bp.route('/rules')
@login_required
def rules_redirect():
    """重定向到核保规则列表"""
    return redirect(url_for('rules.underwriting_list'))

@bp.route('/list')
@login_required
def get_list():
    """获取规则列表"""
    rules = UnderwritingRule.query.all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'version': r.version,
        'status': r.status,
        'questions_count': len(r.questions),
        'diseases_count': len(r.diseases),
        'conclusions_count': len(r.conclusions)
    } for r in rules])

@bp.route('/ai-parameters')
@login_required
def ai_parameters():
    """智核参数配置列表"""
    rule_versions = RuleVersion.query.all()
    return render_template('rules/ai_parameter_list.html', rule_versions=rule_versions)

@bp.route('/rules/add', methods=['POST'])
@login_required
def add_rule():
    """添加核保规则"""
    data = request.get_json()
    
    # 验证数据
    if not data.get('name') or not data.get('version'):
        return jsonify({'status': 'error', 'message': '名称和版本不能为空'})
    
    # 创建新规则
    rule = UnderwritingRule(
        name=data['name'],
        version=data['version'],
        description=data.get('description'),
        status=StatusEnum.ENABLED.value
    )
    
    try:
        db.session.add(rule)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

@bp.route('/parameters/add', methods=['POST'])
@login_required
def add_parameter():
    """添加智核参数"""
    data = request.get_json()
    
    # 验证数据
    if not data.get('name') or not data.get('value'):
        return jsonify({'status': 'error', 'message': '名称和参数值不能为空'})
    
    # 创建新参数
    parameter = AIParameter(
        name=data['name'],
        parameter_type_id=data['parameter_type_id'],
        rule_version_id=data['rule_version_id'],
        value=data['value'],
        status=StatusEnum.ENABLED.value
    )
    
    try:
        db.session.add(parameter)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})

# 疾病分类列表页面
@bp.route('/disease/categories')
def disease_category_list():
    return render_template('rules/disease/category_list.html')

# 获取疾病分类列表
@bp.route('/api/disease/categories')
def list_disease_categories():
    try:
        # 获取查询参数
        name = request.args.get('name', '')
        code = request.args.get('code', '')
        status = request.args.get('status', '')
        
        # 构建查询
        query = DiseaseCategory.query
        if name:
            query = query.filter(DiseaseCategory.name.like(f'%{name}%'))
        if code:
            query = query.filter(DiseaseCategory.code.like(f'%{code}%'))
        if status:
            query = query.filter(DiseaseCategory.status == status)
            
        # 按创建时间倒序排序
        categories = query.order_by(DiseaseCategory.created_at.desc()).all()
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 创建疾病分类
@bp.route('/api/disease/categories', methods=['POST'])
def create_disease_category():
    try:
        data = request.get_json()
        category = DiseaseCategory(
            name=data.get('name'),
            code=data.get('code'),
            description=data.get('description'),
            status=data.get('status')
        )
        
        # 验证数据
        is_valid, errors = category.validate_create()
        if not is_valid:
            return jsonify({
                'code': 1,
                'message': '、'.join(errors)
            })
            
        # 保存数据
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': category.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 获取疾病分类详情
@bp.route('/api/disease/categories/<int:id>')
def get_disease_category(id):
    try:
        category = DiseaseCategory.query.get(id)
        if not category:
            return jsonify({
                'code': 1,
                'message': '分类不存在'
            })
            
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': category.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 更新疾病分类
@bp.route('/api/disease/categories/<int:id>', methods=['PUT'])
def update_disease_category(id):
    try:
        category = DiseaseCategory.query.get(id)
        if not category:
            return jsonify({
                'code': 1,
                'message': '分类不存在'
            })
            
        data = request.get_json()
        category.name = data.get('name')
        category.code = data.get('code')
        category.description = data.get('description')
        category.status = data.get('status')
        
        # 验证数据
        is_valid, errors = category.validate_update()
        if not is_valid:
            return jsonify({
                'code': 1,
                'message': '、'.join(errors)
            })
            
        # 保存数据
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': category.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 删除疾病分类
@bp.route('/api/disease/categories/<int:id>', methods=['DELETE'])
def delete_disease_category(id):
    try:
        category = DiseaseCategory.query.get(id)
        if not category:
            return jsonify({
                'code': 1,
                'message': '分类不存在'
            })
            
        # 检查是否有关联的疾病
        if category.diseases.count() > 0:
            return jsonify({
                'code': 1,
                'message': '该分类下存在疾病，无法删除'
            })
            
        # 删除数据
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 疾病列表页面
@bp.route('/diseases')
def disease_list():
    return render_template('rules/disease/disease_list.html')

# 获取疾病列表
@bp.route('/api/diseases')
def list_diseases():
    try:
        # 获取查询参数
        name = request.args.get('name', '')
        category_id = request.args.get('category_id', type=int)
        risk_level = request.args.get('risk_level', '')
        status = request.args.get('status', '')
        
        # 构建查询
        query = Disease.query
        if name:
            query = query.filter(Disease.name.like(f'%{name}%'))
        if category_id:
            query = query.filter(Disease.category_id == category_id)
        if risk_level:
            query = query.filter(Disease.risk_level == risk_level)
        if status:
            query = query.filter(Disease.status == status)
            
        # 按创建时间倒序排序
        diseases = query.order_by(Disease.created_at.desc()).all()
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': [disease.to_dict() for disease in diseases]
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 创建疾病
@bp.route('/api/diseases', methods=['POST'])
def create_disease():
    try:
        data = request.get_json()
        disease = Disease(
            name=data.get('name'),
            category_id=data.get('category_id'),
            risk_level=data.get('risk_level'),
            description=data.get('description'),
            status=data.get('status')
        )
        
        # 验证数据
        is_valid, errors = disease.validate_create()
        if not is_valid:
            return jsonify({
                'code': 1,
                'message': '、'.join(errors)
            })
            
        # 检查分类是否存在
        category = DiseaseCategory.query.get(disease.category_id)
        if not category:
            return jsonify({
                'code': 1,
                'message': '所选分类不存在'
            })
            
        # 保存数据
        db.session.add(disease)
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': disease.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 获取疾病详情
@bp.route('/api/diseases/<int:id>')
def get_disease(id):
    try:
        disease = Disease.query.get(id)
        if not disease:
            return jsonify({
                'code': 1,
                'message': '疾病不存在'
            })
            
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': disease.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 更新疾病
@bp.route('/api/diseases/<int:id>', methods=['PUT'])
def update_disease(id):
    try:
        disease = Disease.query.get(id)
        if not disease:
            return jsonify({
                'code': 1,
                'message': '疾病不存在'
            })
            
        data = request.get_json()
        disease.name = data.get('name')
        disease.category_id = data.get('category_id')
        disease.risk_level = data.get('risk_level')
        disease.description = data.get('description')
        disease.status = data.get('status')
        
        # 验证数据
        is_valid, errors = disease.validate_update()
        if not is_valid:
            return jsonify({
                'code': 1,
                'message': '、'.join(errors)
            })
            
        # 检查分类是否存在
        category = DiseaseCategory.query.get(disease.category_id)
        if not category:
            return jsonify({
                'code': 1,
                'message': '所选分类不存在'
            })
            
        # 保存数据
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': disease.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 1,
            'message': str(e)
        })

# 删除疾病
@bp.route('/api/diseases/<int:id>', methods=['DELETE'])
def delete_disease(id):
    try:
        disease = Disease.query.get(id)
        if not disease:
            return jsonify({
                'code': 1,
                'message': '疾病不存在'
            })
            
        # 删除数据
        db.session.delete(disease)
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 1,
            'message': str(e)
        })