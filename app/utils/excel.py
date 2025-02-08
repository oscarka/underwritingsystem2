import pandas as pd
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from utils.logger import get_logger

@dataclass
class ExcelSheet:
    name: str
    required_columns: List[str]
    
class ExcelTemplate:
    def __init__(self, sheets: List[ExcelSheet]):
        self.sheets = sheets
        
    def validate_structure(self, excel_file) -> Tuple[bool, List[str]]:
        """验证Excel文件结构"""
        errors = []
        try:
            df_dict = pd.read_excel(excel_file, sheet_name=None)
            
            # 验证sheet页
            for sheet in self.sheets:
                if sheet.name not in df_dict:
                    errors.append(f"缺少必需的sheet页: {sheet.name}")
                    continue
                    
                df = df_dict[sheet.name]
                missing_columns = [col for col in sheet.required_columns if col not in df.columns]
                if missing_columns:
                    errors.append(f"sheet页 {sheet.name} 缺少必需的列: {', '.join(missing_columns)}")
                    
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Excel文件验证失败: {str(e)}")
            return False, errors
            
    def read_data(self, excel_file) -> Dict[str, pd.DataFrame]:
        """读取Excel数据"""
        return pd.read_excel(excel_file, sheet_name=[sheet.name for sheet in self.sheets])

