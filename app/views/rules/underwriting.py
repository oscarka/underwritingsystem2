from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.views.rules import bp
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.base.enums import StatusEnum
from app.extensions import db
from sqlalchemy import or_
import pandas as pd
import os
import uuid
from datetime import datetime
from app.services.underwriting.rule_import_service import RuleImportService
from app.models.rules.disease.disease import Disease
from app.models.rules.question.question import Question
from app.models.rules.answer.answer_option import AnswerOption
from app.models.rules.import_record import ImportRecord
import logging
from collections import defaultdict
from .base import RuleBaseView

logger = logging.getLogger(__name__)

@bp.route('/underwriting')
@login_required
def underwriting_list():
    """规则列表页面"""
    name = request.args.get('name', '')
    
    query = UnderwritingRule.query
    if name:
        query = query.filter(UnderwritingRule.name.like(f'%{name}%'))
        
    rules = query.order_by(UnderwritingRule.created_at.desc()).all()
    return render_template('rules/underwriting/index.html', rules=rules, search_name=name)

@bp.route('/underwriting/create')
@login_required
def underwriting_create():
    """创建规则页面"""
    return render_template('rules/underwriting/create.html')

@bp.route('/underwriting/edit/<int:id>')
@login_required
def underwriting_edit(id):
    """编辑规则页面"""
    rule = UnderwritingRule.query.get_or_404(id)
    return render_template('rules/underwriting/edit.html', rule=rule)

class UnderwritingRuleView(RuleBaseView):
    """核保规则视图类"""
    
    model_class = UnderwritingRule
    list_template = 'underwriting/index'
    detail_template = 'underwriting/rule_detail'
    
    @classmethod
    def get_rule_detail(cls, rule_id):
        """获取规则详情"""
        # 获取规则信息
        rule = cls.model_class.query.get_or_404(rule_id)
        
        # 获取最新的导入记录
        import_record = ImportRecord.query.filter_by(
            rule_id=rule_id
        ).order_by(ImportRecord.created_at.desc()).first()
        
        if not import_record:
            return cls.render_detail(
                rule=rule,
                diseases_by_category={},
                questions=[],
                answers_by_question={}
            )
        
        # 获取该批次的所有疾病，按大类分组
        diseases = Disease.query.filter_by(batch_no=import_record.batch_no).all()
        diseases_by_category = defaultdict(lambda: {'name': '', 'diseases': []})
        
        for disease in diseases:
            category = diseases_by_category[disease.category_code]
            category['name'] = disease.category_name
            category['diseases'].append(disease)
        
        # 获取所有问题
        questions = Question.query.filter_by(rule_id=rule_id).all()
        
        # 获取所有答案并按问题分组
        answers = AnswerOption.query.join(
            Question, AnswerOption.question_id == Question.id
        ).filter(
            Question.rule_id == rule_id
        ).all()
        
        # 将答案按问题ID分组
        answers_by_question = defaultdict(list)
        for answer in answers:
            answers_by_question[answer.question_id].append(answer)
        
        return cls.render_detail(
            rule=rule,
            diseases_by_category=dict(diseases_by_category),
            questions=questions,
            answers_by_question=dict(answers_by_question)
        )

@bp.route('/rule/<int:rule_id>')
def view_rule(rule_id):
    """查看规则详情"""
    return UnderwritingRuleView.get_rule_detail(rule_id)

