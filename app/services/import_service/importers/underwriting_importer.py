from app.extensions import db
from app.models.rules.disease.disease import Disease
from app.models.rules.question.question import Question
from app.models.rules.answer.answer_option import AnswerOption
from app.services.import_service.base import BaseImportService

class UnderwritingRuleImporter(BaseImportService):
    """核保规则导入器"""
    
    def __init__(self, current_user=None):
        super().__init__(current_user)
        self.required_sheets = ['疾病表', '问题表', '答案表']
        self.sheet_headers = {
            '疾病表': ['疾病名称', '疾病编码'],
            '问题表': ['问题编码', '问题内容', '问题类型', '答案类型'],
            '答案表': ['问题编码', '答案选项', '医疗险结论', '医疗特殊编码']
        }
        self.disease_map = {}  # 存储疾病编码与ID的映射
        self.question_map = {}  # 存储问题编码与ID的映射
    
    def process_data(self, workbook):
        """处理导入数据"""
        # 1. 处理疾病表
        diseases_df = self.read_sheet(workbook, '疾病表')
        self.process_diseases(diseases_df)
        
        # 2. 处理问题表
        questions_df = self.read_sheet(workbook, '问题表')
        self.process_questions(questions_df)
        
        # 3. 处理答案表
        answers_df = self.read_sheet(workbook, '答案表')
        self.process_answers(answers_df)
    
    def process_diseases(self, df):
        """处理疾病数据"""
        for index, row in df.iterrows():
            try:
                # 创建疾病记录
                disease = Disease(
                    name=row['疾病名称'],
                    code=row['疾病编码'],
                    import_batch_no=self.batch_no
                )
                db.session.add(disease)
                db.session.flush()  # 获取ID
                
                # 保存映射关系
                self.disease_map[row['疾病编码']] = disease.id
                
                # 记录成功
                self.add_import_detail(
                    sheet_name='疾病表',
                    row_number=index + 2,  # Excel行号从1开始，标题占1行
                    data_type='disease',
                    reference_id=disease.id,
                    raw_data=row.to_dict()
                )
                self.import_record.success_count += 1
                
            except Exception as e:
                # 记录失败
                self.add_import_detail(
                    sheet_name='疾病表',
                    row_number=index + 2,
                    data_type='disease',
                    status='error',
                    error_message=str(e),
                    raw_data=row.to_dict()
                )
                self.import_record.error_count += 1
    
    def process_questions(self, df):
        """处理问题数据"""
        for index, row in df.iterrows():
            try:
                # 创建问题记录
                question = Question(
                    code=row['问题编码'],
                    content=row['问题内容'],
                    question_type=row['问题类型'],
                    answer_type=row['答案类型'],
                    import_batch_no=self.batch_no
                )
                
                # 关联疾病
                disease_code = row['问题编码'].split('_')[1]  # 从问题编码中提取疾病编码
                if disease_code in self.disease_map:
                    question.disease_id = self.disease_map[disease_code]
                else:
                    raise ValueError(f'未找到对应的疾病记录：{disease_code}')
                
                db.session.add(question)
                db.session.flush()
                
                # 保存映射关系
                self.question_map[row['问题编码']] = question.id
                
                # 记录成功
                self.add_import_detail(
                    sheet_name='问题表',
                    row_number=index + 2,
                    data_type='question',
                    reference_id=question.id,
                    raw_data=row.to_dict()
                )
                self.import_record.success_count += 1
                
            except Exception as e:
                # 记录失败
                self.add_import_detail(
                    sheet_name='问题表',
                    row_number=index + 2,
                    data_type='question',
                    status='error',
                    error_message=str(e),
                    raw_data=row.to_dict()
                )
                self.import_record.error_count += 1
    
    def process_answers(self, df):
        """处理答案数据"""
        for index, row in df.iterrows():
            try:
                question_code = row['问题编码']
                if question_code not in self.question_map:
                    raise ValueError(f'未找到对应的问题记录：{question_code}')
                
                # 创建答案选项
                answer = AnswerOption(
                    question_id=self.question_map[question_code],
                    content=row['答案选项'],
                    medical_conclusion=row['医疗险结论'],
                    medical_special_code=row['医疗特殊编码'],
                    import_batch_no=self.batch_no
                )
                db.session.add(answer)
                db.session.flush()
                
                # 记录成功
                self.add_import_detail(
                    sheet_name='答案表',
                    row_number=index + 2,
                    data_type='answer',
                    reference_id=answer.id,
                    raw_data=row.to_dict()
                )
                self.import_record.success_count += 1
                
            except Exception as e:
                # 记录失败
                self.add_import_detail(
                    sheet_name='答案表',
                    row_number=index + 2,
                    data_type='answer',
                    status='error',
                    error_message=str(e),
                    raw_data=row.to_dict()
                )
                self.import_record.error_count += 1 