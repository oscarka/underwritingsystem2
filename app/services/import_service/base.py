import os
import uuid
import pandas as pd
import logging
from datetime import datetime
from app.extensions import db
from app.models.rules.import.import_record import ImportRecord
from app.models.rules.import.import_detail import ImportDetail

logger = logging.getLogger(__name__)

class BaseImportService:
    """导入服务基类"""
    
    def __init__(self, current_user=None):
        self.batch_no = self.generate_batch_no()
        logger.info(f"创建导入服务实例，批次号：{self.batch_no}")
        self.import_record = None
        self.current_user = current_user
        self.required_sheets = []  # 子类需要定义必需的sheet
        self.sheet_headers = {}    # 子类需要定义每个sheet的必需表头
    
    @staticmethod
    def generate_batch_no():
        """生成批次号"""
        return f"IMP{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
    
    def create_import_record(self, file_name, import_type):
        """创建导入记录"""
        logger.info(f"创建导入记录：文件名={file_name}, 类型={import_type}")
        self.import_record = ImportRecord(
            batch_no=self.batch_no,
            import_type=import_type,
            file_name=file_name,
            status='pending',
            created_by=self.current_user.id if self.current_user else None
        )
        db.session.add(self.import_record)
        db.session.flush()
        return self.import_record
    
    def add_import_detail(self, sheet_name, row_number, data_type, status='success', 
                         error_message=None, reference_id=None, raw_data=None):
        """添加导入详情"""
        if status == 'error':
            logger.error(f"导入错误：sheet={sheet_name}, 行号={row_number}, 错误={error_message}")
        else:
            logger.info(f"导入成功：sheet={sheet_name}, 行号={row_number}, 类型={data_type}")
            
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
        db.session.add(detail)
        return detail
    
    def validate_file(self, file_path):
        """验证文件"""
        logger.info(f"开始验证文件：{file_path}")
        if not os.path.exists(file_path):
            logger.error(f"文件不存在：{file_path}")
            raise ValueError('文件不存在')
        
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.xlsx', '.xls']:
            logger.error(f"不支持的文件格式：{ext}")
            raise ValueError('不支持的文件格式，请使用Excel文件')
            
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
        if sheet_name not in self.sheet_headers:
            return
            
        logger.info(f"开始验证表头：sheet={sheet_name}")
        logger.info(f"当前表头：{', '.join(df.columns)}")
        logger.info(f"必需表头：{', '.join(self.sheet_headers[sheet_name])}")
            
        required_headers = self.sheet_headers[sheet_name]
        missing_headers = set(required_headers) - set(df.columns)
        if missing_headers:
            logger.error(f"表头验证失败，缺少：{', '.join(missing_headers)}")
            raise ValueError(f'Sheet {sheet_name} 缺少必需的表头：{", ".join(missing_headers)}')
            
        logger.info(f"表头验证通过：sheet={sheet_name}")
    
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
        """读取sheet数据"""
        logger.info(f"开始读取sheet：{sheet_name}")
        try:
            df = pd.read_excel(workbook, sheet_name)
            self.validate_headers(df, sheet_name)
            logger.info(f"Sheet读取成功，共{len(df)}行数据")
            return df
        except Exception as e:
            logger.error(f"读取sheet {sheet_name} 失败：{str(e)}")
            raise ValueError(f'读取sheet {sheet_name} 失败：{str(e)}')
    
    def process(self, file_path, import_type):
        """处理导入"""
        logger.info(f"开始处理导入：文件={file_path}, 类型={import_type}")
        try:
            # 验证文件
            self.validate_file(file_path)
            
            # 创建导入记录
            self.create_import_record(os.path.basename(file_path), import_type)
            self.import_record.status = 'processing'
            db.session.flush()
            
            # 读取Excel文件
            workbook = self.read_excel(file_path)
            
            # 验证sheet
            self.validate_sheets(workbook)
            
            # 开始事务
            logger.info("开始导入数据事务")
            with db.session.begin_nested():
                # 处理数据
                self.process_data(workbook)
                
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
    
    def process_data(self, workbook):
        """处理数据（子类必须实现）"""
        raise NotImplementedError 