# API路由
@bp.route('/underwriting/rules')
@login_required
def underwriting_get_list():
    """获取规则列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        name = request.args.get('name', '')
        status = request.args.get('status', '')
        disease_category = request.args.get('diseaseCategory', '')
        
        logger.info(f'获取规则列表 - 参数: page={page}, pageSize={page_size}, name={name}, status={status}, diseaseCategory={disease_category}')
        
        # 构建查询
        query = UnderwritingRule.query
        
        # 应用过滤条件
        if name:
            query = query.filter(UnderwritingRule.name.like(f'%{name}%'))
        if status:
            query = query.filter(UnderwritingRule.status == status)
        if disease_category:
            query = query.join(UnderwritingRule.diseases).filter(Disease.category_id == disease_category)
            
        # 计算总数
        total = query.count()
        
        # 分页
        rules = query.order_by(UnderwritingRule.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
            
        # 转换为列表
        rule_list = [{
            'id': r.id,
            'name': r.name,
            'version': r.version,
            'status': r.status,
            'description': r.description,
            'has_data': bool(r.diseases or r.questions or r.conclusions),
            'created_at': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else None,
            'updated_at': r.updated_at.strftime('%Y-%m-%d %H:%M:%S') if r.updated_at else None
        } for r in rules]
        
        logger.info(f'获取规则列表成功 - 总数: {total}, 当前页数据量: {len(rule_list)}')
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'list': rule_list,
                'pagination': {
                    'current': page,
                    'pageSize': page_size,
                    'total': total
                }
            }
        })
        
    except Exception as e:
        logger.error(f'获取规则列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        })

@bp.route('/underwriting', methods=['POST'])
@login_required
def underwriting_create_api():
    """创建规则"""
    try:
        data = request.get_json()
        
        # 验证数据
        if not data.get('name'):
            return jsonify({'status': 'error', 'message': '规则名称不能为空'})
        if not data.get('version'):
            return jsonify({'status': 'error', 'message': '规则版本不能为空'})
            
        # 检查是否已存在相同名称和版本的规则
        existing_rule = UnderwritingRule.query.filter_by(
            name=data['name'],
            version=data['version']
        ).first()
        
        if existing_rule:
            return jsonify({'status': 'error', 'message': '相同名称和版本的规则已存在'})
            
        # 创建规则
        rule = UnderwritingRule(
            name=data['name'],
            version=data['version'],
            description=data.get('description', ''),
            status=StatusEnum.ENABLED.value
        )
        
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

@bp.route('/underwriting/<int:id>', methods=['PUT'])
@login_required
def underwriting_update(id):
    """更新规则"""
    try:
        rule = UnderwritingRule.query.get_or_404(id)
        data = request.get_json()
        
        # 验证数据
        if not data.get('name'):
            return jsonify({'status': 'error', 'message': '规则名称不能为空'})
        if not data.get('version'):
            return jsonify({'status': 'error', 'message': '规则版本不能为空'})
            
        # 更新数据
        rule.name = data['name']
        rule.version = data['version']
        rule.description = data.get('description', '')
        rule.status = data.get('status', rule.status)
        
        # 验证数据
        is_valid, errors = rule.validate_update()
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': '、'.join(errors)
            })
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '更新成功',
            'data': rule.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/underwriting/<int:id>', methods=['DELETE'])
@login_required
def underwriting_delete(id):
    """删除规则"""
    try:
        rule = UnderwritingRule.query.get_or_404(id)
        db.session.delete(rule)
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

@bp.route('/underwriting/import', methods=['POST'])
@login_required
def underwriting_import():
    """导入规则"""
    try:
        data = request.get_json()
        
        # 验证数据
        if not data.get('name'):
            return jsonify({'status': 'error', 'message': '规则名称不能为空'})
        if not data.get('version'):
            return jsonify({'status': 'error', 'message': '规则版本不能为空'})
            
        # 检查是否已存在相同名称和版本的规则
        existing_rule = UnderwritingRule.query.filter_by(
            name=data['name'],
            version=data['version']
        ).first()
        
        if existing_rule:
            return jsonify({'status': 'error', 'message': '相同名称和版本的规则已存在'})
            
        # 创建规则
        rule = UnderwritingRule(
            name=data['name'],
            version=data['version'],
            description=data.get('description', ''),
            status=StatusEnum.DRAFT.value  # 导入的规则默认为草稿状态
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '导入成功',
            'data': rule.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/underwriting/<int:id>/export')
@login_required
def underwriting_export(id):
    """导出规则"""
    try:
        rule = UnderwritingRule.query.get_or_404(id)
        return jsonify({
            'status': 'success',
            'data': rule.to_dict()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@bp.route('/underwriting/import_excel', methods=['POST'])
@login_required
def import_excel():
    """导入Excel规则配置"""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': '没有上传文件'})
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '没有选择文件'})
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({'status': 'error', 'message': '请上传Excel文件(.xlsx)'})
        
        # 获取规则ID
        rule_id = request.form.get('rule_id')
        if not rule_id:
            return jsonify({'status': 'error', 'message': '未指定规则ID'})
            
        # 检查规则是否存在
        rule = UnderwritingRule.query.get(rule_id)
        if not rule:
            return jsonify({'status': 'error', 'message': f'未找到ID为{rule_id}的规则'})
        
        # 创建导入日志
        import_log = []
        import_log.append(f"开始导入Excel文件: {file.filename}")
        import_log.append(f"导入到规则: {rule.name} (ID: {rule.id})")
        
        # 保存上传的文件
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        safe_filename = f"upload_{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:8]}.xlsx"
        file_path = os.path.join(upload_folder, safe_filename)
        file.save(file_path)
        
        # 使用RuleImportService处理导入
        importer = RuleImportService(current_user)
        success, result = importer.process(file_path, rule_id=rule.id)
        
        if success:
            # 更新规则状态为已导入
            rule.status = StatusEnum.IMPORTED.value
            db.session.commit()
            
            import_log.append("\n=== 导入成功 ===")
            import_log.append(f"批次号: {result.batch_no}")
            import_log.append(f"总记录数: {result.total_count}")
            import_log.append(f"成功数: {result.success_count}")
            import_log.append(f"失败数: {result.error_count}")
            
            return jsonify({
                'status': 'success',
                'message': '导入成功',
                'log': '\n'.join(import_log)
            })
        else:
            import_log.append("\n=== 导入失败 ===")
            import_log.append(str(result))
            
            return jsonify({
                'status': 'error',
                'message': '导入失败',
                'log': '\n'.join(import_log)
            })
            
    except Exception as e:
        import traceback
        error_log = f"导入失败: {str(e)}\n{traceback.format_exc()}"
        return jsonify({
            'status': 'error',
            'message': '导入失败',
            'log': error_log
        })
    finally:
        # 清理临时文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"清理临时文件失败：{str(e)}")

@bp.route('/underwriting/rules/<string:id>', methods=['GET'])
@login_required
def get_rule_detail(id):
    """获取规则详情"""
    try:
        logger.info(f'获取规则详情 - id: {id}')
        rule = UnderwritingRule.query.get_or_404(id)
        
        data = rule.to_dict()
        data['has_data'] = bool(rule.diseases or rule.questions or rule.conclusions)
        
        logger.info(f'获取规则详情成功 - id: {id}')
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': data
        })
    except Exception as e:
        logger.error(f'获取规则详情失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        })

@bp.route('/underwriting/rules/<string:id>/export', methods=['GET'])
@login_required
def export_rule(id):
    """导出规则数据"""
    try:
        logger.info(f'导出规则数据 - id: {id}')
        rule = UnderwritingRule.query.get_or_404(id)
        
        # 检查规则是否有数据
        if not (rule.diseases or rule.questions or rule.conclusions):
            return jsonify({
                'code': 400,
                'message': '规则没有可导出的数据',
                'data': None
            })
        
        # 构建导出数据
        export_data = rule.to_dict()
        export_data['diseases'] = [d.to_dict() for d in rule.diseases]
        export_data['questions'] = [q.to_dict() for q in rule.questions]
        export_data['conclusions'] = [c.to_dict() for c in rule.conclusions]
        
        logger.info(f'导出规则数据成功 - id: {id}')
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': export_data
        })
    except Exception as e:
        logger.error(f'导出规则数据失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        })

@bp.route('/underwriting/disease-categories', methods=['GET'])
@login_required
def get_disease_categories():
    """获取疾病大类列表"""
    try:
        logger.info('获取疾病大类列表')
        categories = Disease.query.with_entities(
            Disease.category_id,
            Disease.category_name
        ).distinct().all()
        
        category_list = [{
            'id': c.category_id,
            'name': c.category_name
        } for c in categories]
        
        logger.info(f'获取疾病大类列表成功 - 数量: {len(category_list)}')
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': category_list
        })
    except Exception as e:
        logger.error(f'获取疾病大类列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }) 