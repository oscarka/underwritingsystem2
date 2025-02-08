import os
import uuid
import pandas as pd
import logging
from datetime import datetime
from app.extensions import db
from app.models.rules.disease.disease import Disease
from app.models.rules.question.question import Question
from app.models.rules.answer.answer_option import AnswerOption
from app.models.rules.import_record import ImportRecord
from app.models.rules.import_detail import ImportDetail
from app.models.rules.underwriting.underwriting_rule import UnderwritingRule

logger = logging.getLogger(__name__)

class RuleImportService:
    """规则导入服务"""
    
    def __init__(self, current_user=None):
        self.batch_no = self.generate_batch_no()
        logger.info(f"创建导入服务实例 [batch_no={self.batch_no}]")
        self.import_record = None
        self.current_user = current_user
        self.required_sheets = ['疾病', '问题', '结论']
        self.sheet_headers = {
            '疾病': ['疾病', '疾病编码', '疾病大类编码', '疾病大类', '疾病第一个问题编码', '备注（疾病解释）', '是否为常见疾病0：否，1：是'],
            '问题': ['问题编码', '问题内容', '问题属性 P:普通问题 G:归类问题', '问题类型 1-单选 0-多选 2-录入问题', '备注（问题解释）'],
            '结论': ['问题编码', '8答案内容', '10重疾结论', '11重疾特殊编码', '12重疾特殊描述', '15医疗险结论', '16医疗特殊编码', '17医疗特殊描述', '19对应下一个问题编码（结束为空）', '23答案展示顺序', '24备注（答案的解释）']
        }
        self.disease_map = {}  # 存储疾病编码与ID的映射
        self.question_map = {}  # 存储问题编码与ID的映射
        
        logger.info("导入服务初始化完成", extra={
            'batch_no': self.batch_no,
            'user_id': str(self.current_user.id) if self.current_user else None,
            'required_sheets': self.required_sheets
        })
    
    @staticmethod
    def generate_batch_no():
        """生成批次号"""
        return f"IMP{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
    
    def create_import_record(self, file_name):
        """创建导入记录"""
        logger.info("创建导入记录", extra={
            'batch_no': self.batch_no,
            'file_name': file_name,
            'user_id': str(self.current_user.id) if self.current_user else None
        })
        
        created_by = str(self.current_user.id) if self.current_user else None
        
        self.import_record = ImportRecord(
            batch_no=self.batch_no,
            import_type='underwriting',
            file_name=file_name,
            status='pending',
            created_by=created_by
        )
        
        db.session.add(self.import_record)
        db.session.flush()
        
        logger.info("导入记录创建成功", extra={
            'batch_no': self.batch_no,
            'import_id': self.import_record.id
        })
        return self.import_record
    
    def add_import_detail(self, sheet_name, row_number, data_type, status='success', 
                         error_message=None, reference_id=None, raw_data=None):
        """添加导入详情"""
        detail = ImportDetail(
            import_id=self.import_record.id,
            sheet_name=sheet_name,
            row_number=row_number,
            status=status,
            error_message=error_message,
            data_type=data_type,
            reference_id=reference_id,
            raw_data=raw_data
        )
        
        if status == 'error':
            logger.error("导入错误", extra={
                'batch_no': self.batch_no,
                'sheet': sheet_name,
                'row': row_number,
                'error': error_message
            })
        
        db.session.add(detail)
        return detail
    
    def validate_file(self, file_path):
        """验证文件"""
        logger.info(f"开始验证文件：{file_path}")
        if not os.path.exists(file_path):
            logger.error(f"文件不存在：{file_path}")
            raise ValueError('文件不存在')
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"文件大小: {file_size} bytes")
        if file_size == 0:
            logger.error("文件为空")
            raise ValueError('文件为空')
            
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        logger.info(f"文件扩展名: {ext}")
        
        # 如果扩展名为空，尝试从文件内容判断
        if not ext:
            try:
                import magic
                mime = magic.Magic(mime=True)
                file_type = mime.from_file(file_path)
                logger.info(f"MIME类型: {file_type}")
                if file_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                               'application/vnd.ms-excel']:
                    logger.info("通过MIME类型验证")
                    return
            except ImportError:
                logger.warning("python-magic库未安装，跳过MIME类型检查")
                pass
            
        # 验证扩展名
        if ext not in ['.xlsx', '.xls']:
            logger.error(f"不支持的文件格式：{ext}")
            raise ValueError('不支持的文件格式，请使用Excel文件(.xlsx, .xls)')
            
        logger.info("文件验证通过")
    
    def validate_sheets(self, workbook):
        """验证sheet"""
        logger.info("开始验证Excel表单")
        sheet_names = workbook.sheet_names
        logger.info(f"Excel包含的表单：{', '.join(sheet_names)}")
        
        for required_sheet in self.required_sheets:
            if required_sheet not in sheet_names:
                logger.error(f"缺少必需的sheet：{required_sheet}")
                raise ValueError(f'缺少必需的sheet：{required_sheet}')
                
        logger.info("表单验证通过")
    
    def validate_headers(self, df, sheet_name):
        """验证表头"""
        logger.info(f"开始验证表头 [sheet={sheet_name}]")
        
        # 获取当前sheet的所有列名
        current_headers = df.columns.tolist()
        
        # 获取必需的表头
        required_headers = self.sheet_headers.get(sheet_name, [])
        
        logger.info(f"表头验证信息", extra={
            'sheet_name': sheet_name,
            'current_headers': current_headers,
            'required_headers': required_headers,
            'batch_no': self.batch_no
        })
        
        # 检查是否缺少必需的表头
        missing_headers = []
        for header in required_headers:
            if header not in current_headers:
                missing_headers.append(header)
                logger.error(f"缺少必需的表头", extra={
                    'sheet_name': sheet_name,
                    'missing_header': header,
                    'batch_no': self.batch_no
                })
        
        if missing_headers:
            error_msg = f'Sheet {sheet_name} 缺少必需的表头：{", ".join(missing_headers)}'
            logger.error(error_msg, extra={
                'sheet_name': sheet_name,
                'missing_headers': missing_headers,
                'batch_no': self.batch_no
            })
            raise ValueError(error_msg)
            
        logger.info(f"表头验证通过 [sheet={sheet_name}]")
        
        # 打印前三行数据预览（表头、说明行、第一条数据）
        logger.info(f"数据预览（前三行）：")
        preview_data = df.head(3).to_dict('records')
        for idx, row in enumerate(preview_data, 1):
            row_type = "表头" if idx == 1 else "说明行" if idx == 2 else "数据行"
            logger.info(f"第{idx}行 ({row_type}): {row}")
        
        # 检查第二行是否为说明行
        if len(df) >= 2:
            second_row = df.iloc[1].to_dict()
            logger.info("验证说明行", extra={
                'sheet_name': sheet_name,
                'row_data': second_row,
                'batch_no': self.batch_no
            })
    
    def read_excel(self, file_path):
        """读取Excel文件"""
        logger.info(f"开始读取Excel文件：{file_path}")
        try:
            workbook = pd.ExcelFile(file_path)
            logger.info("Excel文件读取成功")
            return workbook
        except Exception as e:
            logger.error(f"读取Excel文件失败：{str(e)}")
            raise ValueError(f'读取Excel文件失败：{str(e)}')
    
    def read_sheet(self, workbook, sheet_name):
        """读取sheet"""
        logger.info(f"开始读取sheet：{sheet_name}")
        try:
            logger.info(f"尝试读取 {sheet_name} 的数据...")
            df = pd.read_excel(workbook, sheet_name)
            
            # 打印基本信息
            logger.info(f"Sheet {sheet_name} 基本信息：")
            logger.info(f"- 总行数：{len(df)}")
            logger.info(f"- 总列数：{len(df.columns)}")
            logger.info(f"- 列名：{', '.join(df.columns.tolist())}")
            
            # 检查数据是否为空
            if df.empty:
                logger.warning(f"Sheet {sheet_name} 数据为空")
                raise ValueError(f'Sheet {sheet_name} 数据为空')
            
            # 验证表头
            self.validate_headers(df, sheet_name)
            
            logger.info(f"Sheet {sheet_name} 读取成功")
            return df
            
        except Exception as e:
            logger.error(f"读取sheet {sheet_name} 失败：{str(e)}")
            raise ValueError(f'读取sheet {sheet_name} 失败：{str(e)}')
    
    def process_diseases(self, df):
        """处理疾病数据"""
        logger.info("开始处理疾病数据", extra={
            'batch_no': self.batch_no,
            'total_rows': len(df) - 1  # 减去表头行
        })
        success_count = 0
        error_count = 0
        
        try:
            for index, row in df.iterrows():
                # 跳过表头行
                if index == 0:  # 只跳过第1行（表头）
                    logger.info(f"跳过第{index + 1}行", extra={
                        'batch_no': self.batch_no,
                        'row_index': index + 1,
                        'row_type': '表头'
                    })
                    continue
                
                try:
                    logger.info(f"处理第{index + 1}行疾病数据", extra={
                        'row_index': index + 1,
                        'batch_no': self.batch_no,
                        'disease_code': row.get('疾病编码', ''),
                        'disease_name': row.get('疾病', ''),
                        'row_data': row.to_dict()
                    })
                    
                    # 数据验证
                    disease_code = str(row['疾病编码']).strip()
                    disease_name = str(row['疾病']).strip()
                    category_code = str(row.get('疾病大类编码', '')).strip()
                    category_name = str(row.get('疾病大类', '')).strip()
                    first_question_code = str(row.get('疾病第一个问题编码', '')).strip()
                    
                    # 验证必填字段
                    if not disease_code:
                        raise ValueError('疾病编码不能为空')
                    if not disease_name:
                        raise ValueError('疾病名称不能为空')
                    if not category_code:
                        raise ValueError('疾病大类编码不能为空')
                    if not category_name:
                        raise ValueError('疾病大类名称不能为空')
                    if not first_question_code:
                        raise ValueError('疾病第一个问题编码不能为空')
                    
                    # 创建疾病记录
                    disease = Disease(
                        name=disease_name,
                        code=disease_code,
                        category_code=category_code,
                        category_name=category_name,
                        first_question_code=first_question_code,
                        description=row.get('备注（疾病解释）'),
                        is_common=str(row.get('是否为常见疾病0：否，1：是', '0')).strip() == '1',
                        batch_no=self.batch_no,
                        rule_id=self.rule.id  # 添加规则ID
                    )
                    
                    logger.info("创建疾病记录", extra={
                        'batch_no': self.batch_no,
                        'disease_code': disease_code,
                        'disease_name': disease_name,
                        'disease_data': disease.to_dict()
                    })
                    
                    db.session.add(disease)
                    db.session.flush()  # 立即获取ID
                    
                    # 保存映射关系
                    self.disease_map[disease_code] = disease.id
                    
                    # 记录成功
                    self.add_import_detail(
                        sheet_name='疾病',
                        row_number=index + 1,
                        data_type='disease',
                        reference_id=disease.id,
                        raw_data=row.to_dict()
                    )
                    success_count += 1
                    logger.info("疾病记录创建成功", extra={
                        'disease_id': disease.id,
                        'disease_code': disease_code,
                        'batch_no': self.batch_no
                    })
                    
                except Exception as e:
                    logger.error("处理疾病数据失败", extra={
                        'row_index': index + 1,
                        'batch_no': self.batch_no,
                        'error': str(e),
                        'disease_code': row.get('疾病编码', ''),
                        'disease_name': row.get('疾病', ''),
                        'row_data': row.to_dict()
                    })
                    logger.error(f"错误详情: {str(e)}")
                    self.add_import_detail(
                        sheet_name='疾病',
                        row_number=index + 1,
                        data_type='disease',
                        status='error',
                        error_message=str(e),
                        raw_data=row.to_dict()
                    )
                    error_count += 1
            
            # 最后执行一次flush
            logger.info("执行最终flush", extra={
                'batch_no': self.batch_no,
                'success_count': success_count,
                'error_count': error_count
            })
            db.session.flush()
            
            # 更新导入记录的计数
            self.import_record.success_count += success_count
            self.import_record.error_count += error_count
            
            logger.info("疾病数据处理完成", extra={
                'batch_no': self.batch_no,
                'success_count': success_count,
                'error_count': error_count,
                'total_count': success_count + error_count,
                'disease_map': self.disease_map
            })
            
        except Exception as e:
            logger.error("处理疾病数据时发生错误", extra={
                'batch_no': self.batch_no,
                'error': str(e)
            })
            raise
    
    def process_questions(self, df):
        """处理问题数据"""
        logger.info("开始处理问题数据", extra={
            'batch_no': self.batch_no,
            'total_rows': len(df) - 1  # 减去表头行
        })
        success_count = 0
        error_count = 0
        
        try:
            for index, row in df.iterrows():
                # 跳过表头行
                if index == 0:  # 只跳过第1行（表头）
                    logger.info(f"跳过第{index + 1}行", extra={
                        'batch_no': self.batch_no,
                        'row_index': index + 1,
                        'row_type': '表头'
                    })
                    continue
                
                try:
                    logger.info(f"处理第{index + 1}行问题数据", extra={
                        'row_index': index + 1,
                        'batch_no': self.batch_no,
                        'question_code': row.get('问题编码', ''),
                        'question_content': row.get('问题内容', ''),
                        'row_data': row.to_dict()
                    })
                    
                    # 数据验证
                    question_code = str(row['问题编码']).strip()
                    question_content = str(row['问题内容']).strip()
                    
                    # 验证必填字段
                    if not question_code:
                        raise ValueError('问题编码不能为空')
                    if not question_content:
                        raise ValueError('问题内容不能为空')
                    
                    # 创建问题记录
                    question = Question(
                        code=question_code,
                        content=question_content,
                        batch_no=self.batch_no
                    )
                    
                    # 解析问题属性
                    question_property = str(row['问题属性 P:普通问题 G:归类问题']).strip().upper()
                    logger.info(f"问题属性原始值: {question_property}")
                    if question_property == 'P':
                        question.is_group = False
                    elif question_property == 'G':
                        question.is_group = True
                    else:
                        logger.warning(f"未知的问题属性值: {question_property}，默认设置为普通问题")
                        question.is_group = False
                    
                    # 解析问题类型
                    question_type_str = str(row['问题类型 1-单选 0-多选 2-录入问题']).strip()
                    logger.info(f"问题类型原始值: {question_type_str}")
                    
                    # 提取数字部分
                    import re
                    type_match = re.search(r'[012]', question_type_str)
                    if type_match:
                        question_type = type_match.group()
                        if question_type == '1':
                            question.question_type = 1  # 单选
                            question.answer_type = 'radio'
                        elif question_type == '0':
                            question.question_type = 0  # 多选
                            question.answer_type = 'checkbox'
                        elif question_type == '2':
                            question.question_type = 2  # 录入问题
                            question.answer_type = 'text'
                    else:
                        logger.warning(f"未能识别问题类型: {question_type_str}，默认设置为单选")
                        question.question_type = 1
                        question.answer_type = 'radio'
                    
                    logger.info(f"设置问题类型: {question.question_type}, 答案类型: {question.answer_type}")
                    
                    # 设置备注
                    question.remark = row.get('备注（问题解释）', '')
                    
                    # 关联疾病
                    try:
                        disease_code = row['问题编码'].split('_')[1]  # 从问题编码中提取疾病编码
                        logger.info(f"从问题编码 {row['问题编码']} 提取疾病编码: {disease_code}")
                        
                        if disease_code in self.disease_map:
                            question.disease_id = self.disease_map[disease_code]
                            logger.info(f"关联疾病ID: {question.disease_id}, 疾病编码: {disease_code}")
                        else:
                            error_msg = f'未找到对应的疾病记录：{disease_code}'
                            logger.error(error_msg)
                            raise ValueError(error_msg)
                            
                    except (IndexError, KeyError) as e:
                        error_msg = f'问题编码格式错误或未找到对应疾病：{row["问题编码"]}'
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    logger.info(f"创建问题记录：{question.to_dict()}")
                    db.session.add(question)
                    db.session.flush()  # 立即获取ID
                    
                    # 保存映射关系
                    self.question_map[question_code] = question.id
                    logger.info(f"保存问题映射关系：{question_code} -> {question.id}")
                    
                    # 记录成功
                    self.add_import_detail(
                        sheet_name='问题',
                        row_number=index + 1,
                        data_type='question',
                        reference_id=question.id,
                        raw_data=row.to_dict()
                    )
                    success_count += 1
                    logger.info("问题记录创建成功", extra={
                        'question_id': question.id,
                        'question_code': question_code,
                        'batch_no': self.batch_no
                    })
                    
                except Exception as e:
                    logger.error("处理问题数据失败", extra={
                        'row_index': index + 1,
                        'batch_no': self.batch_no,
                        'error': str(e),
                        'question_code': row.get('问题编码', ''),
                        'question_content': row.get('问题内容', ''),
                        'row_data': row.to_dict()
                    })
                    self.add_import_detail(
                        sheet_name='问题',
                        row_number=index + 1,
                        data_type='question',
                        status='error',
                        error_message=str(e),
                        raw_data=row.to_dict()
                    )
                    error_count += 1
            
            # 最后执行一次flush
            logger.info("执行最终flush", extra={
                'batch_no': self.batch_no,
                'success_count': success_count,
                'error_count': error_count
            })
            db.session.flush()
            
            # 更新导入记录的计数
            self.import_record.success_count += success_count
            self.import_record.error_count += error_count
            
            logger.info("问题数据处理完成", extra={
                'batch_no': self.batch_no,
                'success_count': success_count,
                'error_count': error_count,
                'total_count': success_count + error_count,
                'question_map': self.question_map
            })
            
        except Exception as e:
            logger.error("处理问题数据时发生错误", extra={
                'batch_no': self.batch_no,
                'error': str(e)
            })
            raise
    
    def process_answers(self, df):
        """处理答案数据"""
        logger.info("开始处理答案数据", extra={
            'batch_no': self.batch_no,
            'total_rows': len(df) - 1  # 减去表头行
        })
        success_count = 0
        error_count = 0
        
        try:
            for index, row in df.iterrows():
                # 跳过表头行
                if index == 0:  # 只跳过第1行（表头）
                    logger.info(f"跳过第{index + 1}行", extra={
                        'batch_no': self.batch_no,
                        'row_index': index + 1,
                        'row_type': '表头'
                    })
                    continue
                
                try:
                    logger.info(f"处理第{index + 1}行答案数据", extra={
                        'row_index': index + 1,
                        'batch_no': self.batch_no,
                        'question_code': row.get('问题编码', ''),
                        'answer_content': row.get('8答案内容', ''),
                        'row_data': row.to_dict()
                    })
                    
                    # 数据验证
                    question_code = str(row['问题编码']).strip()
                    answer_content = str(row['8答案内容']).strip()
                    
                    # 验证必填字段
                    if not question_code:
                        raise ValueError('问题编码不能为空')
                    if not answer_content:
                        raise ValueError('答案内容不能为空')
                    
                    # 检查问题编码是否存在
                    logger.info(f"检查问题编码 {question_code} 是否存在", extra={
                        'question_code': question_code,
                        'question_map': self.question_map
                    })
                    if question_code not in self.question_map:
                        error_msg = f'未找到对应的问题记录：{question_code}'
                        logger.error(error_msg, extra={
                            'batch_no': self.batch_no,
                            'question_code': question_code,
                            'available_codes': list(self.question_map.keys())
                        })
                        raise ValueError(error_msg)
                    
                    # 创建答案选项（只使用模型中存在的字段）
                    answer = AnswerOption(
                        question_id=self.question_map[question_code],
                        content=answer_content,
                        medical_conclusion=row.get('15医疗险结论'),
                        medical_special_code=row.get('16医疗特殊编码'),
                        batch_no=self.batch_no
                    )
                    
                    logger.info("创建答案选项", extra={
                        'batch_no': self.batch_no,
                        'question_id': self.question_map[question_code],
                        'answer_content': answer_content,
                        'answer_data': answer.to_dict()
                    })
                    
                    db.session.add(answer)
                    db.session.flush()  # 立即获取ID
                    
                    # 记录成功
                    self.add_import_detail(
                        sheet_name='结论',
                        row_number=index + 1,
                        data_type='answer',
                        reference_id=answer.id,
                        raw_data=row.to_dict()
                    )
                    success_count += 1
                    logger.info("答案记录创建成功", extra={
                        'answer_id': answer.id,
                        'question_code': question_code,
                        'batch_no': self.batch_no
                    })
                    
                except Exception as e:
                    logger.error("处理答案数据失败", extra={
                        'row_index': index + 1,
                        'batch_no': self.batch_no,
                        'error': str(e),
                        'question_code': row.get('问题编码', ''),
                        'answer_content': row.get('8答案内容', ''),
                        'row_data': row.to_dict()
                    })
                    logger.error(f"错误详情: {str(e)}")
                    self.add_import_detail(
                        sheet_name='结论',
                        row_number=index + 1,
                        data_type='answer',
                        status='error',
                        error_message=str(e),
                        raw_data=row.to_dict()
                    )
                    error_count += 1
            
            # 最后执行一次flush
            logger.info("执行最终flush", extra={
                'batch_no': self.batch_no,
                'success_count': success_count,
                'error_count': error_count
            })
            db.session.flush()
            
            # 更新导入记录的计数
            self.import_record.success_count += success_count
            self.import_record.error_count += error_count
            
            logger.info("答案数据处理完成", extra={
                'batch_no': self.batch_no,
                'success_count': success_count,
                'error_count': error_count,
                'total_count': success_count + error_count
            })
            
        except Exception as e:
            logger.error("处理答案数据时发生错误", extra={
                'batch_no': self.batch_no,
                'error': str(e)
            })
            raise
    
    def process(self, file_path, rule_id=None):
        """处理导入"""
        logger.info(f"开始处理导入：文件={file_path}, 规则ID={rule_id}")
        try:
            # 验证文件
            self.validate_file(file_path)
            
            # 创建导入记录
            self.create_import_record(os.path.basename(file_path))
            self.import_record.status = 'processing'
            self.import_record.rule_id = rule_id  # 记录规则ID
            db.session.flush()
            
            # 读取Excel文件
            workbook = self.read_excel(file_path)
            
            # 验证sheet
            self.validate_sheets(workbook)
            
            # 开始事务
            logger.info("开始导入数据事务")
            with db.session.begin_nested():
                # 处理数据
                self.process_diseases(self.read_sheet(workbook, '疾病'))
                self.process_questions(self.read_sheet(workbook, '问题'))
                self.process_answers(self.read_sheet(workbook, '结论'))
                
                # 更新导入记录
                self.import_record.status = 'completed'
                self.import_record.total_count = (
                    self.import_record.success_count + self.import_record.error_count
                )
                
            db.session.commit()
            logger.info(f"导入完成：成功={self.import_record.success_count}, 失败={self.import_record.error_count}")
            return True, self.import_record
            
        except Exception as e:
            logger.error(f"导入失败：{str(e)}")
            db.session.rollback()
            if self.import_record:
                self.import_record.status = 'failed'
                self.import_record.error_details = str(e)
                db.session.commit()
            return False, str(e) 