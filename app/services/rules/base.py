from datetime import datetime
import logging
from app.extensions import db
from app.services.base import ImportServiceBase
from app.models.rules.import_record import ImportRecord

logger = logging.getLogger(__name__)

class RuleImportBase(ImportServiceBase):
    """规则导入基础服务类"""
    
    def __init__(self):
        self.batch_no = self.generate_batch_no()
        self.success_count = 0
        self.error_count = 0
        self.error_messages = []
    
    def generate_batch_no(self):
        """生成批次号"""
        return f"BATCH_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def create_import_record(self, rule_id, file_name):
        """创建导入记录"""
        return super().create_import_record(rule_id, file_name, ImportRecord)
    
    def update_import_record(self, record):
        """更新导入记录"""
        record.success_count = self.success_count
        record.error_count = self.error_count
        record.total_count = self.success_count + self.error_count
        record.error_message = '\n'.join(self.error_messages) if self.error_messages else None
        db.session.commit()
    
    def add_error(self, message):
        """添加错误信息"""
        self.error_count += 1
        self.error_messages.append(message)
        logger.error(f"导入错误: {message}")
    
    def add_success(self):
        """添加成功计数"""
        self.success_count += 1
    
    def get_import_result(self):
        """获取导入结果"""
        return {
            'success': len(self.error_messages) == 0,
            'total': self.success_count + self.error_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'error_messages': self.error_messages
        } 