from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel

class ImportRecord(BaseModel):
    """导入记录模型"""
    __tablename__ = 'rule_import_records'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_no = db.Column(db.String(50), unique=True, comment='导入批次号')
    import_type = db.Column(db.String(20), comment='导入类型：underwriting/disease等')
    file_name = db.Column(db.String(200), comment='原始文件名')
    status = db.Column(db.String(20), comment='导入状态：pending/processing/completed/failed')
    total_count = db.Column(db.Integer, default=0, comment='总记录数')
    success_count = db.Column(db.Integer, default=0, comment='成功数')
    error_count = db.Column(db.Integer, default=0, comment='失败数')
    error_details = db.Column(db.Text, comment='错误详情')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关联导入详情
    details = db.relationship('ImportDetail', backref='import_record', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_no': self.batch_no,
            'import_type': self.import_type,
            'file_name': self.file_name,
            'status': self.status,
            'total_count': self.total_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'error_details': self.error_details,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        } 