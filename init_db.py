from app import create_app, db
from app.models import (
    User, Channel, Product, AIParameter, UnderwritingRule, 
    InsuranceCompany, ProductType, Tenant, Disease, Question, Conclusion, 
    DiseaseCategory, QuestionType, ConclusionType, AIParameterType
)
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        try:
            # 1. 创建基础数据
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
            else:
                print('管理员用户已存在')
            
            # 创建问题类型
            question_types = [
                ('BASIC', '基础问题', 'radio'),
                ('MEDICAL', '医疗问题', 'radio'),
                ('LIFESTYLE', '生活习惯', 'radio'),
                ('FAMILY', '家族病史', 'radio')
            ]
            
            type_map = {}  # 用于存储类型ID的映射
            for code, name, input_type in question_types:
                qt = QuestionType.query.filter_by(code=code).first()
                if not qt:
                    qt = QuestionType(code=code, name=name, input_type=input_type)
                    db.session.add(qt)
                    db.session.commit()
                type_map[code] = qt
            
            # 获取各个类型的引用
            basic_type = type_map['BASIC']
            medical_type = type_map['MEDICAL']
            lifestyle_type = type_map['LIFESTYLE']
            family_type = type_map['FAMILY']

            # 创建渠道
            channels = [
                ('default', '默认渠道'),
                ('online', '线上渠道'),
                ('offline', '线下渠道')
            ]
            for code, name in channels:
                if not Channel.query.filter_by(code=code).first():
                    channel = Channel(name=name, code=code)
                    db.session.add(channel)
            
            # 创建保险公司
            companies = [
                ('default', '默认保险公司'),
                ('pingan', '中国平安'),
                ('cpic', '中国太保')
            ]
            for code, name in companies:
                if not InsuranceCompany.query.filter_by(code=code).first():
                    company = InsuranceCompany(name=name, code=code)
                    db.session.add(company)
            
            # 创建产品类型
            product_types = [
                ('default', '默认类型'),
                ('medical', '医疗险'),
                ('life', '寿险'),
                ('accident', '意外险')
            ]
            for code, name in product_types:
                if not ProductType.query.filter_by(code=code).first():
                    product_type = ProductType(
                        name=name,
                        code=code,
                        description=f'{name}产品类型'
                    )
                    db.session.add(product_type)

            # 提交基础数据获取ID
            db.session.commit()

            # 2. 创建核保规则及相关数据
            rule = UnderwritingRule.query.filter_by(name='默认规则').first()
            if not rule:
                rule = UnderwritingRule(
                    name='默认规则',
                    version='1.0',
                    status='已导入',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(rule)
                db.session.commit()

            # 创建疾病类别
            disease_categories = [
                ('心血管疾病', 'CARDIOVASCULAR'),
                ('呼吸系统疾病', 'RESPIRATORY'),
                ('消化系统疾病', 'DIGESTIVE')
            ]
            
            for name, code in disease_categories:
                category = DiseaseCategory.query.filter_by(code=code).first()
                if not category:
                    category = DiseaseCategory(
                        name=name,
                        code=code
                    )
                    db.session.add(category)
            db.session.commit()

            # 获取疾病类别
            cardio_category = DiseaseCategory.query.filter_by(code='CARDIOVASCULAR').first()
            
            # 创建疾病 - 移除category_code，使用category_id
            if cardio_category:
                diseases = [
                    ('高血压', 'HYPERTENSION'),
                    ('冠心病', 'CHD'),
                    ('心律失常', 'ARRHYTHMIA')
                ]
                
                for name, code in diseases:
                    if not Disease.query.filter_by(code=code).first():
                        disease = Disease(
                            name=name,
                            code=code,
                            category_id=cardio_category.id,  # 使用category_id而不是category_code
                            category_code=cardio_category.code,
                            category_name=cardio_category.name,
                            description=f'{name}的基本描述',
                            is_common=True
                        )
                        db.session.add(disease)

            # 创建示例问题数据
            questions = [
                {
                    'code': 'Q_1',
                    'content': '您是否被诊断或怀疑有高血压？',
                    'attribute': 'P',
                    'question_type': '1',
                    'remark': '了解患者是否有高血压病史',
                    'type_id': basic_type.id
                },
                {
                    'code': 'Q_2',
                    'content': '您的高血压是否在进行规律治疗？',
                    'attribute': 'P',
                    'question_type': '1',
                    'remark': '了解患者的治疗情况',
                    'type_id': medical_type.id
                },
                {
                    'code': 'Q_3',
                    'content': '您的血压是否控制稳定？',
                    'attribute': 'P',
                    'question_type': '1',
                    'remark': '了解患者的血压控制情况',
                    'type_id': medical_type.id
                }
            ]
            
            for q in questions:
                if not Question.query.filter_by(code=q['code']).first():
                    question = Question(
                        code=q['code'],
                        content=q['content'],
                        attribute=q['attribute'],
                        question_type=q['question_type'],
                        remark=q['remark'],
                        rule_id=rule.id,
                        type_id=q['type_id']
                    )
                    db.session.add(question)

            # 创建结论类型
            conclusion_types = [
                {'code': 'STANDARD', 'name': '标准承保', 'input_type': 'radio'},
                {'code': 'SUBSTANDARD', 'name': '次标准承保', 'input_type': 'radio'},
                {'code': 'DECLINE', 'name': '拒保', 'input_type': 'radio'},
                {'code': 'POSTPONE', 'name': '延期', 'input_type': 'radio'},
                {'code': 'EXCLUSION', 'name': '除外责任', 'input_type': 'radio'}
            ]
            
            type_map = {}  # 用于存储结论类型ID的映射
            for ct in conclusion_types:
                conclusion_type = ConclusionType.query.filter_by(code=ct['code']).first()
                if not conclusion_type:
                    conclusion_type = ConclusionType(
                        code=ct['code'], 
                        name=ct['name'],
                        input_type=ct['input_type']
                    )
                    db.session.add(conclusion_type)
                    db.session.commit()
                type_map[ct['code']] = conclusion_type

            # 获取结论类型引用
            standard_type = type_map['STANDARD']
            substandard_type = type_map['SUBSTANDARD']
            decline_type = type_map['DECLINE']
            postpone_type = type_map['POSTPONE']
            exclusion_type = type_map['EXCLUSION']

            # 创建结论
            conclusions = [
                {
                    'code': 'C001',
                    'name': '标准承保',
                    'content': '可以标准费率承保',
                    'decision': 'STANDARD',
                    'em_value': 1.0,
                    'rule_id': rule.id,
                    'type_id': standard_type.id
                },
                {
                    'code': 'C002',
                    'name': '加费承保',
                    'content': '需要加费承保',
                    'decision': 'SUBSTANDARD',
                    'em_value': 1.5,
                    'rule_id': rule.id,
                    'type_id': substandard_type.id
                },
                {
                    'code': 'C003',
                    'name': '拒保',
                    'content': '不符合承保条件',
                    'decision': 'DECLINE',
                    'em_value': 0.0,
                    'rule_id': rule.id,
                    'type_id': decline_type.id
                },
                {
                    'code': 'C004',
                    'name': '延期承保',
                    'content': '建议延期后再次申请',
                    'decision': 'POSTPONE',
                    'em_value': 0.0,
                    'rule_id': rule.id,
                    'type_id': postpone_type.id
                },
                {
                    'code': 'C005',
                    'name': '除外承保',
                    'content': '特定责任除外后承保',
                    'decision': 'EXCLUSION',
                    'em_value': 1.0,
                    'rule_id': rule.id,
                    'type_id': exclusion_type.id
                }
            ]
            
            for c in conclusions:
                conclusion = Conclusion.query.filter_by(code=c['code']).first()
                if not conclusion:
                    conclusion = Conclusion(
                        code=c['code'],
                        name=c['name'],
                        content=c['content'],
                        decision=c['decision'],
                        em_value=c['em_value'],
                        rule_id=c['rule_id'],
                        type_id=c['type_id']
                    )
                    db.session.add(conclusion)
            db.session.commit()

            # 创建 AI 参数类型
            print('创建AI参数类型')
            parameter_types = [
                ('TRADITIONAL', '传统问答'),
                ('INTELLIGENT', '智能对话')
            ]

            type_map = {}  # 存储参数类型ID的映射
            for code, name in parameter_types:
                param_type = AIParameterType.query.filter_by(code=code).first()
                if not param_type:
                    param_type = AIParameterType(
                        name=name,
                        code=code,
                        description=f'{name}参数类型',
                        value_type='string',
                        status='enabled'
                    )
                    db.session.add(param_type)
                    db.session.commit()
                type_map[code] = param_type

            # 获取默认规则
            rule = UnderwritingRule.query.filter_by(name='默认规则').first()
            if rule:
                # 创建AI参数
                ai_params = [
                    {
                        'name': '传统问答参数',
                        'parameter_type_id': type_map['TRADITIONAL'].id,
                        'rule_id': rule.id,
                        'value': '{"mode": "traditional", "threshold": 0.8}',
                        'description': '传统问答方式的默认配置',
                        'status': 'enabled'
                    },
                    {
                        'name': '智能对话参数',
                        'parameter_type_id': type_map['INTELLIGENT'].id,
                        'rule_id': rule.id,
                        'value': '{"mode": "intelligent", "threshold": 0.9}',
                        'description': '智能对话方式的高级配置',
                        'status': 'enabled'
                    }
                ]

                for param in ai_params:
                    existing_param = AIParameter.query.filter_by(name=param['name']).first()
                    if not existing_param:
                        ai_param = AIParameter(**param)
                        db.session.add(ai_param)
                db.session.commit()

            # 4. 创建产品
            default_channel = Channel.query.filter_by(code='default').first()
            default_company = InsuranceCompany.query.filter_by(code='default').first()
            default_type = ProductType.query.filter_by(code='default').first()
            default_ai = AIParameter.query.filter_by(name='传统AI参数').first()

            products = [
                ('默认产品', 'DEFAULT001'),
                ('医疗保险', 'MEDICAL001'),
                ('寿险产品', 'LIFE001')
            ]
            
            for name, code in products:
                if not Product.query.filter_by(product_code=code).first():
                    product = Product(
                        name=name,
                        product_code=code,
                        product_type_id=default_type.id,
                        insurance_company_id=default_company.id,
                        channel_id=default_channel.id,
                        ai_parameter_id=default_ai.id,  # 关联默认AI参数
                        status='enabled'
                    )
                    db.session.add(product)

            db.session.commit()
            print('所有数据创建成功')
            
            # 5. 验证关联关系
            verify_relationships()
            
            # 创建更多疾病类别
            disease_categories.extend([
                ('内分泌系统疾病', 'ENDOCRINE'),
                ('神经系统疾病', 'NERVOUS'),
                ('骨骼肌肉系统疾病', 'MUSCULOSKELETAL'),
                ('泌尿系统疾病', 'URINARY'),
                ('血液系统疾病', 'HEMATOLOGICAL'),
                ('免疫系统疾病', 'IMMUNE')
            ])
            
            for name, code in disease_categories:
                category = DiseaseCategory.query.filter_by(code=code).first()
                if not category:
                    category = DiseaseCategory(
                        name=name,
                        code=code
                    )
                    db.session.add(category)
            db.session.commit()

            # 创建更多疾病数据
            diseases_data = {
                'CARDIOVASCULAR': [
                    ('高血压', 'HYPERTENSION', True),
                    ('冠心病', 'CHD', True),
                    ('心律失常', 'ARRHYTHMIA', False),
                    ('心肌梗塞', 'MI', True),
                    ('心力衰竭', 'HEART_FAILURE', True)
                ],
                'RESPIRATORY': [
                    ('哮喘', 'ASTHMA', True),
                    ('慢性支气管炎', 'BRONCHITIS', True),
                    ('肺炎', 'PNEUMONIA', False),
                    ('肺结核', 'TB', True),
                    ('慢性阻塞性肺疾病', 'COPD', True)
                ],
                'ENDOCRINE': [
                    ('糖尿病', 'DIABETES', True),
                    ('甲状腺功能亢进', 'HYPERTHYROIDISM', True),
                    ('甲状腺功能减退', 'HYPOTHYROIDISM', False),
                    ('肥胖', 'OBESITY', True)
                ]
            }
            
            for category_code, diseases in diseases_data.items():
                category = DiseaseCategory.query.filter_by(code=category_code).first()
                if category:
                    for name, code, is_common in diseases:
                        if not Disease.query.filter_by(code=code).first():
                            disease = Disease(
                                name=name,
                                code=code,
                                category_id=category.id,
                                category_code=category.code,
                                category_name=category.name,
                                description=f'{name}是一种{category.name}，需要详细评估。',
                                is_common=is_common
                            )
                            db.session.add(disease)
            db.session.commit()

            # 创建更多问题数据
            questions.extend([
                {
                    'code': 'Q_GENERAL_1',
                    'content': '您的一般健康状况如何？',
                    'attribute': 'P',
                    'question_type': '1',
                    'remark': '了解患者的一般健康状况'
                },
                {
                    'code': 'Q_GENERAL_2',
                    'content': '过去一年内您去医院就医的频率是多少？',
                    'attribute': 'P',
                    'question_type': '1',
                    'remark': '了解患者的就医频率'
                },
                {
                    'code': 'Q_MEDICAL_1',
                    'content': '您目前是否正在服用任何药物？',
                    'attribute': 'P',
                    'question_type': '1',
                    'remark': '了解患者的用药情况'
                },
                {
                    'code': 'Q_MEDICAL_2',
                    'content': '您是否做过任何手术？',
                    'attribute': 'P',
                    'question_type': '1',
                    'remark': '了解患者的手术史'
                }
            ])
            
            for q in questions:
                if not Question.query.filter_by(code=q['code']).first():
                    question = Question(
                        code=q['code'],
                        content=q['content'],
                        attribute=q['attribute'],
                        question_type=q['question_type'],
                        remark=q['remark'],
                        rule_id=rule.id
                    )
                    db.session.add(question)
            db.session.commit()

            print('所有数据创建成功')
            
            # 5. 验证关联关系
            verify_relationships()
            
            # 创建更多的AI参数类型
            print('\n创建更多AI参数类型:')
            parameter_types.extend([
                ('RISK_LEVEL', '风险等级'),
                ('AGE_LIMIT', '年龄限制'),
                ('OCCUPATION', '职业类别')
            ])

            for code, name in parameter_types:
                param_type = AIParameterType.query.filter_by(code=code).first()
                if not param_type:
                    param_type = AIParameterType(
                        name=name,
                        code=code,
                        description=f'{name}参数类型',
                        value_type='string',
                        status='enabled'
                    )
                    db.session.add(param_type)
                    db.session.commit()
                    print(f'- 创建参数类型: {name} ({code})')
                type_map[code] = param_type

            # 获取默认规则
            rule = UnderwritingRule.query.filter_by(name='默认规则').first()
            if rule:
                # 创建更多AI参数
                ai_params.extend([
                    {
                        'name': '风险等级参数',
                        'parameter_type_id': type_map['RISK_LEVEL'].id,
                        'rule_id': rule.id,
                        'value': '{"risk_levels": ["low", "medium", "high"], "thresholds": [0.3, 0.7]}',
                        'description': '风险等级评估配置',
                        'status': 'enabled'
                    },
                    {
                        'name': '年龄限制参数',
                        'parameter_type_id': type_map['AGE_LIMIT'].id,
                        'rule_id': rule.id,
                        'value': '{"min_age": 18, "max_age": 65}',
                        'description': '年龄限制配置',
                        'status': 'enabled'
                    },
                    {
                        'name': '职业类别参数',
                        'parameter_type_id': type_map['OCCUPATION'].id,
                        'rule_id': rule.id,
                        'value': '{"occupation_levels": ["1", "2", "3", "4", "5", "6"]}',
                        'description': '职业类别配置',
                        'status': 'enabled'
                    }
                ])

                print('\n创建AI参数:')
                for param in ai_params:
                    existing_param = AIParameter.query.filter_by(name=param['name']).first()
                    if not existing_param:
                        ai_param = AIParameter(**param)
                        db.session.add(ai_param)
                        print(f'- 创建参数: {param["name"]} (类型: {type_map[next(k for k, v in type_map.items() if v.id == param["parameter_type_id"])].name})')
                db.session.commit()

            print('\n打印数据关系:')
            print('=' * 50)
            print('AI参数类型:')
            for param_type in AIParameterType.query.all():
                print(f'\n类型: {param_type.name} ({param_type.code})')
                print(f'描述: {param_type.description}')
                params = AIParameter.query.filter_by(parameter_type_id=param_type.id).all()
                print(f'关联的参数:')
                for param in params:
                    print(f'  - {param.name}')
                    print(f'    值: {param.value}')
                    print(f'    描述: {param.description}')
                    print(f'    状态: {param.status}')
                    print(f'    规则: {param.rule.name if param.rule else "未关联"}')

            print('\n=' * 50)
            print('核保规则:')
            for rule in UnderwritingRule.query.all():
                print(f'\n规则: {rule.name} (版本: {rule.version})')
                print(f'状态: {rule.status}')
                params = AIParameter.query.filter_by(rule_id=rule.id).all()
                print(f'关联的参数:')
                for param in params:
                    print(f'  - {param.name} ({param.parameter_type.name})')

            print('\n验证完成')
            
        except Exception as e:
            print(f'初始化失败: {str(e)}')
            db.session.rollback()
            raise e

def verify_relationships():
    """验证所有关联关系"""
    print('\n验证关联关系:')
    
    # 验证产品关联
    product = Product.query.filter_by(product_code='DEFAULT001').first()
    if product:
        print('\n产品关联:')
        print(f'产品 -> 渠道: {product.channel.name if product.channel else "未关联"}')
        print(f'产品 -> 保险公司: {product.insurance_company.name if product.insurance_company else "未关联"}')
        print(f'产品 -> 产品类型: {product.product_type.name if product.product_type else "未关联"}')
        print(f'产品 -> AI参数: {product.ai_parameter.name if product.ai_parameter else "未关联"}')
    
    # 验证规则关联
    rule = UnderwritingRule.query.filter_by(name='默认规则').first()
    if rule:
        print('\n规则关联:')
        print(f'规则名称: {rule.name}')
        diseases = Disease.query.all()
        questions = Question.query.filter_by(rule_id=rule.id).all()
        conclusions = Conclusion.query.filter_by(rule_id=rule.id).all()
        print(f'疾病数量: {len(diseases)}')
        print(f'问题数量: {len(questions)}')
        print(f'结论数量: {len(conclusions)}')
    
    # 验证疾病类别
    categories = DiseaseCategory.query.all()
    if categories:
        print('\n疾病类别:')
        for category in categories:
            diseases = Disease.query.filter_by(category_id=category.id).all()
            print(f'{category.name}: {len(diseases)}个疾病')
    
    # 验证问题类型
    question_types = QuestionType.query.all()
    if question_types:
        print('\n问题类型:')
        for qtype in question_types:
            questions = Question.query.filter_by(type_id=qtype.id).all()
            print(f'{qtype.name}: {len(questions)}个问题')
    
    # 验证结论类型
    conclusion_types = ConclusionType.query.all()
    if conclusion_types:
        print('\n结论类型:')
        for ctype in conclusion_types:
            conclusions = Conclusion.query.filter_by(type_id=ctype.id).all()
            print(f'{ctype.name}: {len(conclusions)}个结论')
    
    # 验证AI参数
    ai_params = AIParameter.query.all()
    if ai_params:
        print('\nAI参数:')
        for param in ai_params:
            print(f'名称: {param.name}')
            print(f'类型: {param.parameter_type.name if param.parameter_type else "未关联"}')
            print(f'规则: {param.rule.name if param.rule else "未关联"}')

if __name__ == '__main__':
    init_db()