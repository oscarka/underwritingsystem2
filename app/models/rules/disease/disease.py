from app import db
from datetime import datetime
from app.models.base.model import BaseModel
from sqlalchemy.orm import relationship
from app.utils.logging import get_logger

class Disease(BaseModel):
    __tablename__ = 'diseases'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)  # 疾病编码
    name = db.Column(db.String(100), nullable=False)  # 疾病名称
    category_code = db.Column(db.String(50))  # 疾病大类编码
    category_name = db.Column(db.String(100))  # 疾病大类名称
    category_id = db.Column(db.Integer, db.ForeignKey('disease_categories.id'), nullable=True)  # 所属分类ID
    rule_id = db.Column(db.Integer, db.ForeignKey('underwriting_rules.id'), nullable=True)  # 所属规则ID
    first_question_code = db.Column(db.String(50))  # 首个问题编码
    risk_level = db.Column(db.String(20))  # 风险等级
    description = db.Column(db.Text)  # 描述
    is_common = db.Column(db.Boolean, default=False)  # 是否为常见疾病
    sort_order = db.Column(db.Integer)  # 排序
    status = db.Column(db.String(20), nullable=False, default='active')  # 状态
    batch_no = db.Column(db.String(50))  # 导入批次号
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship('DiseaseCategory', backref='diseases')
    # questions = relationship('Question', backref='disease', cascade='all, delete-orphan')
    
    def __init__(self, code, name, category_code=None, category_name=None, category_id=None, 
                 first_question_code=None, risk_level='medium', description=None, 
                 is_common=False, sort_order=0, batch_no=None, rule_id=None):
        self.code = code
        self.name = name
        self.category_code = category_code
        self.category_name = category_name
        self.category_id = category_id
        self.rule_id = rule_id
        self.first_question_code = first_question_code
        self.risk_level = risk_level
        self.description = description
        self.is_common = is_common
        self.sort_order = sort_order
        self.batch_no = batch_no
        
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'category_code': self.category_code,
            'category_name': self.category_name,
            'category_id': self.category_id,
            'first_question_code': self.first_question_code,
            'risk_level': self.risk_level,
            'description': self.description,
            'is_common': self.is_common,
            'sort_order': self.sort_order,
            'status': self.status,
            'batch_no': self.batch_no,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def validate_rule_consistency(self):
        """验证rule_id与关联问题的rule_id一致性"""
        if not self.rule_id:
            return True, None
            
        from app.models.rules.question import Question
        question = Question.query.filter_by(code=self.first_question_code).first()
        if not question:
            return False, "关联的问题不存在"
            
        if question.rule_id != self.rule_id:
            return False, "疾病的规则ID与关联问题的规则ID不一致"
            
        return True, None
        
    @classmethod
    def get_by_rule_id(cls, rule_id):
        """通过规则ID获取疾病列表"""
        logger = get_logger(__name__)
        
        logger.info(f"[Disease] 开始通过rule_id={rule_id}查询疾病列表")
        # 直接通过rule_id查询疾病
        diseases = cls.query.filter_by(rule_id=rule_id).all()
        logger.info(f"[Disease] 查询到疾病数量: {len(diseases)}")
        for disease in diseases:
            logger.info(f"[Disease] 疾病信息: id={disease.id}, code={disease.code}, name={disease.name}, category_id={disease.category_id}")
        return diseases
        
    @classmethod
    def get_categories_by_rule_id(cls, rule_id):
        """通过规则ID获取疾病大类列表"""
        from app.models.rules.disease.disease_category import DiseaseCategory
        logger = get_logger(__name__)
        
        logger.info(f"[Disease] 开始通过rule_id={rule_id}查询疾病大类列表")
        
        # 1. 获取规则关联的疾病
        diseases = cls.get_by_rule_id(rule_id)
        if not diseases:
            logger.info("[Disease] 未找到关联疾病，尝试直接从疾病大类表查询")
            # 尝试直接从疾病大类表查询
            categories = DiseaseCategory.query.filter_by(rule_id=rule_id).all()
            if categories:
                logger.info(f"[Disease] 直接从疾病大类表查询到{len(categories)}个类别")
                for category in categories:
                    logger.info(f"[Disease] 疾病大类信息: id={category.id}, code={category.code}, name={category.name}")
                return categories
            logger.info("[Disease] 未找到任何疾病大类")
            return []
            
        # 2. 获取疾病关联的类别ID
        category_ids = list(set(d.category_id for d in diseases if d.category_id))
        logger.info(f"[Disease] 从疾病中提取到的类别ID: {category_ids}")
        
        if not category_ids:
            logger.info("[Disease] 未找到任何有效的类别ID")
            return []
            
        # 3. 获取疾病大类
        categories = DiseaseCategory.query.filter(DiseaseCategory.id.in_(category_ids)).all()
        logger.info(f"[Disease] 查询到疾病大类数量: {len(categories)}")
        for category in categories:
            logger.info(f"[Disease] 疾病大类信息: id={category.id}, code={category.code}, name={category.name}")
        
        return categories 