from flask import Blueprint, request, jsonify
from app.models.rules import (
    UnderwritingRule,
    Disease,
    DiseaseCategory,
    Question,
    Conclusion as Answer
)
from app import db
from app.utils.logging import get_logger

logger = get_logger(__name__)

bp = Blueprint('underwriting', __name__, url_prefix='/api/v1/underwriting')

@bp.route('/rules', methods=['GET'])
def get_rules():
    """获取规则列表"""
    try:
        # 获取查询参数
        name = request.args.get('name', '')
        status = request.args.get('status', '')
        disease_category = request.args.get('diseaseCategory', '')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        simple = request.args.get('simple', 'false').lower() == 'true'
        
        logger.info(f'[请求参数] name={name}, status={status}, disease_category={disease_category}, page={page}, page_size={page_size}, simple={simple}')
        
        # 构建查询
        query = UnderwritingRule.query
        
        # 记录原始SQL
        logger.info(f'[原始SQL] {query.statement.compile(compile_kwargs={"literal_binds": True})}')
        
        # 应用过滤条件
        if name:
            query = query.filter(UnderwritingRule.name.like(f'%{name}%'))
            logger.info(f'[添加名称过滤] name LIKE %{name}%')
        if status:
            query = query.filter(UnderwritingRule.status == status)
            logger.info(f'[添加状态过滤] status = {status}')
            
        # 记录最终SQL
        logger.info(f'[最终SQL] {query.statement.compile(compile_kwargs={"literal_binds": True})}')
        
        # 执行分页查询
        pagination = query.order_by(UnderwritingRule.created_at.desc()).paginate(
            page=page, per_page=page_size, error_out=False)
            
        logger.info(f'[分页结果] 总数={pagination.total}, 当前页={pagination.page}, 每页条数={page_size}')
        
        # 转换数据
        rules = []
        for rule in pagination.items:
            # 记录原始数据
            logger.info(f'[处理数据] 原始: id={rule.id}, name={rule.name}, version={rule.version}, status={rule.status}')
            
            # 使用 to_dict() 方法获取完整数据
            rule_dict = rule.to_dict()
            
            # 如果是简单模式，只保留必要字段
            if simple:
                rule_dict = {
                    'id': f'R{str(rule.id).zfill(3)}',
                    'name': rule_dict['name'],
                    'version': rule_dict['version'],
                    'status': rule_dict['status'],
                    'has_data': rule_dict['has_data'],
                    'created_at': rule_dict['created_at'],
                    'updated_at': rule_dict['updated_at']
                }
            
            rules.append(rule_dict)
            # 记录转换后的数据
            logger.info(f'[处理数据] 转换后: {rule_dict}')
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': {
                'list': rules,
                'total': pagination.total,
                'page': pagination.page,
                'pageSize': page_size
            }
        }
        logger.info(f'[响应数据] {response_data}')
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f'获取规则列表失败: {str(e)}', exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'获取规则列表失败: {str(e)}'
        })

