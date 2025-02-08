from app import db
from decimal import Decimal
from datetime import datetime
from app.models.base.model import BaseModel

class Conclusion(BaseModel):
    """结论模型"""
    __tablename__ = 'conclusions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_code = db.Column(db.String(50))  # 问题编码
    answer_content = db.Column(db.Text)  # 答案内容
    next_question_code = db.Column(db.String(50))  # 下一个问题编码
    medical_conclusion = db.Column(db.Text)  # 医疗险结论
    critical_illness_conclusion = db.Column(db.Text)  # 重疾结论
    medical_special_desc = db.Column(db.Text)  # 医疗特殊描述
    critical_illness_special_desc = db.Column(db.Text)  # 重疾特殊描述
    medical_special_code = db.Column(db.String(50))  # 医疗特殊编码
    critical_illness_special_code = db.Column(db.String(50))  # 重疾特殊编码
    display_order = db.Column(db.Integer, default=0)  # 答案展示顺序
    remark = db.Column(db.Text)  # 备注
    rule_id = db.Column(db.Integer, db.ForeignKey('underwriting_rules.id'))  # 规则ID
    batch_no = db.Column(db.String(50))  # 批次号
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # 更新时间
    
    # 关系
    underwriting_rule = db.relationship('UnderwritingRule', back_populates='conclusions')
    
    def __init__(self, **kwargs):
        """初始化方法"""
        # 调用父类的初始化方法
        super().__init__(**kwargs)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'question_code': self.question_code,
            'answer_content': self.answer_content,
            'next_question_code': self.next_question_code,
            'medical_conclusion': self.medical_conclusion,
            'critical_illness_conclusion': self.critical_illness_conclusion,
            'medical_special_desc': self.medical_special_desc,
            'critical_illness_special_desc': self.critical_illness_special_desc,
            'medical_special_code': self.medical_special_code,
            'critical_illness_special_code': self.critical_illness_special_code,
            'display_order': self.display_order,
            'remark': self.remark,
            'rule_id': self.rule_id,
            'batch_no': self.batch_no,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        } 