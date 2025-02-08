from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel

class Question(BaseModel):
    """问题模型"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), comment='问题编码')
    content = db.Column(db.Text, comment='问题内容')
    attribute = db.Column(db.String(20), default='P', comment='问题属性:P-普通,G-归类')
    question_type = db.Column(db.String(20), comment='问题类型(1单选/0多选/2录入)')
    remark = db.Column(db.Text, comment='问题解释')
    rule_id = db.Column(db.Integer, db.ForeignKey('underwriting_rules.id'), comment='规则ID')
    type_id = db.Column(db.Integer, db.ForeignKey('question_types.id'), comment='问题类型ID')
    batch_no = db.Column(db.String(50), comment='导入批次号')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联
    rule = db.relationship('UnderwritingRule', backref='questions')
    question_type_rel = db.relationship('QuestionType', backref='questions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'content': self.content,
            'attribute': self.attribute,
            'question_type': self.question_type,
            'remark': self.remark,
            'rule_id': self.rule_id,
            'type_id': self.type_id,
            'batch_no': self.batch_no,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }