from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel

class AnswerOption(BaseModel):
    """答案选项模型"""
    __tablename__ = 'answer_options'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), comment='问题ID')
    content = db.Column(db.Text, comment='答案内容')
    medical_conclusion = db.Column(db.String(50), comment='医疗险结论')
    medical_special_code = db.Column(db.String(50), comment='医疗特殊编码')
    batch_no = db.Column(db.String(50), comment='导入批次号')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'content': self.content,
            'medical_conclusion': self.medical_conclusion,
            'medical_special_code': self.medical_special_code,
            'batch_no': self.batch_no,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        } 