@bp.route('/rules/<string:id>', methods=['GET'])
def get_rule(id):
    """获取规则详情"""
    try:
        logger.info(f"[API] 开始获取规则详情, 请求参数: id={id}")
        # 如果id是字符串格式（如'R001'），转换为数字
        numeric_id = int(id.replace('R', '')) if id.startswith('R') else int(id)
        logger.debug(f"[转换] 规则ID转换结果: 原始ID={id}, 转换后numeric_id={numeric_id}")
        
        rule = UnderwritingRule.query.get_or_404(numeric_id)
        logger.debug(f"[查询] 查询到的规则对象: id={rule.id}, name={rule.name}, version={rule.version}")
        
        # 检查是否已导入数据
        has_data = bool(Question.query.filter_by(rule_id=numeric_id).first())
        
        # 构建规则详情数据
        rule_data = {
            'id': f"R{rule.id:03d}",  # 转换为R001格式
            'name': rule.name,
            'version': rule.version,
            'description': rule.description,
            'status': rule.status,
            'has_data': has_data,  # 添加数据导入状态
            'created_at': rule.created_at.strftime('%Y-%m-%d %H:%M:%S') if rule.created_at else None,
            'updated_at': rule.updated_at.strftime('%Y-%m-%d %H:%M:%S') if rule.updated_at else None
        }
        logger.debug(f"[响应] 返回的规则数据: {rule_data}")
        
        return jsonify({
            "code": 200,
            "data": rule_data,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取规则详情失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/diseases', methods=['GET'])
def get_diseases():
    """获取疾病列表"""
    try:
        logger.info("[API] 开始获取疾病列表")
        logger.debug(f"[请求] 请求参数: {request.args}")
        
        diseases = Disease.query.all()
        logger.info(f"[查询] 查询到疾病总数: {len(diseases)}")
        
        disease_list = []
        for disease in diseases:
            disease_dict = {
                'code': disease.code,
                'name': disease.name,
                'category_name': disease.category_name,
                'first_question_code': disease.first_question_code
            }
            disease_list.append(disease_dict)
            logger.debug(f"[数据] 处理疾病数据: code={disease.code}, name={disease.name}")
            
        logger.debug(f"[响应] 返回疾病列表数量: {len(disease_list)}")
        return jsonify({
            "code": 200,
            "data": disease_list,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取疾病列表失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/diseases/<string:disease_code>/questions', methods=['GET'])
def get_disease_questions(disease_code):
    """获取疾病对应的问题及答案选项"""
    try:
        logger.info(f"[API] 开始获取疾病问题, 疾病代码: {disease_code}")
        
        # 1. 获取疾病信息
        disease = Disease.query.filter_by(code=disease_code).first_or_404()
        logger.debug(f"[查询] 查询到疾病信息: code={disease.code}, name={disease.name}")
        
        # 2. 获取关联的问题
        question = Question.query.filter_by(code=disease.first_question_code).first_or_404()
        logger.debug(f"[查询] 查询到问题信息: code={question.code}, content={question.content}")
        
        # 3. 获取问题对应的规则
        rule = question.rule
        logger.debug(f"[查询] 关联的规则信息: id={rule.id}, name={rule.name}")
        
        # 4. 获取规则下的结论选项
        conclusions = Answer.query.filter_by(rule_id=rule.id).all()
        logger.debug(f"[查询] 查询到结论选项数量: {len(conclusions)}")
        
        # 5. 构建返回数据
        question_data = {
            'disease': {
                'code': disease.code,
                'name': disease.name,
                'category_name': disease.category_name
            },
            'question': {
                'code': question.code,
                'content': question.content,
                'question_type': question.question_type,
                'attribute': question.attribute
            },
            'answers': [{
                'question_code': conclusion.question_code,
                'answer_content': conclusion.answer_content,
                'medical_conclusion': conclusion.medical_conclusion,
                'critical_illness_conclusion': conclusion.critical_illness_conclusion,
                'medical_special_code': conclusion.medical_special_code,
                'critical_illness_special_code': conclusion.critical_illness_special_code,
                'next_question_code': conclusion.next_question_code,
                'display_order': conclusion.display_order
            } for conclusion in conclusions]
        }
        logger.debug(f"[响应] 返回的问题数据: {question_data}")
        
        return jsonify({
            "code": 200,
            "data": question_data,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取疾病问题失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/rules/<string:rule_id>/questions', methods=['GET'])
def get_rule_questions(rule_id):
    """获取规则相关的问题列表"""
    try:
        logger.info(f"[API] 开始获取规则问题列表, rule_id={rule_id}")
        logger.debug(f"[请求] 请求参数: {request.args}")
        
        # 如果id是字符串格式（如'R001'），转换为数字
        numeric_id = int(rule_id.replace('R', '')) if rule_id.startswith('R') else int(rule_id)
        logger.debug(f"[转换] 规则ID转换结果: 原始ID={rule_id}, 转换后numeric_id={numeric_id}")
        
        # 获取规则对象
        rule = UnderwritingRule.query.get_or_404(numeric_id)
        logger.debug(f"[查询] 查询到的规则对象: id={rule.id}, name={rule.name}")
        
        # 检查是否已导入数据
        has_data = bool(Question.query.filter_by(rule_id=numeric_id).first())
        if not has_data:
            logger.info(f"[查询] 规则{rule_id}未导入数据")
            return jsonify({
                "code": 200,
                "data": [],
                "message": "规则未导入数据"
            })
        
        questions = Question.query.filter_by(rule_id=numeric_id).all()
        logger.info(f"[查询] 查询到问题总数: {len(questions)}")
        
        question_list = []
        for question in questions:
            question_dict = question.to_dict()
            question_list.append(question_dict)
            logger.debug(f"[数据] 处理问题数据: code={question.code}, content={question.content}")
            
        logger.debug(f"[响应] 返回问题列表数量: {len(question_list)}")
        return jsonify({
            "code": 200,
            "data": question_list,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取问题列表失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/rules/<string:rule_id>/conclusions', methods=['GET'])
def get_rule_conclusions(rule_id):
    """获取规则相关的结论列表"""
    try:
        logger.info(f"[API] 开始获取规则结论列表, rule_id={rule_id}")
        logger.debug(f"[请求] 请求参数: {request.args}")
        
        conclusions = Answer.query.filter_by(rule_id=rule_id).all()
        logger.info(f"[查询] 查询到结论总数: {len(conclusions)}")
        
        conclusion_list = []
        for conclusion in conclusions:
            conclusion_dict = {
                'id': conclusion.id,
                'question_code': conclusion.question_code,
                'answer_content': conclusion.answer_content,
                'medical_conclusion': conclusion.medical_conclusion,
                'critical_illness_conclusion': conclusion.critical_illness_conclusion
            }
            conclusion_list.append(conclusion_dict)
            logger.debug(f"[数据] 处理结论数据: question_code={conclusion.question_code}, content={conclusion.answer_content}")
            
        logger.debug(f"[响应] 返回结论列表数量: {len(conclusion_list)}")
        return jsonify({
            "code": 200,
            "data": conclusion_list,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取结论列表失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/disease-categories', methods=['GET'])
def get_disease_categories():
    """获取疾病大类列表"""
    try:
        logger.info("[API] 开始获取疾病大类列表")
        logger.debug(f"[请求] 请求参数: {request.args}")
        
        categories = DiseaseCategory.query.all()
        logger.info(f"[查询] 查询到疾病大类总数: {len(categories)}")
        
        category_list = []
        for category in categories:
            category_dict = {
                'code': category.code,
                'name': category.name,
                'description': category.description
            }
            category_list.append(category_dict)
            logger.debug(f"[数据] 处理疾病大类数据: code={category.code}, name={category.name}")
            
        logger.debug(f"[响应] 返回疾病大类列表数量: {len(category_list)}")
        return jsonify({
            "code": 200,
            "data": category_list,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取疾病大类列表失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/rules/<string:rule_id>/answers', methods=['GET'])
def get_rule_answers(rule_id):
    """获取规则相关的答案列表"""
    try:
        logger.info(f"[API] 开始获取规则答案列表, rule_id={rule_id}")
        logger.debug(f"[请求] 请求参数: {request.args}")
        
        # 如果id是字符串格式（如'R001'），转换为数字
        numeric_id = int(rule_id.replace('R', '')) if rule_id.startswith('R') else int(rule_id)
        logger.debug(f"[转换] 规则ID转换结果: 原始ID={rule_id}, 转换后numeric_id={numeric_id}")
        
        # 获取规则对象
        rule = UnderwritingRule.query.get_or_404(numeric_id)
        logger.debug(f"[查询] 查询到的规则对象: id={rule.id}, name={rule.name}")
        
        # 检查是否已导入数据
        has_data = bool(Question.query.filter_by(rule_id=numeric_id).first())
        if not has_data:
            logger.info(f"[查询] 规则{rule_id}未导入数据")
            return jsonify({
                "code": 200,
                "data": [],
                "message": "规则未导入数据"
            })
        
        # 获取规则相关的所有答案
        answers = Answer.query.filter_by(rule_id=numeric_id).all()
        logger.info(f"[查询] 查询到答案总数: {len(answers)}")
        
        answer_list = []
        for answer in answers:
            answer_dict = {
                'id': answer.id,
                'question_code': answer.question_code,
                'answer_content': answer.answer_content,
                'medical_conclusion': answer.medical_conclusion,
                'critical_illness_conclusion': answer.critical_illness_conclusion,
                'medical_special_code': answer.medical_special_code,
                'critical_illness_special_code': answer.critical_illness_special_code,
                'medical_special_desc': answer.medical_special_desc,
                'critical_illness_special_desc': answer.critical_illness_special_desc,
                'next_question_code': answer.next_question_code,
                'display_order': answer.display_order,
                'remark': answer.remark,
                'rule_id': answer.rule_id,
                'batch_no': answer.batch_no,
                'created_at': answer.created_at.strftime('%Y-%m-%d %H:%M:%S') if answer.created_at else None,
                'updated_at': answer.updated_at.strftime('%Y-%m-%d %H:%M:%S') if answer.updated_at else None
            }
            answer_list.append(answer_dict)
            logger.debug(f"[数据] 处理答案数据: question_code={answer.question_code}, answer_content={answer.answer_content}")
            
        logger.debug(f"[响应] 返回答案列表数量: {len(answer_list)}")
        return jsonify({
            "code": 200,
            "data": answer_list,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取答案列表失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/rules', methods=['POST'])
def create_rule():
    """创建规则"""
    try:
        logger.info("[API] 开始创建规则")
        data = request.get_json()
        logger.debug(f"[请求] 请求数据: {data}")
        
        # 验证必填字段
        required_fields = ['name', 'version']
        for field in required_fields:
            if not data.get(field):
                error_msg = f"缺少必填字段: {field}"
                logger.error(f"[错误] {error_msg}")
                return jsonify({
                    "code": 400,
                    "message": error_msg
                }), 400
        
        # 检查是否已存在相同名称和版本的规则
        existing_rule = UnderwritingRule.query.filter_by(
            name=data['name'],
            version=data['version']
        ).first()
        
        if existing_rule:
            error_msg = "相同名称和版本的规则已存在"
            logger.error(f"[错误] {error_msg}")
            return jsonify({
                "code": 400,
                "message": error_msg
            }), 400
            
        # 创建规则
        rule = UnderwritingRule(
            name=data['name'],
            version=data['version'],
            description=data.get('description', ''),
            status=data.get('status', 'enabled')
        )
        
        db.session.add(rule)
        db.session.commit()
        logger.info(f"[成功] 规则创建成功: id={rule.id}")
        
        # 构建返回数据
        rule_data = {
            'id': f"R{rule.id:03d}",  # 转换为R001格式
            'name': rule.name,
            'version': rule.version,
            'description': rule.description,
            'status': rule.status,
            'created_at': rule.created_at.strftime('%Y-%m-%d %H:%M:%S') if rule.created_at else None,
            'updated_at': rule.updated_at.strftime('%Y-%m-%d %H:%M:%S') if rule.updated_at else None
        }
        
        return jsonify({
            "code": 200,
            "data": rule_data,
            "message": "success"
        })
    except Exception as e:
        db.session.rollback()
        error_msg = f"创建规则失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/rules/<string:rule_id>/export', methods=['GET'])
def export_rule(rule_id):
    """导出规则数据"""
    try:
        logger.info(f"[API] 开始导出规则数据, rule_id={rule_id}")
        
        # 如果id是字符串格式（如'R001'），转换为数字
        numeric_id = int(rule_id.replace('R', '')) if rule_id.startswith('R') else int(rule_id)
        logger.debug(f"[转换] 规则ID转换结果: 原始ID={rule_id}, 转换后numeric_id={numeric_id}")
        
        # 获取规则对象
        rule = UnderwritingRule.query.get_or_404(numeric_id)
        logger.debug(f"[查询] 查询到的规则对象: id={rule.id}, name={rule.name}")
        
        # 检查是否已导入数据
        has_data = bool(Question.query.filter_by(rule_id=numeric_id).first())
        if not has_data:
            logger.info(f"[查询] 规则{rule_id}未导入数据")
            return jsonify({
                "code": 400,
                "message": "规则未导入数据,无法导出"
            }), 400
            
        # 获取规则相关的所有数据
        questions = Question.query.filter_by(rule_id=numeric_id).all()
        answers = Answer.query.filter_by(rule_id=numeric_id).all()
        
        # 构建导出数据
        export_data = {
            'rule': {
                'id': f"R{rule.id:03d}",
                'name': rule.name,
                'version': rule.version,
                'description': rule.description,
                'status': rule.status
            },
            'questions': [{
                'code': q.code,
                'content': q.content,
                'question_type': q.question_type,
                'attribute': q.attribute
            } for q in questions],
            'answers': [{
                'code': a.code,
                'content': a.content,
                'decision': a.decision,
                'em_value': float(a.em_value) if a.em_value else None
            } for a in answers]
        }
        
        logger.info(f"[导出] 导出数据成功: questions={len(questions)}, answers={len(answers)}")
        return jsonify({
            "code": 200,
            "data": export_data,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"导出规则数据失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/rules/<string:rule_id>/import', methods=['POST'])
def import_rule(rule_id):
    """导入规则数据"""
    try:
        logger.info(f"[API] 开始导入规则数据, rule_id={rule_id}")
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            error_msg = "未找到上传的文件"
            logger.error(f"[错误] {error_msg}")
            return jsonify({
                "code": 400,
                "message": error_msg
            }), 400
            
        file = request.files['file']
        if not file or not file.filename:
            error_msg = "文件无效"
            logger.error(f"[错误] {error_msg}")
            return jsonify({
                "code": 400,
                "message": error_msg
            }), 400
            
        logger.info(f"[上传] 接收到文件: {file.filename}, 大小: {file.content_length if hasattr(file, 'content_length') else '未知'} bytes")
        
        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            error_msg = "不支持的文件类型，仅支持.xlsx和.xls格式"
            logger.error(f"[错误] {error_msg}, 文件类型: {file.content_type if hasattr(file, 'content_type') else '未知'}")
            return jsonify({
                "code": 400,
                "message": error_msg
            }), 400
        
        # 如果id是字符串格式（如'R001'），转换为数字
        numeric_id = int(rule_id.replace('R', '')) if rule_id.startswith('R') else int(rule_id)
        logger.debug(f"[转换] 规则ID转换结果: 原始ID={rule_id}, 转换后numeric_id={numeric_id}")
        
        # 获取规则对象
        rule = UnderwritingRule.query.get_or_404(numeric_id)
        logger.debug(f"[查询] 查询到的规则对象: id={rule.id}, name={rule.name}")
        
        # 检查是否已导入数据
        has_data = bool(Question.query.filter_by(rule_id=numeric_id).first())
        if has_data:
            # 生成新的批次号
            import datetime
            batch_no = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            logger.info(f"[导入] 规则{rule_id}已有数据，使用新批次号: {batch_no}")
        else:
            batch_no = '000001'  # 第一次导入使用初始批次号
            logger.info(f"[导入] 规则{rule_id}首次导入，使用初始批次号: {batch_no}")

        try:
            # 保存文件到临时目录
            import tempfile
            import pandas as pd
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                file.save(temp_file.name)
                logger.info(f"[文件] 临时保存文件到: {temp_file.name}")
                
                # 首先获取所有sheet名称
                xl = pd.ExcelFile(temp_file.name)
                sheet_names = xl.sheet_names
                logger.info(f"[Excel] 文件包含的sheet: {sheet_names}")
                
                # 读取疾病数据（第一个sheet），使用第一行作为列名，跳过第二行说明，从第三行开始读取数据
                diseases_df = pd.read_excel(temp_file.name, sheet_name=0, header=0, skiprows=[1])
                logger.info(f"[Excel] 读取疾病sheet成功, 列名: {list(diseases_df.columns)}, 行数: {len(diseases_df)}")
                
                # 读取问题数据（第二个sheet），使用第一行作为列名，跳过第二行说明，从第三行开始读取数据
                questions_df = pd.read_excel(temp_file.name, sheet_name=1, header=0, skiprows=[1])
                logger.info(f"[Excel] 读取问题sheet成功, 列名: {list(questions_df.columns)}, 行数: {len(questions_df)}")
                
                # 读取答案数据（第三个sheet），使用第一行作为列名，跳过第二行说明，从第三行开始读取数据
                answers_df = pd.read_excel(temp_file.name, sheet_name=2, header=0, skiprows=[1])
                logger.info(f"[Excel] 读取答案sheet成功, 列名: {list(answers_df.columns)}, 行数: {len(answers_df)}")
                
                # 验证必需的列是否存在
                required_disease_columns = ['疾病大类编码', '疾病大类', '疾病编码', '疾病', '疾病第一个问题编码']
                missing_disease_columns = [col for col in required_disease_columns if col not in diseases_df.columns]
                if missing_disease_columns:
                    error_msg = f"疾病sheet缺少必需的列: {', '.join(missing_disease_columns)}"
                    logger.error(f"[错误] {error_msg}")
                    return jsonify({
                        "code": 400,
                        "message": error_msg
                    }), 400

                required_question_columns = ['问题编码', '问题内容', '问题属性', '问题类型']
                missing_question_columns = [col for col in required_question_columns if col not in questions_df.columns]
                if missing_question_columns:
                    error_msg = f"问题sheet缺少必需的列: {', '.join(missing_question_columns)}"
                    logger.error(f"[错误] {error_msg}")
                    return jsonify({
                        "code": 400,
                        "message": error_msg
                    }), 400

                required_answer_columns = ['问题编码', '答案内容', '重疾结论', '医疗险结论']
                missing_answer_columns = [col for col in required_answer_columns if col not in answers_df.columns]
                if missing_answer_columns:
                    error_msg = f"答案sheet缺少必需的列: {', '.join(missing_answer_columns)}"
                    logger.error(f"[错误] {error_msg}")
                    return jsonify({
                        "code": 400,
                        "message": error_msg
                    }), 400
                
                logger.info(f"[解析] Excel文件解析成功: 疾病数={len(diseases_df)}, 问题数={len(questions_df)}, 答案数={len(answers_df)}")
                
                # 开始事务
                # 先处理疾病数据
                for idx, row in diseases_df.iterrows():
                    try:
                        # 跳过空行
                        if pd.isna(row['疾病编码']) or pd.isna(row['疾病']):
                            logger.debug(f"[跳过] 跳过空行 [{idx+1}]")
                            continue
                            
                        disease = Disease(
                            rule_id=numeric_id,
                            batch_no=batch_no,  # 添加批次号
                            category_code=str(row['疾病大类编码']),
                            category_name=str(row['疾病大类']),
                            code=str(row['疾病编码']),
                            name=str(row['疾病']),
                            first_question_code=str(row['疾病第一个问题编码']),
                            is_common=bool(row.get('是否为常见疾病', 0)),
                            description=str(row.get('备注', '')) if pd.notna(row.get('备注')) else None
                        )
                        db.session.add(disease)
                        logger.debug(f"[导入] 添加疾病 [{idx+1}/{len(diseases_df)}]: code={disease.code}, name={disease.name}, batch_no={batch_no}")
                    except Exception as e:
                        logger.error(f"[错误] 处理疾病数据失败 [行 {idx+1}]: {str(e)}, 数据: {row.to_dict()}")
                        raise

                # 处理问题数据
                for idx, row in questions_df.iterrows():
                    try:
                        # 跳过空行
                        if pd.isna(row['问题编码']) or pd.isna(row['问题内容']):
                            logger.debug(f"[跳过] 跳过空行 [{idx+1}]")
                            continue
                            
                        question = Question(
                            rule_id=numeric_id,
                            batch_no=batch_no,  # 添加批次号
                            question_code=str(row['问题编码']),
                            content=str(row['问题内容']),
                            question_type=str(row['问题属性']),
                            attribute=str(row['问题类型'])
                        )
                        db.session.add(question)
                        logger.debug(f"[导入] 添加问题 [{idx+1}/{len(questions_df)}]: code={question.question_code}, content={question.content}, batch_no={batch_no}")
                    except Exception as e:
                        logger.error(f"[错误] 处理问题数据失败 [行 {idx+1}]: {str(e)}, 数据: {row.to_dict()}")
                        raise

                # 处理答案（结论）数据
                logger.info(f"[处理] 开始处理答案数据, 总行数: {len(answers_df)}")
                logger.info(f"[数据] 答案数据列名: {list(answers_df.columns)}")
                
                for idx, row in answers_df.iterrows():
                    try:
                        # 跳过空行
                        if pd.isna(row['问题编码']) or pd.isna(row['答案内容']):
                            logger.debug(f"[跳过] 跳过空行 [{idx+1}]")
                            continue
                        
                        logger.debug(f"[数据] 正在处理第 {idx+1} 行答案数据:")
                        logger.debug(f"- 问题编码: {row['问题编码']}")
                        logger.debug(f"- 答案内容: {row['答案内容']}")
                        logger.debug(f"- 医疗险结论: {row.get('医疗险结论', 'N/A')}")
                        logger.debug(f"- 重疾结论: {row.get('重疾结论', 'N/A')}")
                        
                        answer = Answer(
                            rule_id=numeric_id,
                            batch_no=batch_no,  # 添加批次号
                            question_code=str(row['问题编码']),
                            answer_content=str(row['答案内容']),
                            medical_conclusion=str(row['医疗险结论']) if pd.notna(row.get('医疗险结论')) else None,
                            critical_illness_conclusion=str(row['重疾结论']) if pd.notna(row.get('重疾结论')) else None,
                            medical_special_code=str(row['医疗特殊编码']) if pd.notna(row.get('医疗特殊编码')) else None,
                            critical_illness_special_code=str(row['重疾特殊编码']) if pd.notna(row.get('重疾特殊编码')) else None,
                            medical_special_desc=str(row['医疗特殊描述']) if pd.notna(row.get('医疗特殊描述')) else None,
                            critical_illness_special_desc=str(row['重疾特殊描述']) if pd.notna(row.get('重疾特殊描述')) else None,
                            next_question_code=str(row['对应下一个问题编码']) if pd.notna(row.get('对应下一个问题编码')) else None,
                            display_order=int(row['答案展示顺序']) if pd.notna(row.get('答案展示顺序')) else 0,
                            remark=str(row['备注（答案解释）']) if pd.notna(row.get('备注（答案解释）')) else None
                        )
                        db.session.add(answer)
                        logger.debug(f"[导入] 添加答案 [{idx+1}/{len(answers_df)}]: question_code={answer.question_code}, answer_content={answer.answer_content}, batch_no={batch_no}")
                    except Exception as e:
                        logger.error(f"[错误] 处理答案数据失败 [行 {idx+1}]: {str(e)}, 数据: {row.to_dict()}")
                        raise
                
                # 处理疾病大类数据
                category_codes = diseases_df['疾病大类编码'].unique()
                for code in category_codes:
                    if pd.isna(code):
                        continue
                    # 获取该大类的第一条疾病记录
                    category_data = diseases_df[diseases_df['疾病大类编码'] == code].iloc[0]
                    category = DiseaseCategory(
                        rule_id=numeric_id,
                        batch_no=batch_no,  # 添加批次号
                        code=str(code),
                        name=str(category_data['疾病大类'])
                    )
                    db.session.add(category)
                    logger.debug(f"[导入] 添加疾病大类: code={category.code}, name={category.name}, batch_no={batch_no}")

                db.session.commit()
                logger.info(f"[导入] 导入数据成功: questions={len(questions_df)}, answers={len(answers_df)}, categories={len(category_codes)}, batch_no={batch_no}")
                
        except Exception as e:
            db.session.rollback()
            error_msg = f"导入数据失败: {str(e)}"
            logger.error(f"[错误] {error_msg}")
            return jsonify({
                "code": 500,
                "message": error_msg
            }), 500

        finally:
            # 删除临时文件
            try:
                os.unlink(temp_file.name)
                logger.info(f"[清理] 删除临时文件: {temp_file.name}")
            except Exception as e:
                logger.error(f"[错误] 删除临时文件失败: {str(e)}")
            
        return jsonify({
            "code": 200,
            "message": "导入成功"
        })
            
    except Exception as e:
        error_msg = f"导入规则数据失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        logger.error(f"[堆栈] 详细错误信息:", stack_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

def normalize_rule_id(rule_id):
    """统一处理规则ID的格式"""
    if not rule_id or rule_id == 'undefined':
        return None
    try:
        # 处理带R前缀的规则ID
        if isinstance(rule_id, str) and rule_id.startswith('R'):
            return int(rule_id[1:])
        return int(rule_id)
    except (ValueError, TypeError):
        return None

@bp.route('/rules/<string:rule_id>/disease-categories', methods=['GET'])
def get_rule_disease_categories(rule_id):
    try:
        logger.info(f"[API] 开始获取规则关联的疾病大类列表, rule_id: {rule_id}")
        
        # 规则ID格式处理
        numeric_id = normalize_rule_id(rule_id)
        logger.debug(f"[转换] 规则ID转换结果: 原始ID={rule_id}, 转换后numeric_id={numeric_id}")
        
        if not numeric_id:
            logger.info("[返回] 规则ID无效，返回空列表")
            return jsonify({
                "code": 200,
                "data": [],
                "message": "success"
            })
            
        # 验证规则是否存在
        rule = UnderwritingRule.query.get(numeric_id)
        if not rule:
            logger.info(f"[查询] 规则不存在: rule_id={numeric_id}")
            return jsonify({
                "code": 200,
                "data": [],
                "message": "success"
            })
        logger.info(f"[数据] 找到规则: id={rule.id}, name={rule.name}")
        
        # 直接通过rule_id查询疾病大类
        categories = DiseaseCategory.get_by_rule_id(numeric_id)
        logger.info(f"[数据] 找到疾病类别数量: {len(categories)}")
        
        # 如果通过rule_id没有找到，尝试通过疾病关联查询
        if not categories:
            logger.debug("[查询] 通过rule_id未找到类别，尝试通过疾病关联查询")
            categories = Disease.get_categories_by_rule_id(numeric_id)
            logger.info(f"[数据] 通过疾病关联找到疾病类别数量: {len(categories)}")
        
        result = [category.to_dict() for category in categories]
        logger.info(f"[返回] 返回疾病类别列表, 数量: {len(result)}")
        return jsonify({
            "code": 200,
            "data": result,
            "message": "success"
        })
        
    except Exception as e:
        logger.error(f"[错误] 获取规则关联的疾病大类列表失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "data": [],
            "message": str(e)
        }), 500

@bp.route('/rules/<string:rule_id>/diseases', methods=['GET'])
def get_rule_diseases(rule_id):
    try:
        logger.info(f"[API] 开始获取规则关联的疾病列表, rule_id: {rule_id}")
        
        # 规则ID格式处理
        numeric_id = normalize_rule_id(rule_id)
        logger.debug(f"[转换] 规则ID转换结果: 原始ID={rule_id}, 转换后numeric_id={numeric_id}")
        
        if not numeric_id:
            logger.info("[返回] 规则ID无效，返回空列表")
            return jsonify({
                "code": 200,
                "data": [],
                "message": "success"
            })
            
        # 验证规则是否存在
        rule = UnderwritingRule.query.get(numeric_id)
        if not rule:
            logger.info(f"[查询] 规则不存在: rule_id={numeric_id}")
            return jsonify({
                "code": 200,
                "data": [],
                "message": "success"
            })
        logger.info(f"[数据] 找到规则: id={rule.id}, name={rule.name}")
        
        # 使用Disease模型的类方法获取疾病列表
        diseases = Disease.get_by_rule_id(numeric_id)
        logger.info(f"[数据] 找到疾病数量: {len(diseases)}")
        
        result = [disease.to_dict() for disease in diseases]
        logger.info(f"[返回] 返回疾病列表, 数量: {len(result)}")
        return jsonify({
            "code": 200,
            "data": result,
            "message": "success"
        })
            
    except Exception as e:
        logger.error(f"[错误] 获取规则关联的疾病列表失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "data": [],
            "message": str(e)
        }), 500

@bp.route('/all-diseases', methods=['GET'])
def get_all_diseases():
    """获取所有疾病数据（用于调试）"""
    try:
        logger.info("[API] 开始获取所有疾病数据")
        diseases = Disease.query.all()
        logger.info(f"[查询] 查询到疾病总数: {len(diseases)}")
        
        disease_list = []
        for disease in diseases:
            disease_dict = disease.to_dict()
            disease_list.append(disease_dict)
            logger.debug(f"[数据] 疾病: id={disease.id}, code={disease.code}, name={disease.name}, rule_id={disease.rule_id}, category_id={disease.category_id}")
            
        return jsonify({
            "code": 200,
            "data": disease_list,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取所有疾病数据失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        return jsonify({
            "code": 500,
            "data": [],
            "message": error_msg
        }), 500

@bp.route('/all-categories', methods=['GET'])
def get_all_categories():
    """获取所有疾病大类数据（用于调试）"""
    try:
        logger.info("[API] 开始获取所有疾病大类数据")
        categories = DiseaseCategory.query.all()
        logger.info(f"[查询] 查询到疾病大类总数: {len(categories)}")
        
        category_list = []
        for category in categories:
            category_dict = category.to_dict()
            category_list.append(category_dict)
            logger.debug(f"[数据] 疾病大类: id={category.id}, code={category.code}, name={category.name}, rule_id={category.rule_id}")
            
        return jsonify({
            "code": 200,
            "data": category_list,
            "message": "success"
        })
    except Exception as e:
        error_msg = f"获取所有疾病大类数据失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        return jsonify({
            "code": 500,
            "data": [],
            "message": error_msg
        }), 500

@bp.route('/rules/<string:rule_id>/diseases/associate', methods=['POST'])
def associate_rule_diseases(rule_id):
    """关联规则和疾病"""
    try:
        logger.info(f"[API] 开始关联规则和疾病, rule_id={rule_id}")
        data = request.get_json()
        logger.debug(f"[请求] 请求数据: {data}")
        
        # 规则ID格式处理
        numeric_id = normalize_rule_id(rule_id)
        if not numeric_id:
            return jsonify({
                "code": 400,
                "message": "无效的规则ID"
            }), 400
            
        # 验证规则是否存在
        rule = UnderwritingRule.query.get(numeric_id)
        if not rule:
            return jsonify({
                "code": 404,
                "message": "规则不存在"
            }), 404
            
        # 获取要关联的疾病ID列表
        disease_codes = data.get('disease_codes', [])
        if not disease_codes:
            return jsonify({
                "code": 400,
                "message": "请提供要关联的疾病代码列表"
            }), 400
            
        # 更新疾病的rule_id
        diseases = Disease.query.filter(Disease.code.in_(disease_codes)).all()
        for disease in diseases:
            disease.rule_id = numeric_id
            logger.info(f"[关联] 疾病 {disease.code} 关联到规则 {rule_id}")
            
        # 更新疾病大类的rule_id
        category_ids = list(set(d.category_id for d in diseases if d.category_id))
        if category_ids:
            categories = DiseaseCategory.query.filter(DiseaseCategory.id.in_(category_ids)).all()
            for category in categories:
                category.rule_id = numeric_id
                logger.info(f"[关联] 疾病大类 {category.code} 关联到规则 {rule_id}")
                
        db.session.commit()
        logger.info(f"[成功] 成功关联 {len(diseases)} 个疾病和 {len(category_ids)} 个疾病大类到规则 {rule_id}")
        
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "associated_diseases": len(diseases),
                "associated_categories": len(category_ids)
            }
        })
            
    except Exception as e:
        db.session.rollback()
        error_msg = f"关联规则和疾病失败: {str(e)}"
        logger.error(f"[错误] {error_msg}", exc_info=True)
        return jsonify({
            "code": 500,
            "message": error_msg
        }), 500

@bp.route('/debug/rules', methods=['GET'])
def debug_rules():
    """调试接口:获取数据库中所有规则数据"""
    try:
        rules = UnderwritingRule.query.all()
        logger.info(f'数据库中的规则总数: {len(rules)}')
        
        rules_data = []
        for rule in rules:
            rule_dict = {
                'id': rule.id,
                'name': rule.name,
                'version': rule.version,
                'status': rule.status,
                'description': rule.description,
                'created_at': rule.created_at.strftime('%Y-%m-%d %H:%M:%S') if rule.created_at else None,
                'updated_at': rule.updated_at.strftime('%Y-%m-%d %H:%M:%S') if rule.updated_at else None,
                'raw_data': str(rule.__dict__)
            }
            rules_data.append(rule_dict)
            logger.info(f'规则详细数据: {rule_dict}')
            
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': rules_data
        })
    except Exception as e:
        logger.error(f'获取调试数据失败: {str(e)}', exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'获取调试数据失败: {str(e)}'
        }) 