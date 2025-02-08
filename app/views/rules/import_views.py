import os
import traceback
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.underwriting.rule_import_service import RuleImportService
from app.models.rules.import_record import ImportRecord
from app.models.rules.import_detail import ImportDetail
import logging
import uuid
from app.extensions import db

logger = logging.getLogger(__name__)

bp = Blueprint('rule_import', __name__)

def generate_safe_filename(original_filename):
    """生成安全的文件名，保留原始扩展名"""
    if not original_filename:
        return None
    # 获取文件扩展名
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    # 生成唯一文件名
    safe_name = f"upload_{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:8]}"
    if ext:
        safe_name = f"{safe_name}.{ext}"
    return safe_name

@bp.route('/import/test')
@login_required
def import_test():
    """导入测试页面"""
    logger.info("访问导入测试页面")
    return render_template('rules/import/test.html')

def allowed_file(filename):
    """检查文件类型是否允许"""
    logger.info(f"检查文件类型: {filename}")
    if not filename:
        logger.error("文件名为空")
        return False
    if '.' not in filename:
        logger.error(f"文件名 {filename} 没有扩展名")
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    logger.info(f"文件扩展名: {ext}")
    is_allowed = ext in ['xls', 'xlsx']
    logger.info(f"文件类型检查结果: {'允许' if is_allowed else '不允许'}")
    return is_allowed

@bp.route('/import/<import_type>', methods=['POST'])
@login_required
def import_template(import_type):
    """导入模板"""
    start_time = datetime.now()
    logger.info(f"=== 开始处理导入请求 ===")
    logger.info(f"导入类型: {import_type}")
    logger.info(f"请求时间: {start_time}")
    logger.info(f"请求用户: {current_user.username}")
    logger.info(f"请求方法: {request.method}")
    logger.info(f"请求头: {dict(request.headers)}")
    logger.info(f"请求表单数据: {request.form}")
    logger.info(f"请求文件: {request.files}")
    
    if 'file' not in request.files:
        logger.error("未上传文件")
        return jsonify({
            'code': 1,
            'message': '未上传文件'
        })
        
    file = request.files['file']
    logger.info(f"上传的文件信息:")
    logger.info(f"- 文件名: {file.filename}")
    logger.info(f"- 内容类型: {file.content_type}")
    logger.info(f"- 文件大小: {len(file.read()) if file else 0} bytes")
    file.seek(0)  # 重置文件指针
    
    if not file or not file.filename:
        logger.error("文件对象为空或文件名为空")
        return jsonify({
            'code': 1,
            'message': '请选择要上传的文件'
        })
        
    if not allowed_file(file.filename):
        logger.error(f"不支持的文件类型：{file.filename}")
        return jsonify({
            'code': 1,
            'message': '不支持的文件类型，请使用Excel文件(.xls, .xlsx)'
        })
    
    file_path = None
    try:
        # 生成安全的文件名
        original_filename = file.filename
        safe_filename = generate_safe_filename(original_filename)
        logger.info(f"原始文件名: {original_filename}")
        logger.info(f"安全化后的文件名: {safe_filename}")
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        logger.info(f"上传目录配置: {upload_folder}")
        
        if not os.path.exists(upload_folder):
            logger.info(f"创建上传目录: {upload_folder}")
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, safe_filename)
        logger.info(f"完整的文件保存路径：{file_path}")
        
        logger.info("开始保存文件...")
        file.save(file_path)
        logger.info(f"文件保存成功，大小: {os.path.getsize(file_path)} bytes")
        
        # 根据导入类型选择导入器
        if import_type == 'underwriting':
            logger.info("=== 使用核保规则导入器 ===")
            logger.info(f"当前用户ID: {current_user.id}")
            importer = RuleImportService(current_user)
            
            try:
                # 创建导入记录
                logger.info("创建导入记录...")
                importer.create_import_record(original_filename)  # 使用原始文件名
                logger.info(f"导入记录创建成功，批次号: {importer.batch_no}")
                
                # 处理导入
                logger.info("=== 开始处理导入 ===")
                logger.info("验证文件...")
                importer.validate_file(file_path)
                logger.info("文件验证通过")
                
                logger.info("读取Excel文件...")
                workbook = importer.read_excel(file_path)
                logger.info(f"Excel读取成功，包含以下sheet: {workbook.sheet_names}")
                
                logger.info("验证sheet...")
                importer.validate_sheets(workbook)
                logger.info("sheet验证通过")
                
                # 处理各个sheet
                logger.info("=== 开始处理疾病表 ===")
                diseases_df = importer.read_sheet(workbook, '疾病')
                logger.info(f"疾病表数据行数: {len(diseases_df)}")
                importer.process_diseases(diseases_df)
                logger.info("疾病表处理完成")
                
                logger.info("=== 开始处理问题表 ===")
                questions_df = importer.read_sheet(workbook, '问题')
                logger.info(f"问题表数据行数: {len(questions_df)}")
                importer.process_questions(questions_df)
                logger.info("问题表处理完成")
                
                logger.info("=== 开始处理答案表 ===")
                answers_df = importer.read_sheet(workbook, '结论')
                logger.info(f"答案表数据行数: {len(answers_df)}")
                importer.process_answers(answers_df)
                logger.info("答案表处理完成")
                
                # 提交事务
                logger.info("提交数据库事务...")
                db.session.commit()
                logger.info("数据库事务提交成功")
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"=== 导入完成 ===")
                logger.info(f"总耗时: {duration}秒")
                logger.info(f"批次号: {importer.batch_no}")
                logger.info(f"总记录数: {importer.import_record.total_count}")
                logger.info(f"成功数: {importer.import_record.success_count}")
                logger.info(f"失败数: {importer.import_record.error_count}")
                
                return jsonify({
                    'code': 0,
                    'message': '导入成功',
                    'data': {
                        'batch_no': importer.batch_no,
                        'total': importer.import_record.total_count,
                        'success': importer.import_record.success_count,
                        'error': importer.import_record.error_count,
                        'duration': duration
                    }
                })
            except Exception as e:
                logger.error("=== 导入处理失败 ===")
                logger.error(f"错误类型: {type(e).__name__}")
                logger.error(f"错误信息: {str(e)}")
                logger.error("详细堆栈:")
                logger.error(traceback.format_exc())
                
                if db.session:
                    logger.info("回滚数据库事务...")
                    db.session.rollback()
                    logger.info("数据库事务已回滚")
                
                return jsonify({
                    'code': 1,
                    'message': f'导入处理失败：{str(e)}',
                    'error_type': type(e).__name__,
                    'stack_trace': traceback.format_exc()
                })
        else:
            logger.error(f"不支持的导入类型：{import_type}")
            return jsonify({
                'code': 1,
                'message': f'不支持的导入类型：{import_type}'
            })
                
    except Exception as e:
        logger.error("=== 导入过程发生异常 ===")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error("详细堆栈:")
        logger.error(traceback.format_exc())
        
        if db.session:
            logger.info("回滚数据库事务...")
            db.session.rollback()
            logger.info("数据库事务已回滚")
            
        return jsonify({
            'code': 1,
            'message': f'导入失败：{str(e)}',
            'error_type': type(e).__name__,
            'stack_trace': traceback.format_exc()
        })
    finally:
        # 清理临时文件
        if file_path and os.path.exists(file_path):
            logger.info(f"清理临时文件：{file_path}")
            try:
                os.remove(file_path)
                logger.info("临时文件清理成功")
            except Exception as e:
                logger.error(f"清理临时文件失败：{str(e)}")
                logger.error(traceback.format_exc())

