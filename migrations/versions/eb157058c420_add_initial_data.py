"""add_initial_data

Revision ID: eb157058c420
Revises: 
Create Date: 2025-02-08 17:46:01.456789

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from werkzeug.security import generate_password_hash
from app.models import (
    User, Channel, Product, AIParameter, UnderwritingRule, 
    InsuranceCompany, ProductType, Tenant, Disease, Question, Conclusion, 
    DiseaseCategory, QuestionType, ConclusionType, AIParameterType
)


# revision identifiers, used by Alembic.
revision = 'eb157058c420'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 获取绑定的连接
    connection = op.get_bind()
    
    # 创建默认租户
    tenant = sa.Table(
        'tenant',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50)),
        sa.Column('code', sa.String(50)),
        sa.Column('status', sa.String(20))
    )
    
    connection.execute(
        tenant.insert().values(
            name='默认租户',
            code='default',
            status='enabled'
        )
    )
    
    # 创建管理员用户
    user = sa.Table(
        'user',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50)),
        sa.Column('password_hash', sa.String(128)),
        sa.Column('is_admin', sa.Boolean),
        sa.Column('tenant_id', sa.Integer),
        sa.Column('status', sa.String(20))
    )
    
    # 生成管理员密码哈希
    admin_password = 'admin123'
    password_hash = generate_password_hash(admin_password)
    
    connection.execute(
        user.insert().values(
            username='admin',
            password_hash=password_hash,
            is_admin=True,
            tenant_id=1,
            status='enabled'
        )
    )
    
    # 创建问题类型
    question_type = sa.Table(
        'question_type',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(50)),
        sa.Column('name', sa.String(50)),
        sa.Column('input_type', sa.String(20))
    )
    
    question_types_data = [
        ('BASIC', '基础问题', 'radio'),
        ('MEDICAL', '医疗问题', 'radio'),
        ('LIFESTYLE', '生活习惯', 'radio'),
        ('FAMILY', '家族病史', 'radio')
    ]
    
    for code, name, input_type in question_types_data:
        connection.execute(
            question_type.insert().values(
                code=code,
                name=name,
                input_type=input_type
            )
        )
    
    # 创建渠道
    channel = sa.Table(
        'channel',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(50)),
        sa.Column('name', sa.String(50))
    )
    
    channels_data = [
        ('default', '默认渠道'),
        ('online', '线上渠道'),
        ('offline', '线下渠道')
    ]
    
    for code, name in channels_data:
        connection.execute(
            channel.insert().values(
                code=code,
                name=name
            )
        )
    
    # 创建保险公司
    insurance_company = sa.Table(
        'insurance_company',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(50)),
        sa.Column('name', sa.String(50))
    )
    
    companies_data = [
        ('default', '默认保险公司'),
        ('pingan', '中国平安'),
        ('cpic', '中国太保')
    ]
    
    for code, name in companies_data:
        connection.execute(
            insurance_company.insert().values(
                code=code,
                name=name
            )
        )
    
    # 创建产品类型
    product_type = sa.Table(
        'product_type',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(50)),
        sa.Column('name', sa.String(50)),
        sa.Column('description', sa.String(200))
    )
    
    product_types_data = [
        ('default', '默认类型'),
        ('medical', '医疗险'),
        ('life', '寿险'),
        ('accident', '意外险')
    ]
    
    for code, name in product_types_data:
        connection.execute(
            product_type.insert().values(
                code=code,
                name=name,
                description=f'{name}产品类型'
            )
        )
    
    # 创建核保规则
    underwriting_rule = sa.Table(
        'underwriting_rule',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50)),
        sa.Column('version', sa.String(20)),
        sa.Column('status', sa.String(20)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )
    
    connection.execute(
        underwriting_rule.insert().values(
            name='默认规则',
            version='1.0',
            status='已导入',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    )
    
    # 创建疾病类别
    disease_category = sa.Table(
        'disease_category',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50)),
        sa.Column('code', sa.String(50))
    )
    
    disease_categories_data = [
        ('心血管疾病', 'CARDIOVASCULAR'),
        ('呼吸系统疾病', 'RESPIRATORY'),
        ('消化系统疾病', 'DIGESTIVE')
    ]
    
    for name, code in disease_categories_data:
        connection.execute(
            disease_category.insert().values(
                name=name,
                code=code
            )
        )
    
    # 创建疾病
    disease = sa.Table(
        'disease',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50)),
        sa.Column('code', sa.String(50)),
        sa.Column('category_id', sa.Integer),
        sa.Column('category_code', sa.String(50)),
        sa.Column('category_name', sa.String(50)),
        sa.Column('description', sa.String(200)),
        sa.Column('is_common', sa.Boolean)
    )
    
    diseases_data = [
        ('高血压', 'HYPERTENSION'),
        ('冠心病', 'CHD'),
        ('心律失常', 'ARRHYTHMIA')
    ]
    
    for name, code in diseases_data:
        connection.execute(
            disease.insert().values(
                name=name,
                code=code,
                category_id=1,  # 心血管疾病的ID
                category_code='CARDIOVASCULAR',
                category_name='心血管疾病',
                description=f'{name}的基本描述',
                is_common=True
            )
        )
    
    # 创建结论类型
    conclusion_type = sa.Table(
        'conclusion_type',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(50)),
        sa.Column('name', sa.String(50)),
        sa.Column('input_type', sa.String(20))
    )
    
    conclusion_types_data = [
        ('STANDARD', '标准承保', 'radio'),
        ('SUBSTANDARD', '次标准承保', 'radio'),
        ('DECLINE', '拒保', 'radio'),
        ('POSTPONE', '延期', 'radio'),
        ('EXCLUSION', '除外责任', 'radio')
    ]
    
    for code, name, input_type in conclusion_types_data:
        connection.execute(
            conclusion_type.insert().values(
                code=code,
                name=name,
                input_type=input_type
            )
        )
    
    # 创建示例问题
    question = sa.Table(
        'question',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(50)),
        sa.Column('content', sa.String(200)),
        sa.Column('attribute', sa.String(10)),
        sa.Column('question_type', sa.String(20)),
        sa.Column('remark', sa.String(200)),
        sa.Column('rule_id', sa.Integer),
        sa.Column('type_id', sa.Integer)
    )
    
    # 先获取问题类型的ID
    question_type_ids = {}
    for code, name, _ in question_types_data:
        result = connection.execute(
            sa.text(f"SELECT id FROM question_type WHERE code = '{code}'")
        ).fetchone()
        if result:
            question_type_ids[code] = result[0]
    
    questions_data = [
        {
            'code': 'Q_1',
            'content': '您是否被诊断或怀疑有高血压？',
            'attribute': 'P',
            'question_type': '1',
            'remark': '了解患者是否有高血压病史',
            'type_id': question_type_ids['BASIC']
        },
        {
            'code': 'Q_2',
            'content': '您的高血压是否在进行规律治疗？',
            'attribute': 'P',
            'question_type': '1',
            'remark': '了解患者的治疗情况',
            'type_id': question_type_ids['MEDICAL']
        },
        {
            'code': 'Q_3',
            'content': '您的血压是否控制稳定？',
            'attribute': 'P',
            'question_type': '1',
            'remark': '了解患者的血压控制情况',
            'type_id': question_type_ids['MEDICAL']
        }
    ]
    
    for q in questions_data:
        connection.execute(
            question.insert().values(
                code=q['code'],
                content=q['content'],
                attribute=q['attribute'],
                question_type=q['question_type'],
                remark=q['remark'],
                rule_id=1,  # 默认规则的ID
                type_id=q['type_id']
            )
        )
    
    # 创建结论
    conclusion = sa.Table(
        'conclusion',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String(50)),
        sa.Column('name', sa.String(50)),
        sa.Column('content', sa.String(200)),
        sa.Column('decision', sa.String(50)),
        sa.Column('em_value', sa.Float),
        sa.Column('rule_id', sa.Integer),
        sa.Column('type_id', sa.Integer)
    )
    
    # 获取结论类型的ID
    conclusion_type_ids = {}
    for code, name, _ in conclusion_types_data:
        result = connection.execute(
            sa.text(f"SELECT id FROM conclusion_type WHERE code = '{code}'")
        ).fetchone()
        if result:
            conclusion_type_ids[code] = result[0]
    
    conclusions_data = [
        {
            'code': 'C001',
            'name': '标准承保',
            'content': '可以标准费率承保',
            'decision': 'STANDARD',
            'em_value': 1.0,
            'type_id': conclusion_type_ids['STANDARD']
        },
        {
            'code': 'C002',
            'name': '加费承保',
            'content': '需要加费承保',
            'decision': 'SUBSTANDARD',
            'em_value': 1.5,
            'type_id': conclusion_type_ids['SUBSTANDARD']
        },
        {
            'code': 'C003',
            'name': '拒保',
            'content': '不予承保',
            'decision': 'DECLINE',
            'em_value': 0.0,
            'type_id': conclusion_type_ids['DECLINE']
        },
        {
            'code': 'C004',
            'name': '延期',
            'content': '暂缓承保',
            'decision': 'POSTPONE',
            'em_value': 0.0,
            'type_id': conclusion_type_ids['POSTPONE']
        },
        {
            'code': 'C005',
            'name': '除外责任',
            'content': '承保但除外特定责任',
            'decision': 'EXCLUSION',
            'em_value': 1.0,
            'type_id': conclusion_type_ids['EXCLUSION']
        }
    ]
    
    for c in conclusions_data:
        connection.execute(
            conclusion.insert().values(
                code=c['code'],
                name=c['name'],
                content=c['content'],
                decision=c['decision'],
                em_value=c['em_value'],
                rule_id=1,  # 默认规则的ID
                type_id=c['type_id']
            )
        )


def downgrade():
    # 删除初始数据
    connection = op.get_bind()
    
    tables = [
        'conclusion',
        'question',
        'disease',
        'disease_category',
        'conclusion_type',
        'underwriting_rule',
        'product_type',
        'insurance_company',
        'channel',
        'question_type',
        'user',
        'tenant'
    ]
    
    for table in tables:
        connection.execute(f'DELETE FROM {table}')
