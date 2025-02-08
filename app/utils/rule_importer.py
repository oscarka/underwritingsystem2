import pandas as pd
import logging
from datetime import datetime
from app import db
from app.models.rules.disease.disease import Disease
from app.models.rules.question.question import Question
from app.models.rules.conclusion.conclusion import Conclusion

# 设置日志
logger = logging.getLogger(__name__)

class RuleImporter:
    """规则导入工具类"""
    
    def __init__(self, rule_id):
        self.rule_id = rule_id
        self.import_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def validate_headers(self, df, sheet_name, required_headers):
        """验证表头"""
        headers = df.columns.tolist()
        logger.info(f"{self.import_time} - [{sheet_name}] 实际表头: {headers}")
        logger.info(f"{self.import_time} - [{sheet_name}] 要求表头: {required_headers}")
        
        missing_headers = set(required_headers) - set(headers)
        if missing_headers:
            error_msg = f"[{sheet_name}] 缺少必需的列: {', '.join(missing_headers)}"
            logger.error(f"{self.import_time} - {error_msg}")
            raise ValueError(error_msg)
        return True
        
    def import_diseases(self, df):
        """导入疾病数据"""
        logger.info(f"{self.import_time} - 开始导入疾病数据")
        
        # 打印原始DataFrame的详细信息
        logger.info(f"{self.import_time} - 原始DataFrame信息:")
        logger.info(f"原始DataFrame形状: {df.shape}")
        logger.info(f"原始列名: {list(df.columns)}")
        logger.info(f"原始数据预览:\n{df.to_string()}")  # 显示所有行，看看具体数据
        
        # 检查是否有数据
        if df.empty:
            raise ValueError("Excel中疾病sheet页没有数据!")
        
        # 跳过第一行（表头），保留数据行
        df = df.iloc[1:]  # 只跳过表头
        df = df.reset_index(drop=True)
        
        # 过滤掉规则说明行（第一行）
        df = df[~df['疾病大类编码'].str.contains('不能为空', na=False)]
        df = df.reset_index(drop=True)
        
        logger.info(f"{self.import_time} - 处理后数据预览:\n{df.to_string()}")
        
        # 如果处理后没有数据，抛出异常
        if df.empty:
            raise ValueError("处理后没有疾病数据!")
        
        success_count = 0
        error_count = 0
        
        # 遍历每一行数据
        for index, row in df.iterrows():
            try:
                # 打印当前处理的行
                logger.info(f"{self.import_time} - 正在处理第{index+1}行疾病数据:")
                logger.info(f"行数据: {row.to_dict()}")
                
                # 数据验证
                required_fields = ['疾病大类编码', '疾病大类', '疾病编码', '疾病', '疾病第一个问题编码']
                empty_fields = [f for f in required_fields if pd.isna(row[f])]
                if empty_fields:
                    logger.error(f"{self.import_time} - 第{index+1}行以下必填字段为空: {empty_fields}")
                    error_count += 1
                    continue
                
                # 检查疾病编码和疾病名称的唯一性
                disease_code = str(row['疾病编码']).strip()
                disease_name = str(row['疾病']).strip()
                
                existing = Disease.query.filter(
                    (Disease.code == disease_code) | 
                    (Disease.name == disease_name)
                ).first()
                
                if existing:
                    logger.error(f"{self.import_time} - 第{index+1}行疾病编码或疾病名称重复，跳过")
                    error_count += 1
                    continue
                
                # 创建疾病记录
                disease = Disease(
                    category_code=str(row['疾病大类编码']).strip(),
                    category_name=str(row['疾病大类']).strip(),
                    code=disease_code,
                    name=disease_name,
                    first_question_code=str(row['疾病第一个问题编码']).strip(),
                    description=str(row['备注（疾病解释）']).strip() if not pd.isna(row['备注（疾病解释）']) else None,
                    is_common=bool(int(row['是否为常见疾病0：否，1：是'])) if not pd.isna(row['是否为常见疾病0：否，1：是']) else False,
                    rule_id=self.rule_id,
                    status='active',
                    batch_no=self.import_time
                )
                
                db.session.add(disease)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"{self.import_time} - 导入第{index+1}行疾病数据失败:")
                logger.error(f"错误信息: {str(e)}")
                logger.error(f"行数据: {row.to_dict()}")
                logger.error("详细错误堆栈:", exc_info=True)
                continue
        
        try:
            db.session.commit()
            logger.info(f"{self.import_time} - 疾病数据导入完成. 成功: {success_count}, 失败: {error_count}")
        except Exception as e:
            logger.error(f"{self.import_time} - 最终提交失败: {str(e)}", exc_info=True)
            db.session.rollback()
            raise
        
        return success_count, error_count
        
    def import_questions(self, df):
        """导入问题数据"""
        logger.info(f"{self.import_time} - 开始导入问题数据")
        
        # 打印原始DataFrame的详细信息
        logger.info(f"{self.import_time} - 原始DataFrame信息:")
        logger.info(f"原始DataFrame形状: {df.shape}")
        logger.info(f"原始列名: {list(df.columns)}")
        logger.info(f"原始数据预览:\n{df.head(10).to_string()}")
        
        # 检查是否有数据
        if df.empty:
            raise ValueError("Excel中问题sheet页没有数据!")
        
        # 跳过第一行（表头），保留数据行
        df = df.iloc[1:]  # 只跳过表头
        df = df.reset_index(drop=True)
        
        # 过滤掉规则说明行
        df = df[~df['问题编码'].str.contains('不能为空', na=False)]
        df = df.reset_index(drop=True)
        
        logger.info(f"{self.import_time} - 处理后数据预览:\n{df.head(10).to_string()}")
        
        # 如果处理后没有数据，抛出异常
        if df.empty:
            raise ValueError("处理后没有问题数据!")
        
        success_count = 0
        error_count = 0
        
        # 遍历每一行数据，跳过第一行（规则说明）
        for index, row in df.iterrows():
            try:
                # 打印当前处理的行
                logger.info(f"{self.import_time} - 正在处理第{index+1}行问题数据:")
                logger.info(f"行数据: {row.to_dict()}")
                
                # 数据验证
                if pd.isna(row['问题编码']) or pd.isna(row['问题内容']):
                    logger.error(f"{self.import_time} - 第{index+1}行必填字段为空，跳过")
                    error_count += 1
                    continue
                
                # 检查问题编码唯一性
                if Question.query.filter_by(question_code=row['问题编码']).first():
                    logger.error(f"{self.import_time} - 第{index+1}行问题编码重复，跳过")
                    error_count += 1
                    continue
                
                # 创建问题记录
                question = Question(
                    question_code=str(row['问题编码']).strip(),
                    content=str(row['问题内容']).strip(),
                    attribute=str(row['问题属性 P:普通问题 G:归类问题']).strip() if not pd.isna(row['问题属性 P:普通问题 G:归类问题']) else None,
                    question_type=str(row['问题类型 1-单选 0-多选 2-录入问题']).strip() if not pd.isna(row['问题类型 1-单选 0-多选 2-录入问题']) else None,
                    remark=str(row['备注（问题解释）']).strip() if not pd.isna(row['备注（问题解释）']) else None,
                    rule_id=self.rule_id
                )
                
                db.session.add(question)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"{self.import_time} - 导入第{index+1}行问题数据失败:")
                logger.error(f"错误信息: {str(e)}")
                logger.error(f"行数据: {row.to_dict()}")
                logger.error("详细错误堆栈:", exc_info=True)
                continue
        
        try:
            db.session.commit()
            logger.info(f"{self.import_time} - 问题数据导入完成. 成功: {success_count}, 失败: {error_count}")
        except Exception as e:
            logger.error(f"{self.import_time} - 最终提交失败: {str(e)}", exc_info=True)
            db.session.rollback()
            raise
        
        return success_count, error_count
        
    def import_conclusions(self, df):
        """导入结论数据"""
        logger.info(f"{self.import_time} - 开始导入结论数据")
        
        # 打印原始DataFrame的详细信息
        logger.info(f"{self.import_time} - 原始DataFrame信息:")
        logger.info(f"原始DataFrame形状: {df.shape}")
        logger.info(f"原始列名: {list(df.columns)}")
        logger.info(f"原始数据预览:\n{df.head(10).to_string()}")
        
        # 检查是否有数据
        if df.empty:
            logger.error(f"{self.import_time} - Excel中结论sheet页为空")
            raise ValueError("Excel中结论sheet页没有数据!")
        
        # 跳过第一行（表头），保留数据行
        df = df.iloc[1:]  # 只跳过表头
        df = df.reset_index(drop=True)
        
        # 过滤掉规则说明行
        df = df[~df['问题编码'].str.contains('不能为空', na=False)]
        df = df.reset_index(drop=True)
        
        logger.info(f"{self.import_time} - 处理后数据预览:\n{df.head(10).to_string()}")
        
        # 如果处理后没有数据，抛出异常
        if df.empty:
            logger.error(f"{self.import_time} - 处理后结论数据为空")
            raise ValueError("处理后没有结论数据!")
        
        success_count = 0
        error_count = 0
        
        # 遍历每一行数据，跳过第一行（规则说明）
        for index, row in df.iterrows():
            try:
                # 打印当前处理的行
                logger.info(f"{self.import_time} - 正在处理第{index+1}行结论数据:")
                logger.info(f"行数据: {row.to_dict()}")
                
                # 数据验证
                if pd.isna(row['问题编码']) or pd.isna(row['8答案内容']):
                    logger.error(f"{self.import_time} - 第{index+1}行必填字段为空，问题编码: {row.get('问题编码', 'NA')}, 答案内容: {row.get('8答案内容', 'NA')}")
                    error_count += 1
                    continue
                
                # 检查问题编码是否存在
                question_code = str(row['问题编码']).strip()
                logger.info(f"{self.import_time} - 检查问题编码 {question_code} 是否存在")
                if not Question.query.filter_by(question_code=question_code).first():
                    logger.error(f"{self.import_time} - 第{index+1}行问题编码 {question_code} 不存在")
                    error_count += 1
                    continue
                
                # 检查下一个问题编码是否存在（如果有）
                next_code = row['19对应下一个问题编码（结束为空）']
                if not pd.isna(next_code):
                    next_code = str(next_code).strip()
                    logger.info(f"{self.import_time} - 检查下一个问题编码 {next_code} 是否存在")
                    if not Question.query.filter_by(question_code=next_code).first():
                        logger.error(f"{self.import_time} - 第{index+1}行下一个问题编码 {next_code} 不存在")
                        error_count += 1
                        continue
                
                # 记录创建结论记录前的参数
                logger.info(f"{self.import_time} - 准备创建结论记录，参数如下:")
                conclusion_params = {
                    'question_code': str(row['问题编码']).strip(),
                    'answer_content': str(row['8答案内容']).strip() if not pd.isna(row['8答案内容']) else None,
                    'next_question_code': str(row['19对应下一个问题编码']).strip() if not pd.isna(row['19对应下一个问题编码']) else None,
                    'medical_conclusion': str(row['15医疗险结论']).strip() if not pd.isna(row['15医疗险结论']) else None,
                    'critical_illness_conclusion': str(row['11重疾结论']).strip() if not pd.isna(row['11重疾结论']) else None,
                    'medical_special_desc': str(row['17医疗特殊说明']).strip() if not pd.isna(row['17医疗特殊说明']) else None,
                    'critical_illness_special_desc': str(row['12重疾特殊说明']).strip() if not pd.isna(row['12重疾特殊说明']) else None,
                    'medical_special_code': str(row['16医疗特殊编码']).strip() if not pd.isna(row['16医疗特殊编码']) else None,
                    'critical_illness_special_code': str(row['11重疾特殊编码']).strip() if not pd.isna(row['11重疾特殊编码']) else None,
                    'display_order': int(row['23答案展示顺序']) if not pd.isna(row['23答案展示顺序']) else 0,
                    'remark': str(row['24备注（答案解释）']).strip() if not pd.isna(row['24备注（答案解释）']) else None,
                    'rule_id': self.rule_id,
                    'batch_no': self.import_time
                }
                logger.info(f"结论参数: {conclusion_params}")
                
                logger.info("创建结论对象...")
                conclusion = Conclusion(**conclusion_params)
                
                logger.info("结论对象创建成功，准备添加到数据库...")
                db.session.add(conclusion)
                
                logger.info("执行数据库flush...")
                db.session.flush()
                
                logger.info(f"结论记录创建成功，ID: {conclusion.id}")
                
                success_count += 1
                logger.info(f"{self.import_time} - 第{index+1}行结论数据处理成功")
                
            except Exception as e:
                error_count += 1
                logger.error(f"{self.import_time} - 导入第{index+1}行结论数据失败:")
                logger.error(f"错误信息: {str(e)}")
                logger.error(f"行数据: {row.to_dict()}")
                logger.error("详细错误堆栈:", exc_info=True)
                continue
        
        try:
            db.session.commit()
            logger.info(f"{self.import_time} - 结论数据导入完成. 成功: {success_count}, 失败: {error_count}")
        except Exception as e:
            logger.error(f"{self.import_time} - 最终提交失败: {str(e)}", exc_info=True)
            db.session.rollback()
            raise
        
        return success_count, error_count
        
    def import_rule_data(self, disease_df, question_df, conclusion_df):
        """导入规则数据"""
        # 初始化计数器
        disease_success = disease_error = 0
        question_success = question_error = 0
        conclusion_success = conclusion_error = 0
        
        try:
            # 打印所有sheet页的基本信息
            logger.info(f"{self.import_time} - 疾病sheet页信息:")
            logger.info(f"形状: {disease_df.shape}")
            logger.info(f"列名: {list(disease_df.columns)}")
            
            logger.info(f"{self.import_time} - 问题sheet页信息:")
            logger.info(f"形状: {question_df.shape}")
            logger.info(f"列名: {list(question_df.columns)}")
            
            logger.info(f"{self.import_time} - 结论sheet页信息:")
            logger.info(f"形状: {conclusion_df.shape}")
            logger.info(f"列名: {list(conclusion_df.columns)}")
            
            # 导入疾病数据
            disease_success, disease_error = self.import_diseases(disease_df)
            if disease_success == 0:
                raise ValueError("疾病数据导入失败：没有成功导入任何数据")
            
            # 导入问题数据
            question_success, question_error = self.import_questions(question_df)
            if question_success == 0:
                raise ValueError("问题数据导入失败：没有成功导入任何数据")
            
            # 导入结论数据
            conclusion_success, conclusion_error = self.import_conclusions(conclusion_df)
            if conclusion_success == 0:
                raise ValueError("结论数据导入失败：没有成功导入任何数据")
            
            # 只有当所有数据都有成功导入时才返回True
            return True, (
                f"导入完成！\n"
                f"疾病数据：成功{disease_success}条，失败{disease_error}条\n"
                f"问题数据：成功{question_success}条，失败{question_error}条\n"
                f"结论数据：成功{conclusion_success}条，失败{conclusion_error}条"
            )
            
        except Exception as e:
            # 发生异常时回滚所有更改
            db.session.rollback()
            error_msg = (
                f"导入失败：{str(e)}\n"
                f"疾病数据：成功{disease_success}条，失败{disease_error}条\n"
                f"问题数据：成功{question_success}条，失败{question_error}条\n"
                f"结论数据：成功{conclusion_success}条，失败{conclusion_error}条"
            )
            return False, error_msg 