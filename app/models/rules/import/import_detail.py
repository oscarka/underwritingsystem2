from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel

class ImportDetail(BaseModel):
    """导入详情模型"""
    __tablename__ = 'rule_import_details'
    
    id = db.Column(db.Integer, primary_key=True)
    import_id = db.Column(db.Integer, db.ForeignKey('rule_import_records.id'), comment='导入记录ID')
    sheet_name = db.Column(db.String(50), comment='Sheet名称')
    row_number = db.Column(db.Integer, comment='行号')
    status = db.Column(db.String(20), comment='状态：success/error')
    error_message = db.Column(db.Text, comment='错误信息')
    data_type = db.Column(db.String(20), comment='数据类型：disease/question/answer')
    reference_id = db.Column(db.Integer, comment='关联ID（disease_id/question_id等）')
    raw_data = db.Column(db.JSON, comment='原始数据')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'import_id': self.import_id,
            'sheet_name': self.sheet_name,
            'row_number': self.row_number,
            'status': self.status,
            'error_message': self.error_message,
            'data_type': self.data_type,
            'reference_id': self.reference_id,
            'raw_data': self.raw_data,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        } 