@bp.route('/import/records')
@login_required
def get_import_records():
    """获取导入记录列表"""
    logger.info("=== 获取导入记录列表 ===")
    logger.info(f"请求用户: {current_user.username}")
    
    try:
        logger.info("查询导入记录...")
        records = ImportRecord.query.order_by(ImportRecord.created_at.desc()).all()
        logger.info(f"查询到 {len(records)} 条记录")
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': [record.to_dict() for record in records]
        })
    except Exception as e:
        logger.error("获取导入记录失败")
        logger.error(f"错误信息: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'code': 1,
            'message': str(e)
        })

@bp.route('/import/records/<batch_no>/details')
@login_required
def get_import_details(batch_no):
    """获取导入详情"""
    logger.info(f"=== 获取导入详情 ===")
    logger.info(f"批次号: {batch_no}")
    logger.info(f"请求用户: {current_user.username}")
    
    try:
        # 获取导入记录
        logger.info(f"查询导入记录...")
        record = ImportRecord.query.filter_by(batch_no=batch_no).first()
        if not record:
            logger.error(f"导入记录不存在: {batch_no}")
            return jsonify({
                'code': 1,
                'message': '导入记录不存在'
            })
        
        logger.info(f"查询导入详情...")
        details = ImportDetail.query.filter_by(import_id=record.id).all()
        logger.info(f"查询到 {len(details)} 条详情记录")
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'record': record.to_dict(),
                'details': [detail.to_dict() for detail in details]
            }
        })
    except Exception as e:
        logger.error("获取导入详情失败")
        logger.error(f"错误信息: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'code': 1,
            'message': str(e)
        }) 