class RuleExcelTemplate(ExcelTemplate):
    """核保规则Excel模板"""
    def __init__(self):
        self.logger = get_logger(__name__)
        super().__init__([
            ExcelSheet(
                name="疾病配置",
                required_columns=[
                    "疾病类别代码",
                    "疾病类别",
                    "疾病代码",
                    "疾病",
                    "疾病第一个问题编码",
                    "备注（疾病解释）",
                    "是否为常见疾病0：否，1：是"
                ]
            ),
            ExcelSheet(
                name="问题配置",
                required_columns=[
                    "问题编码",
                    "问题内容",
                    "问题属性 P:普通问题 G:归类问题",
                    "问题类型 1-单选 0-多选 2-录入问题",
                    "备注（问题解释）"
                ]
            ),
            ExcelSheet(
                name="答案配置",
                required_columns=[
                    "问题编码",
                    "答案选项内容",
                    "10重疾结论",
                    "11重疾特殊编码",
                    "12重疾特殊描述",
                    "15医疗险结论",
                    "16医疗特殊编码",
                    "17医疗特殊描述",
                    "19对应下一个问题编码",
                    "23答案展示顺序",
                    "24备注（答案解释）"
                ]
            )
        ])
        
    def validate_structure(self, excel_file) -> Tuple[bool, List[str]]:
        """验证Excel文件结构"""
        self.logger.info("开始验证Excel文件结构")
        errors = []
        try:
            df_dict = pd.read_excel(excel_file, sheet_name=None)
            self.logger.info(f"Excel文件包含以下sheet页: {list(df_dict.keys())}")
            
            # 验证sheet页
            for sheet in self.sheets:
                if sheet.name not in df_dict:
                    error_msg = f"缺少必需的sheet页: {sheet.name}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    continue
                    
                df = df_dict[sheet.name]
                self.logger.info(f"正在验证{sheet.name}页:")
                self.logger.info(f"- 总行数: {len(df)}")
                self.logger.info(f"- 总列数: {len(df.columns)}")
                self.logger.info(f"- 实际列名: {', '.join(df.columns.tolist())}")
                self.logger.info(f"- 要求列名: {', '.join(sheet.required_columns)}")
                
                missing_columns = [col for col in sheet.required_columns if col not in df.columns]
                if missing_columns:
                    error_msg = f"sheet页 {sheet.name} 缺少必需的列: {', '.join(missing_columns)}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    
            if not errors:
                self.logger.info("Excel文件结构验证通过")
            return len(errors) == 0, errors
            
        except Exception as e:
            error_msg = f"Excel文件验证失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            return False, errors
            
    def read_data(self, excel_file) -> Dict[str, pd.DataFrame]:
        """读取Excel数据"""
        self.logger.info("开始读取Excel数据")
        try:
            data = pd.read_excel(excel_file, sheet_name=[sheet.name for sheet in self.sheets])
            
            # 记录每个sheet的数据概况
            for sheet_name, df in data.items():
                self.logger.info(f"\n{sheet_name}页数据概况:")
                self.logger.info(f"- 数据行数: {len(df)}")
                self.logger.info(f"- 数据列数: {len(df.columns)}")
                self.logger.info(f"- 列名: {', '.join(df.columns.tolist())}")
                
                # 跳过前两行(表头和规则说明)，记录实际数据
                if len(df) > 2:
                    df_data = df.iloc[2:]
                    self.logger.info(f"- 实际数据行数: {len(df_data)}")
                    self.logger.info("- 数据预览:")
                    for idx, row in df_data.head().iterrows():
                        self.logger.info(f"  第{idx+1}行: {dict(row)}")
                        
            self.logger.info("Excel数据读取完成")
            return data
            
        except Exception as e:
            self.logger.error(f"读取Excel数据失败: {str(e)}", exc_info=True)
            raise
            
    def process_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
        """处理Excel数据为业务对象"""
        self.logger.info("开始处理Excel数据")
        result = {}
        
        try:
            # 处理疾病数据
            if "疾病配置" in data:
                self.logger.info("处理疾病配置数据:")
                diseases_df = data["疾病配置"].iloc[2:]  # 跳过前两行
                result["diseases"] = diseases_df.to_dict("records")
                self.logger.info(f"- 处理了{len(result['diseases'])}条疾病记录")
                for disease in result["diseases"][:3]:  # 记录前3条数据
                    self.logger.info(f"- 疾病示例: {disease}")
                    
            # 处理问题数据
            if "问题配置" in data:
                self.logger.info("处理问题配置数据:")
                questions_df = data["问题配置"].iloc[2:]
                result["questions"] = questions_df.to_dict("records")
                self.logger.info(f"- 处理了{len(result['questions'])}条问题记录")
                for question in result["questions"][:3]:
                    self.logger.info(f"- 问题示例: {question}")
                    
            # 处理答案数据
            if "答案配置" in data:
                self.logger.info("处理答案配置数据:")
                answers_df = data["答案配置"].iloc[2:]
                result["answers"] = answers_df.to_dict("records")
                self.logger.info(f"- 处理了{len(result['answers'])}条答案记录")
                for answer in result["answers"][:3]:
                    self.logger.info(f"- 答案示例: {answer}")
                    
            # 验证数据关联关系
            self._validate_relationships(result)
                    
            self.logger.info("Excel数据处理完成")
            return result
            
        except Exception as e:
            self.logger.error(f"处理Excel数据失败: {str(e)}", exc_info=True)
            raise
            
    def _validate_relationships(self, data: Dict[str, List[Dict]]):
        """验证数据关联关系"""
        self.logger.info("开始验证数据关联关系")
        
        # 1. 获取所有唯一值
        disease_codes = set()
        question_codes = set()
        disease_question_map = {}
        
        # 收集疾病数据
        for disease in data.get("diseases", []):
            disease_codes.add(disease["疾病代码"])
            if "疾病第一个问题编码" in disease:
                disease_question_map[disease["疾病代码"]] = disease["疾病第一个问题编码"]
                
        # 收集问题数据
        for question in data.get("questions", []):
            question_codes.add(question["问题编码"])
            
        # 2. 验证关联
        self.logger.info("验证疾病-问题关联:")
        for disease_code, question_code in disease_question_map.items():
            if question_code not in question_codes:
                self.logger.warning(f"- 疾病 {disease_code} 关联的问题 {question_code} 不存在")
                
        self.logger.info("验证问题-答案关联:")
        for answer in data.get("answers", []):
            if answer["问题编码"] not in question_codes:
                self.logger.warning(f"- 答案关联的问题 {answer['问题编码']} 不存在")
                
        self.logger.info("数据关联关系验证完成") 