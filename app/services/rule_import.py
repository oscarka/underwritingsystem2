from typing import Dict, List, Tuple
from app.utils.excel import RuleExcelTemplate
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.rules.disease import Disease
from app.models.rules.question import Question
from app.models.rules.answer import Answer
from app.extensions import db
from app.models.base.enums import StatusEnum
from app.utils.logger import get_logger
import pandas as pd

class RuleImportService:
    def __init__(self):
        self.template = RuleExcelTemplate()
        self.logger = get_logger(__name__)
        
    def validate_data(self, data: Dict[str, pd.DataFrame]) -> Tuple[bool, List[str]]:
        """验证Excel数据"""
        errors = []
        
        # 验证疾病数据
        diseases_df = data.get("疾病配置")
        if diseases_df is not None:
            # 检查必填字段
            required_fields = ["疾病代码", "疾病名称", "疾病类别代码"]
            for field in required_fields:
                if diseases_df[field].isnull().any():
                    errors.append(f"疾病配置中存在空的{field}")
                    
            # 检查疾病代码唯一性
            if diseases_df["疾病代码"].duplicated().any():
                errors.append("存在重复的疾病代码")
                
        # 验证问题数据
        questions_df = data.get("问题配置")
        if questions_df is not None:
            # 检查必填字段
            required_fields = ["问题代码", "问题内容", "问题类型"]
            for field in required_fields:
                if questions_df[field].isnull().any():
                    errors.append(f"问题配置中存在空的{field}")
                    
            # 检查问题代码唯一性
            if questions_df["问题代码"].duplicated().any():
                errors.append("存在重复的问题代码")
                
        # 验证答案数据
        answers_df = data.get("答案配置")
        if answers_df is not None:
            # 检查必填字段
            required_fields = ["问题代码", "答案选项"]
            for field in required_fields:
                if answers_df[field].isnull().any():
                    errors.append(f"答案配置中存在空的{field}")
                    
            # 检查问题代码存在性
            if questions_df is not None:
                invalid_question_codes = set(answers_df["问题代码"]) - set(questions_df["问题代码"])
                if invalid_question_codes:
                    errors.append(f"答案配置中存在无效的问题代码: {invalid_question_codes}")
                    
        return len(errors) == 0, errors

    def import_excel(self, excel_file, rule_id: int = None) -> Tuple[bool, str, List[str]]:
        """导入Excel规则配置"""
        self.logger.info(f"开始导入Excel文件，rule_id={rule_id}")
        
        # 验证Excel结构
        is_valid, errors = self.template.validate_structure(excel_file)
        if not is_valid:
            self.logger.error(f"Excel文件格式错误: {errors}")
            return False, "Excel文件格式错误", errors
            
        try:
            # 读取数据
            self.logger.info("开始读取Excel数据")
            data = self.template.read_data(excel_file)
            self.logger.info(f"Excel数据读取成功，包含以下sheet: {list(data.keys())}")
            
            # 验证数据
            self.logger.info("开始验证Excel数据")
            is_valid, errors = self.validate_data(data)
            if not is_valid:
                self.logger.error(f"数据验证失败: {errors}")
                return False, "数据验证失败", errors
            self.logger.info("数据验证通过")
            
            processed_data = self.template.process_data(data)
            self.logger.info(f"数据处理完成，共处理: {len(processed_data.get('diseases', []))}个疾病, "
                           f"{len(processed_data.get('questions', []))}个问题, "
                           f"{len(processed_data.get('answers', []))}个答案")
            
            # 开始导入
            with db.session.begin_nested():
                # 获取或创建规则
                rule = None
                if rule_id:
                    rule = UnderwritingRule.query.get(rule_id)
                    if not rule:
                        self.logger.error(f"未找到ID为{rule_id}的规则")
                        return False, f"未找到ID为{rule_id}的规则", []
                    self.logger.info(f"找到规则: {rule.name} (ID: {rule.id})")
                
                # 导入疾病数据
                self.logger.info("开始导入疾病数据")
                diseases = self._import_diseases(processed_data["diseases"])
                self.logger.info(f"疾病数据导入完成，共导入{len(diseases)}条记录")
                
                # 导入问题数据
                self.logger.info("开始导入问题数据")
                questions = self._import_questions(processed_data["questions"])
                self.logger.info(f"问题数据导入完成，共导入{len(questions)}条记录")
                
                # 导入答案数据
                self.logger.info("开始导入答案数据")
                self._import_answers(processed_data["answers"], questions)
                self.logger.info("答案数据导入完成")
                
                # 关联规则
                if rule:
                    self.logger.info(f"开始关联规则数据")
                    rule.diseases = diseases
                    rule.questions = questions
                    self.logger.info(f"规则关联完成")
                    
                db.session.commit()
                self.logger.info("所有数据导入完成并提交到数据库")
                
            return True, "导入成功", []
            
        except Exception as e:
            self.logger.error(f"导入失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return False, f"导入失败: {str(e)}", []
            
    def _import_diseases(self, disease_data: List[Dict]) -> List[Disease]:
        """导入疾病数据"""
        self.logger.info(f"开始导入疾病数据，共{len(disease_data)}条记录")
        diseases = []
        
        for idx, data in enumerate(disease_data, 1):
            self.logger.info(f"\n处理第{idx}条疾病数据:")
            self.logger.info(f"- 疾病代码: {data['疾病代码']}")
            self.logger.info(f"- 疾病名称: {data['疾病']}")
            self.logger.info(f"- 疾病类别: {data['疾病类别']} ({data['疾病类别代码']})")
            self.logger.info(f"- 首问代码: {data['疾病第一个问题编码']}")
            
            disease = Disease.query.filter_by(code=data["疾病代码"]).first()
            if disease:
                self.logger.info("发现已存在的疾病记录，准备更新")
                self.logger.info(f"- 原记录ID: {disease.id}")
                self.logger.info(f"- 原记录状态: {disease.status}")
            else:
                self.logger.info("创建新的疾病记录")
                disease = Disease(
                    category_code=data["疾病类别代码"],
                    name=data["疾病"],
                    code=data["疾病代码"],
                    first_question_code=data["疾病第一个问题编码"],
                    description=data.get("备注（疾病解释）"),
                    is_common=data.get("是否为常见疾病0：否，1：是") == "1",
                    status=StatusEnum.ENABLED.value
                )
                db.session.add(disease)
                self.logger.info("新疾病记录已创建")
                
            diseases.append(disease)
            
        self.logger.info(f"疾病数据导入完成，共处理{len(diseases)}条记录")
        return diseases
        
    def _import_questions(self, question_data: List[Dict]) -> List[Question]:
        """导入问题数据"""
        self.logger.info(f"开始导入问题数据，共{len(question_data)}条记录")
        questions = []
        
        for idx, data in enumerate(question_data, 1):
            self.logger.info(f"\n处理第{idx}条问题数据:")
            self.logger.info(f"- 问题编码: {data['问题编码']}")
            self.logger.info(f"- 问题内容: {data['问题内容']}")
            self.logger.info(f"- 问题属性: {data['问题属性 P:普通问题 G:归类问题']}")
            self.logger.info(f"- 问题类型: {data['问题类型 1-单选 0-多选 2-录入问题']}")
            
            question = Question.query.filter_by(code=data["问题编码"]).first()
            if question:
                self.logger.info("发现已存在的问题记录，准备更新")
                self.logger.info(f"- 原记录ID: {question.id}")
                self.logger.info(f"- 原记录状态: {question.status}")
            else:
                self.logger.info("创建新的问题记录")
                question = Question(
                    code=data["问题编码"],
                    content=data["问题内容"],
                    question_type=data["问题属性 P:普通问题 G:归类问题"],
                    answer_type=data["问题类型 1-单选 0-多选 2-录入问题"],
                    description=data.get("备注（问题解释）"),
                    status=StatusEnum.ENABLED.value
                )
                db.session.add(question)
                self.logger.info("新问题记录已创建")
                
            questions.append(question)
            
        self.logger.info(f"问题数据导入完成，共处理{len(questions)}条记录")
        return questions
        
    def _import_answers(self, answer_data: List[Dict], questions: List[Question]):
        """导入答案数据"""
        self.logger.info(f"开始导入答案数据，共{len(answer_data)}条记录")
        
        # 创建问题代码到问题对象的映射
        question_map = {q.code: q for q in questions}
        self.logger.info(f"已加载{len(question_map)}个问题的映射关系")
        
        for idx, data in enumerate(answer_data, 1):
            self.logger.info(f"\n处理第{idx}条答案数据:")
            self.logger.info(f"- 问题编码: {data['问题编码']}")
            self.logger.info(f"- 答案内容: {data['答案选项内容']}")
            self.logger.info(f"- 医疗险结论: {data['15医疗险结论']}")
            self.logger.info(f"- 医疗特殊编码: {data['16医疗特殊编码']}")
            self.logger.info(f"- 下一问题: {data.get('19对应下一个问题编码', 'N/A')}")
            
            question = question_map.get(data["问题编码"])
            if not question:
                self.logger.warning(f"未找到问题编码{data['问题编码']}对应的问题记录，跳过此答案")
                continue
                
            self.logger.info(f"找到对应的问题记录: ID={question.id}")
            
            answer = Answer.query.filter_by(
                question_id=question.id,
                content=data["答案选项内容"]
            ).first()
            
            if answer:
                self.logger.info("发现已存在的答案记录，准备更新")
                self.logger.info(f"- 原记录ID: {answer.id}")
                self.logger.info(f"- 原记录状态: {answer.status}")
            else:
                self.logger.info("创建新的答案记录")
                answer = Answer(
                    question_id=question.id,
                    content=data["答案选项内容"],
                    special_disease_code=data.get("16医疗特殊编码"),
                    medical_conclusion=data.get("15医疗险结论"),
                    display_order=data.get("23答案展示顺序", 0),
                    next_question_code=data.get("19对应下一个问题编码"),
                    description=data.get("24备注（答案解释）"),
                    status=StatusEnum.ENABLED.value
                )
                db.session.add(answer)
                self.logger.info("新答案记录已创建")
                
        self.logger.info("答案数据导入完成") 