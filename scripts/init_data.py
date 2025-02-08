from app import create_app, db
from app.models import (
    User, Channel, Product, AIParameter, UnderwritingRule, RiskPool,
    InsuranceCompany, ProductType, Tenant, Disease, Question, Conclusion, 
    DiseaseCategory, QuestionType, ConclusionType, RuleVersion
)
from app.models.base.enums import StatusEnum
from datetime import datetime

def init_all():
    """初始化所有数据"""
    app = create_app()
    with app.app_context():
        # 初始化基础数据
        init_base_data()
        # 初始化认证数据
        init_auth_data()
        print('开始初始化数据...')
        
        # 初始化产品类型
        product_type = ProductType.query.filter_by(code='PERSONAL_LIFE').first()
        if not product_type:
            product_type = ProductType(
                name='个人寿险',
                code='PERSONAL_LIFE',
                description='个人寿险产品'
            )
            db.session.add(product_type)
            db.session.commit()

        # 初始化保险公司
        insurance_company = InsuranceCompany.query.filter_by(code='EXAMPLE_INS').first()
        if not insurance_company:
            insurance_company = InsuranceCompany(
                name='示例保险公司',
                code='EXAMPLE_INS',
                description='示例保险公司描述'
            )
            db.session.add(insurance_company)
            db.session.commit()

        # 初始化风险池
        risk_pool = RiskPool.query.filter_by(code='STANDARD_POOL').first()
        if not risk_pool:
            risk_pool = RiskPool(
                name='标准风险池',
                code='STANDARD_POOL',
                description='标准风险池描述'
            )
            db.session.add(risk_pool)
            db.session.commit()

        # 初始化渠道
        channel = Channel.query.filter_by(code='OFFICIAL').first()
        if not channel:
            channel = Channel(
                name='官方渠道',
                code='OFFICIAL',
                description='官方销售渠道'
            )
            db.session.add(channel)
            db.session.commit()

        # 初始化产品
        product = Product.query.filter_by(product_code='EXAMPLE_PROD').first()
        if not product:
            product = Product(
                name='示例产品',
                product_code='EXAMPLE_PROD',
                product_type_id=product_type.id,
                insurance_company_id=insurance_company.id,
                channel_id=channel.id,
                status='enabled'
            )
            db.session.add(product)
            db.session.commit()

        # 初始化问题类型
        question_type = QuestionType.query.filter_by(code='YES_NO').first()
        if not question_type:
            question_type = QuestionType(
                name='是否选择题',
                code='YES_NO',
                input_type='radio',
                options={'yes': '是', 'no': '否'},
                validation_rules={'required': True},
                description='是/否选择题'
            )
            db.session.add(question_type)
            db.session.commit()

        # 初始化疾病类别
        disease_category = DiseaseCategory.query.filter_by(code='CARDIOVASCULAR').first()
        if not disease_category:
            disease_category = DiseaseCategory(
                name='心血管系统疾病',
                code='CARDIOVASCULAR',
                level=1,
                sort_order=1,
                description='心血管系统疾病'
            )
            db.session.add(disease_category)
            db.session.commit()

        # 初始化结论类型
        conclusion_type = ConclusionType.query.filter_by(code='STANDARD_ACCEPT').first()
        if not conclusion_type:
            conclusion_type = ConclusionType(
                name='标准承保结论',
                code='STANDARD_ACCEPT',
                input_type='text',
                description='标准承保结论'
            )
            db.session.add(conclusion_type)
            db.session.commit()

        # 初始化规则版本
        rule_version = RuleVersion.query.filter_by(code='BASIC_RULES_V1').first()
        if not rule_version:
            rule_version = RuleVersion(
                name='基础规则集',
                code='BASIC_RULES_V1',
                version='1.0.0',
                description='基础核保规则集第一版'
            )
            db.session.add(rule_version)
            db.session.commit()

        # 初始化核保规则
        underwriting_rule = UnderwritingRule.query.filter_by(name='基础核保规则').first()
        if not underwriting_rule:
            underwriting_rule = UnderwritingRule(
                name='基础核保规则',
                version='1.0.0',
                description='基础核保规则描述',
                status=StatusEnum.ENABLED.value
            )
            db.session.add(underwriting_rule)
            db.session.commit()

        # 初始化问题
        question = Question.query.filter_by(code='Q_HYPERTENSION').first()
        if not question:
            question = Question(
                content='询问是否有高血压病史及治疗情况',
                code='Q_HYPERTENSION',
                attribute='P',
                question_type='1',
                remark='用于评估高血压相关风险',
                rule_id=underwriting_rule.id
            )
            db.session.add(question)
            db.session.commit()

        # 最终提交
        db.session.commit()
        print('数据初始化完成')

def init_auth_data():
    """初始化认证相关数据"""
    # 创建默认租户
    tenant = Tenant.query.filter_by(code='default').first()
    if not tenant:
        tenant = Tenant(
            name='默认租户',
            code='default',
            status='enabled'
        )
        db.session.add(tenant)
        db.session.commit()
        print('已创建默认租户')

    # 创建管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            is_admin=True,
            tenant_id=tenant.id,
            status='enabled'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('已创建管理员用户(admin/admin123)')

def init_base_data():
    """初始化基础数据"""
    # ... 保持原有的初始化代码不变 ...

if __name__ == '__main__':
    init_all()