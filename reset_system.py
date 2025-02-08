import os
import sys
from datetime import datetime

from app import create_app, db
from app.models import (
    User, Tenant, Channel, Product, AIParameter, UnderwritingRule,
    InsuranceCompany, ProductType, Disease, Question, Conclusion, RiskPool, AIParameterType,
    DiseaseCategory
)
from app.models.base.enums import StatusEnum

def reset_database():
    """重置数据库"""
    # 删除现有数据库文件
    if os.path.exists('instance/app.db'):
        os.remove('instance/app.db')
        print('删除现有数据库文件')

    # 创建应用上下文
    app = create_app()
    with app.app_context():
        # 删除所有表并重新创建
        print('删除所有表')
        db.drop_all()
        print('重新创建所有表')
        db.create_all()

        print('\n=== 开始创建初始数据 ===\n')

        # 创建默认租户
        tenant = Tenant(
            name='默认租户',
            code='default_demo',
            status=StatusEnum.ENABLED.value
        )
        db.session.add(tenant)
        db.session.commit()
        print('✓ 创建默认租户:', tenant.name)

        # 创建管理员用户
        admin = User(
            username='admin',
            tenant_id=tenant.id,
            status=StatusEnum.ENABLED.value,
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print('✓ 创建管理员用户:', admin.username)

        # 创建产品类型
        product_types = [
            ProductType(
                name='寿险产品',
                code='LIFE_INSURANCE',
                description='传统寿险产品类型',
                status=StatusEnum.ENABLED.value
            ),
            ProductType(
                name='重疾险产品',
                code='CRITICAL_ILLNESS',
                description='重大疾病保险产品类型',
                status=StatusEnum.ENABLED.value
            ),
            ProductType(
                name='医疗险产品',
                code='MEDICAL_INSURANCE',
                description='医疗保险产品类型',
                status=StatusEnum.ENABLED.value
            )
        ]
        for pt in product_types:
            db.session.add(pt)
        print('✓ 创建产品类型:')
        for pt in product_types:
            print(f'  - {pt.name} (代码: {pt.code})')

        # 创建保险公司
        insurance_companies = [
            InsuranceCompany(
                name='平安保险',
                code='PING_AN',
                description='中国平安保险公司',
                status=StatusEnum.ENABLED.value
            ),
            InsuranceCompany(
                name='太平洋保险',
                code='CPIC',
                description='中国太平洋保险公司',
                status=StatusEnum.ENABLED.value
            ),
            InsuranceCompany(
                name='人寿保险',
                code='LIFE',
                description='中国人寿保险公司',
                status=StatusEnum.ENABLED.value
            )
        ]
        for ic in insurance_companies:
            db.session.add(ic)
        print('✓ 创建保险公司:')
        for ic in insurance_companies:
            print(f'  - {ic.name} (代码: {ic.code})')

        # 创建渠道
        channel = Channel(
            name='示例渠道',
            code='DEMO_CH',
            description='这是一个示例渠道'
        )
        channel.status = StatusEnum.ENABLED.value
        db.session.add(channel)
        print('✓ 创建渠道:', channel.name)

        # 创建多个AI参数类型
        parameter_types = [
            AIParameterType(
                name='传统核保',
                code='TRADITIONAL',
                description='传统人工核保参数配置',
                value_type='json',
                status=StatusEnum.ENABLED.value
            ),
            AIParameterType(
                name='智能核保',
                code='AI',
                description='智能自动核保参数配置',
                value_type='json',
                status=StatusEnum.ENABLED.value
            )
        ]
        for pt in parameter_types:
            db.session.add(pt)
        db.session.commit()
        print('\n✓ 创建AI参数类型:')
        for pt in parameter_types:
            print(f'  - {pt.name} (代码: {pt.code})')

        # 创建默认规则
        rules = [
            UnderwritingRule(
                name='标准核保规则',
                version='1.0',
                status=StatusEnum.ENABLED.value,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            UnderwritingRule(
                name='特殊职业核保规则',
                version='1.0',
                status=StatusEnum.ENABLED.value,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        for rule in rules:
            db.session.add(rule)
        db.session.commit()
        print('\n✓ 创建核保规则:')
        for rule in rules:
            print(f'  - {rule.name} (版本: {rule.version})')

        # 创建疾病大类
        disease_categories = [
            DiseaseCategory(
                name='心血管系统疾病',
                code='CARDIOVASCULAR',
                level=1,
                sort_order=1,
                description='包括高血压、冠心病等心血管系统相关疾病',
                status=StatusEnum.ENABLED.value,
                rule_id=rules[0].id
            ),
            DiseaseCategory(
                name='呼吸系统疾病',
                code='RESPIRATORY',
                level=1,
                sort_order=2,
                description='包括哮喘、支气管炎等呼吸系统相关疾病',
                status=StatusEnum.ENABLED.value,
                rule_id=rules[0].id
            ),
            DiseaseCategory(
                name='内分泌系统疾病',
                code='ENDOCRINE',
                level=1,
                sort_order=3,
                description='包括糖尿病、甲状腺疾病等内分泌系统相关疾病',
                status=StatusEnum.ENABLED.value,
                rule_id=rules[0].id
            )
        ]
        for category in disease_categories:
            db.session.add(category)
        db.session.commit()
        print('\n✓ 创建疾病大类:')
        for category in disease_categories:
            print(f'  - {category.name} (代码: {category.code})')

        # 创建疾病
        diseases = [
            Disease(
                name='高血压',
                code='HYPERTENSION',
                category_code=disease_categories[0].code,
                category_name=disease_categories[0].name,
                category_id=disease_categories[0].id,
                rule_id=rules[0].id,
                first_question_code='Q_HBP_1',
                risk_level='medium',
                description='高血压是一种常见的心血管疾病',
                is_common=True
            ),
            Disease(
                name='糖尿病',
                code='DIABETES',
                category_code=disease_categories[2].code,
                category_name=disease_categories[2].name,
                category_id=disease_categories[2].id,
                rule_id=rules[0].id,
                first_question_code='Q_DB_1',
                risk_level='high',
                description='糖尿病是一种常见的内分泌系统疾病',
                is_common=True
            )
        ]
        for disease in diseases:
            db.session.add(disease)
        db.session.commit()
        print('\n✓ 创建疾病:')
        for disease in diseases:
            print(f'  - {disease.name} (代码: {disease.code})')

        # 创建问题
        questions = [
            Question(
                code='Q_HBP_1',
                content='您的血压控制情况如何？',
                question_type='1',
                attribute='P',
                rule_id=rules[0].id,
                remark='了解患者血压控制情况'
            ),
            Question(
                code='Q_DB_1',
                content='您的血糖控制情况如何？',
                question_type='1',
                attribute='P',
                rule_id=rules[0].id,
                remark='了解患者血糖控制情况'
            )
        ]
        for question in questions:
            db.session.add(question)
        db.session.commit()
        print('\n✓ 创建问题:')
        for question in questions:
            print(f'  - {question.content} (代码: {question.code})')

        # 创建AI参数
        ai_parameters = [
            AIParameter(
                name='标准寿险核保配置',
                parameter_type_id=parameter_types[0].id,  # 传统核保
                rule_id=rules[0].id,
                value='''{
                    "age_limit": {"min": 18, "max": 65},
                    "occupation_categories": ["1", "2", "3", "4"],
                    "bmi_range": {"min": 16, "max": 32}
                }''',
                description='标准寿险产品核保参数配置',
                status=StatusEnum.ENABLED.value
            ),
            AIParameter(
                name='重疾险智能核保配置',
                parameter_type_id=parameter_types[1].id,  # 智能核保
                rule_id=rules[1].id,
                value='''{
                    "risk_factors": ["health", "occupation", "age"],
                    "ai_model": "critical_illness_v1",
                    "confidence_threshold": 0.9,
                    "manual_review_threshold": 0.7
                }''',
                description='重疾险产品智能核保参数配置',
                status=StatusEnum.ENABLED.value
            ),
            AIParameter(
                name='医疗险智能核保配置',
                parameter_type_id=parameter_types[1].id,  # 智能核保
                rule_id=rules[1].id,
                value='''{
                    "risk_factors": ["medical_history", "age", "occupation"],
                    "ai_model": "medical_insurance_v1",
                    "confidence_threshold": 0.85,
                    "manual_review_threshold": 0.65
                }''',
                description='医疗险产品智能核保参数配置',
                status=StatusEnum.ENABLED.value
            )
        ]
        for param in ai_parameters:
            db.session.add(param)
        db.session.commit()
        print('\n✓ 创建AI参数:')
        for param in ai_parameters:
            print(f'  - {param.name}')
            print(f'    类型: {param.parameter_type.name}')
            print(f'    规则: {param.rule.name}')
            print(f'    值: {param.value}')

        # 创建示例产品
        products = [
            Product(
                name='传统寿险产品',
                product_code='LIFE_BASIC',
                description='基础寿险保障产品',
                product_type_id=product_types[0].id,  # 寿险产品
                insurance_company_id=insurance_companies[0].id,  # 平安保险
                channel_id=channel.id,
                ai_parameter_id=ai_parameters[0].id,  # 标准寿险核保配置
                status=StatusEnum.ENABLED.value
            ),
            Product(
                name='智能重疾险',
                product_code='CI_SMART',
                description='智能核保重疾险产品',
                product_type_id=product_types[1].id,  # 重疾险产品
                insurance_company_id=insurance_companies[1].id,  # 太平洋保险
                channel_id=channel.id,
                ai_parameter_id=ai_parameters[1].id,  # 重疾险智能核保配置
                status=StatusEnum.ENABLED.value
            ),
            Product(
                name='智能医疗险',
                product_code='MEDICAL_SMART',
                description='智能核保医疗险产品',
                product_type_id=product_types[2].id,  # 医疗险产品
                insurance_company_id=insurance_companies[2].id,  # 人寿保险
                channel_id=channel.id,
                ai_parameter_id=ai_parameters[2].id,  # 医疗险智能核保配置
                status=StatusEnum.ENABLED.value
            )
        ]
        for product in products:
            product.status = StatusEnum.ENABLED.value
            db.session.add(product)
        print('\n✓ 创建示例产品:')
        for product in products:
            print(f'  - {product.name}')
            print(f'    产品代码: {product.product_code}')
            print(f'    产品类型: {product_types[0].name if product.product_type_id == product_types[0].id else product_types[1].name if product.product_type_id == product_types[1].id else product_types[2].name}')
            print(f'    保险公司: {insurance_companies[0].name if product.insurance_company_id == insurance_companies[0].id else insurance_companies[1].name if product.insurance_company_id == insurance_companies[1].id else insurance_companies[2].name}')
            print(f'    渠道: {channel.name}')
            print(f'    关联参数: {ai_parameters[0].name if product.ai_parameter_id == ai_parameters[0].id else ai_parameters[1].name if product.ai_parameter_id == ai_parameters[1].id else ai_parameters[2].name}')

        # 提交所有更改
        db.session.commit()
        print('\n=== 数据初始化完成 ===\n')

        # 打印关联关系
        print('\n=== 数据关联关系 ===\n')
        print('1. AI参数类型 -> AI参数:')
        for pt in parameter_types:
            print(f'\n类型: {pt.name} ({pt.code})')
            params = AIParameter.query.filter_by(parameter_type_id=pt.id).all()
            if params:
                print('关联的参数:')
                for p in params:
                    print(f'  - {p.name} (规则: {p.rule.name})')
            else:
                print('  没有关联的参数')

        print('\n2. 核保规则 -> AI参数:')
        for rule in rules:
            print(f'\n规则: {rule.name}')
            params = AIParameter.query.filter_by(rule_id=rule.id).all()
            if params:
                print('关联的参数:')
                for p in params:
                    print(f'  - {p.name} (类型: {p.parameter_type.name})')
            else:
                print('  没有关联的参数')

        print('\n3. 疾病大类 -> 疾病:')
        for category in disease_categories:
            print(f'\n疾病大类: {category.name}')
            diseases = Disease.query.filter_by(category_id=category.id).all()
            if diseases:
                print('关联的疾病:')
                for d in diseases:
                    print(f'  - {d.name} (代码: {d.code})')
            else:
                print('  没有关联的疾病')

        print('\n4. 疾病 -> 问题:')
        for disease in Disease.query.all():
            print(f'\n疾病: {disease.name}')
            if disease.first_question_code:
                question = Question.query.filter_by(code=disease.first_question_code).first()
                if question:
                    print(f'首个问题: {question.content}')
                else:
                    print('未找到关联的首个问题')
            else:
                print('没有设置首个问题')

if __name__ == '__main__':
    try:
        reset_database()
    except Exception as e:
        print(f'初始化失败: {str(e)}')
        sys.exit(1) 