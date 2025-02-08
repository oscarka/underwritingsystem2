from flask import (
    Blueprint, render_template, redirect, url_for, flash, 
    request, jsonify, Response, stream_with_context, session
)
from flask_login import login_user, logout_user, login_required, current_user
from app.models import (
    User, Channel, Product, AIParameter, UnderwritingRule, 
    Disease, Question, Conclusion, InsuranceCompany, ProductType, Tenant
)
from app.forms import LoginForm
from app import db, cache
import logging
import traceback
import os
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
from app.utils.rule_importer import RuleImporter
from io import BytesIO

# 设置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main = Blueprint('main', __name__)

# 添加产品列表路由
@main.route('/products')
@login_required
def products():
    """产品列表页面"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    products = Product.query.all()
    channels = Channel.query.all()
    return render_template('product_config.html', 
                         title='产品配置',
                         products=products,
                         channels=channels)

# 产品配置路由 - 重定向到新的产品管理页面
@main.route('/product_config')
@login_required
def product_config():
    """产品配置页面 - 重定向到新的产品管理页面"""
    return redirect(url_for('product_view.index'))

# 新增产品路由 - 重定向到新的产品管理页面
@main.route('/new_product', methods=['GET', 'POST'])
@login_required
def new_product():
    """新增产品页面 - 重定向到新的产品管理页面"""
    return redirect(url_for('product_view.index'))

@main.route('/')
@main.route('/index')
@login_required
def index():
    """首页"""
    return render_template('dashboard.html', title='首页')

@main.route('/login', methods=['GET', 'POST'])
def login():
    # 如果用户已经登录，直接重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误', 'error')
            return redirect(url_for('main.login'))
            
        login_user(user)
        # 记录登录日志
        logger.info(f"用户 {user.username} 登录成功")
        
        # 获取next参数，如果没有则默认跳转到首页
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
            
        return redirect(next_page)
        
    return render_template('login.html', title='登录', form=form)

@main.route('/logout')
def logout():
    """退出登录"""
    logout_user()
    return redirect(url_for('main.login'))

# 渠道配置
@main.route('/channel_config')
@login_required
def channel_config():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取渠道列表
    channels = Channel.query.all()
    return render_template('channel_config.html', 
                         title='渠道配置',
                         channels=channels)

# 新增渠道
@main.route('/new_channel', methods=['GET', 'POST'])
@login_required
def new_channel():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            channel = Channel(
                name=request.form['name'],
                code=request.form['code'],
                status='启用'
            )
            db.session.add(channel)
            db.session.commit()
            flash('渠道添加成功')
            return redirect(url_for('main.channel_config'))
        except Exception as e:
            db.session.rollback()
            flash('保存失败：' + str(e))
            return redirect(url_for('main.new_channel'))
            
    return render_template('new_channel.html', title='新增渠道')

# 编辑渠道
@main.route('/edit_channel/<int:channel_id>', methods=['GET', 'POST'])
@login_required
def edit_channel(channel_id):
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    channel = Channel.query.get_or_404(channel_id)
    
    if request.method == 'POST':
        try:
            channel.name = request.form['name']
            channel.code = request.form['code']
            channel.status = request.form['status']
            db.session.commit()
            flash('渠道更新成功')
            return redirect(url_for('main.channel_config'))
        except Exception as e:
            db.session.rollback()
            flash('保存失败：' + str(e))
            
    return render_template('edit_channel.html', 
                         title='编辑渠道',
                         channel=channel)

# 删除渠道 API
@main.route('/api/channels/<int:channel_id>', methods=['DELETE'])
@login_required
def delete_channel(channel_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '没有权限'})
    try:
        channel = Channel.query.get_or_404(channel_id)
        db.session.delete(channel)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# 核保规则配置
@main.route('/rule_config')
@login_required
def rule_config():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    try:
        # 获取查询参数
        name = request.args.get('name', '')
        version = request.args.get('version', '')
        
        # 构建查询
        query = UnderwritingRule.query
        if name:
            query = query.filter(UnderwritingRule.name.like(f'%{name}%'))
        if version:
            query = query.filter(UnderwritingRule.version.like(f'%{version}%'))
            
        # 获取规则列表
        rules = query.order_by(UnderwritingRule.created_at.desc()).all()
        
        return render_template('rule_config.html', 
                             title='核保规则配置',
                             rules=rules)
    except Exception as e:
        flash('加载规则列表失败：' + str(e))
        return redirect(url_for('main.index'))

# 智核参数配置
@main.route('/ai_param_config')
@login_required
def ai_param_config():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取参数列表
    parameters = AIParameter.query.all()
    return render_template('ai_param_config.html', 
                         title='智核参数配置',
                         parameters=parameters)

# 核保数据
@main.route('/underwriting_data')
@login_required
def underwriting_data():
    """核保数据页面"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    try:
        # 获取查询参数
        order_code = request.args.get('order_code', '')
        customer_name = request.args.get('customer_name', '')
        
        # 构建查询
        query = UnderwritingOrder.query
        if order_code:
            query = query.filter(UnderwritingOrder.order_code.like(f'%{order_code}%'))
        if customer_name:
            query = query.filter(UnderwritingOrder.customer_name.like(f'%{customer_name}%'))
            
        # 获取订单列表
        orders = query.order_by(UnderwritingOrder.created_at.desc()).all()
        
        return render_template('underwriting_orders.html',
                             title='核保订单数据',
                             orders=orders)
    except Exception as e:
        logger.error(f"加载核保订单列表失败: {str(e)}", exc_info=True)
        flash('加载核保订单列表失败：' + str(e))
        return redirect(url_for('main.index'))

# 外部服务数据
@main.route('/external_service_data')
@login_required
def external_service_data():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    return render_template('external_service_data.html', title='外部服务数据')

# 新增规则
@main.route('/new_rule', methods=['GET', 'POST'])
@login_required
def new_rule():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            # 打印请求数据，用于调试
            print("Form data:", request.form)
            
            rule = UnderwritingRule(
                name=request.form['name'],
                version=request.form['version'],
                rule_type=request.form['rule_type'],
                description=request.form.get('description', ''),
                status='未导入'  # 初始状态为未导入
            )
            db.session.add(rule)
            db.session.commit()
            flash('规则添加成功')
            return redirect(url_for('main.rule_config'))
        except Exception as e:
            db.session.rollback()
            flash('保存失败：' + str(e))
            print("Error:", str(e))  # 打印错误信息，用于调试
            return redirect(url_for('main.new_rule'))
            
    return render_template('new_rule.html', title='新增规则')

# 编辑规则
@main.route('/edit_rule/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    rule = UnderwritingRule.query.get_or_404(rule_id)
    
    if request.method == 'POST':
        try:
            rule.name = request.form['name']
            rule.version = request.form['version']
            rule.rule_type = request.form['rule_type']
            rule.description = request.form.get('description', '')
            rule.status = request.form['status']
            db.session.commit()
            flash('规则更新成功')
            return redirect(url_for('main.rule_config'))
        except Exception as e:
            db.session.rollback()
            flash('保存失败：' + str(e))
            
    return render_template('edit_rule.html', 
                         title='编辑规则',
                         rule=rule)

# 新增参数
@main.route('/new_parameter', methods=['GET', 'POST'])
@login_required
def new_parameter():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    # 获取默认租户
    default_tenant = Tenant.query.filter_by(code='DEFAULT').first()
    if not default_tenant:
        flash('系统错误：未找到默认租户')
        return redirect(url_for('main.ai_param_config'))

    if request.method == 'POST':
        try:
            parameter = AIParameter(
                name=request.form['name'],
                param_type=request.form['param_type'],
                tenant_id=default_tenant.id,  # 使用默认租户
                rule_id=request.form.get('rule_id'),
                status='启用'
            )
            db.session.add(parameter)
            db.session.commit()
            flash('参数添加成功')
            return redirect(url_for('main.ai_param_config'))
        except Exception as e:
            db.session.rollback()
            flash('保存失败：' + str(e))
            return redirect(url_for('main.new_parameter'))
            
    # 只获取已导入或已启用的核保规则
    rules = UnderwritingRule.query.filter(
        UnderwritingRule.status.in_(['已导入', '启用'])
    ).order_by(UnderwritingRule.created_at.desc()).all()
    
    return render_template('new_parameter.html',
                         title='新增智核参数',
                         default_tenant=default_tenant,
                         rules=rules)

# 编辑参数
@main.route('/edit_parameter/<int:param_id>', methods=['GET', 'POST'])
@login_required
def edit_parameter(param_id):
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    parameter = AIParameter.query.get_or_404(param_id)
    
    if request.method == 'POST':
        try:
            parameter.name = request.form['name']
            parameter.param_type = request.form['param_type']
            parameter.description = request.form.get('description', '')
            parameter.status = request.form['status']
            db.session.commit()
            flash('参数更新成功')
            return redirect(url_for('main.ai_param_config'))
        except Exception as e:
            db.session.rollback()
            flash('保存失败：' + str(e))
            
    return render_template('edit_parameter.html', 
                         title='编辑参数',
                         parameter=parameter)

# API 路由用于删除操作
@main.route('/api/rules/<int:rule_id>', methods=['DELETE'])
@login_required
def delete_rule(rule_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '没有权限'})
    try:
        rule = UnderwritingRule.query.get_or_404(rule_id)
        db.session.delete(rule)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main.route('/api/parameters/<int:param_id>', methods=['DELETE'])
@login_required
def delete_parameter(param_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '没有权限'})
    try:
        parameter = AIParameter.query.get_or_404(param_id)
        db.session.delete(parameter)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# 导入规则
@main.route('/import_rule', methods=['GET', 'POST'])
@login_required
def import_rule():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            # 处理文件上传
            if 'file' not in request.files:
                flash('没有选择文件')
                return redirect(request.url)
                
            file = request.files['file']
            if file.filename == '':
                flash('没有选择文件')
                return redirect(request.url)
                
            if file and allowed_file(file.filename):
                # 处理Excel文件
                df = pd.read_excel(file)
                # TODO: 处理导入逻辑
                flash('导入成功')
                return redirect(url_for('main.rule_config'))
            else:
                flash('不支持的文件格式')
                return redirect(request.url)
                
        except Exception as e:
            flash('导入失败：' + str(e))
            return redirect(request.url)
            
    return render_template('import_rule.html', title='导入规则')

# 下载规则模板
@main.route('/download_rule_template')
@login_required
def download_rule_template():
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    try:
        # 生成Excel模板
        template_path = os.path.join(current_app.root_path, 'static', 'templates', 'rule_template.xlsx')
        return send_file(template_path, 
                        as_attachment=True,
                        download_name='核保规则导入模板.xlsx')
    except Exception as e:
        flash('下载模板失败：' + str(e))
        return redirect(url_for('main.rule_config'))

# 导出规则
@main.route('/export_rule/<int:rule_id>')
@login_required
def export_rule(rule_id):
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    try:
        rule = UnderwritingRule.query.get_or_404(rule_id)
        # TODO: 生成Excel文件
        # 临时返回
        return jsonify({'success': True, 'message': '导出功能开发中'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# 查看规则详情
@main.route('/view_rule/<int:rule_id>')
@login_required
def view_rule(rule_id):
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    rule = UnderwritingRule.query.get_or_404(rule_id)
    
    # 获取规则相关的问题和结论
    questions = Question.query.filter_by(rule_id=rule_id).all()
    conclusions = Conclusion.query.filter_by(rule_id=rule_id).all()
    
    return render_template('view_rule.html', 
                         title='查看规则',
                         rule=rule,
                         questions=questions,
                         conclusions=conclusions)

# 导入规则数据
@main.route('/import_rule_data/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def import_rule_data(rule_id):
    """导入规则数据"""
    # 权限检查
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('main.index'))
        
    # 获取规则信息
    rule = UnderwritingRule.query.get_or_404(rule_id)
    
    if request.method == 'POST':
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                flash('没有选择文件', 'error')
                return redirect(request.url)
                
            file = request.files['file']
            if file.filename == '':
                flash('没有选择文件', 'error')
                return redirect(request.url)
                
            # 检查文件类型
            if not file.filename.endswith(('.xlsx', '.xls')):
                flash('不支持的文件格式，请上传Excel文件(.xlsx, .xls)', 'error')
                return redirect(request.url)
                
            # 读取Excel文件
            logger.info(f"开始读取文件: {file.filename}")
            
            # 使用BytesIO读取文件内容
            file_content = BytesIO(file.read())
            xls = pd.ExcelFile(file_content)
            
            # 检查必需的sheet是否存在
            required_sheets = {'疾病', '问题', '结论'}
            if not required_sheets.issubset(set(xls.sheet_names)):
                missing_sheets = required_sheets - set(xls.sheet_names)
                flash(f'Excel文件缺少必需的sheet: {", ".join(missing_sheets)}', 'error')
                return redirect(request.url)
            
            # 读取所有sheet页
            disease_df = pd.read_excel(file_content, sheet_name='疾病')
            file_content.seek(0)  # 重置文件指针
            question_df = pd.read_excel(file_content, sheet_name='问题')
            file_content.seek(0)  # 重置文件指针
            conclusion_df = pd.read_excel(file_content, sheet_name='结论')
            
            # 导入数据
            importer = RuleImporter(rule_id)
            success, message = importer.import_rule_data(disease_df, question_df, conclusion_df)
            
            if success:
                # 更新规则状态
                rule.status = '已导入'
                db.session.commit()
                flash(message, 'success')
                return redirect(url_for('main.rule_config'))
            else:
                flash(message, 'error')
                return redirect(request.url)
                
        except Exception as e:
            logger.error(f"导入失败: {str(e)}", exc_info=True)
            flash(f'导入失败: {str(e)}', 'error')
            return redirect(request.url)
            
    return render_template('import_rule_data.html', 
                         title='导入规则数据',
                         rule=rule)

@main.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '没有权限'})
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除产品失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)})

# 编辑产品 - 重定向到新的产品管理页面
@main.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """编辑产品页面 - 重定向到新的产品管理页面"""
    return redirect(url_for('product_view.index'))

@main.route('/underwriting_orders')
@login_required
def underwriting_orders():
    """核保订单数据页面"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    try:
        # 获取查询参数
        order_code = request.args.get('order_code', '')
        customer_name = request.args.get('customer_name', '')
        
        # 构建查询
        query = UnderwritingOrder.query
        if order_code:
            query = query.filter(UnderwritingOrder.order_code.like(f'%{order_code}%'))
        if customer_name:
            query = query.filter(UnderwritingOrder.customer_name.like(f'%{customer_name}%'))
            
        # 获取订单列表
        orders = query.order_by(UnderwritingOrder.created_at.desc()).all()
        
        return render_template('underwriting_orders.html',
                             title='核保订单数据',
                             orders=orders)
    except Exception as e:
        logger.error(f"加载核保订单列表失败: {str(e)}", exc_info=True)
        flash('加载核保订单列表失败：' + str(e))
        return redirect(url_for('main.index'))

@main.route('/view_order/<int:order_id>')
@login_required
def view_order(order_id):
    """查看核保订单详情"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    try:
        order = UnderwritingOrder.query.get_or_404(order_id)
        return render_template('view_order.html',
                             title='核保订单详情',
                             order=order)
    except Exception as e:
        logger.error(f"加载核保订单详情失败: {str(e)}", exc_info=True)
        flash('加载核保订单详情失败：' + str(e))
        return redirect(url_for('main.underwriting_orders'))

@main.route('/test_validation')
@login_required
def test_validation():
    """测试验证管理页面"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
        
    # 获取所有疾病大类
    disease_categories = Disease.query.with_entities(
        Disease.category_code.label('code'),
        Disease.category_name.label('name'),
        Disease.updated_at
    ).distinct().order_by(Disease.id).all()
    
    return render_template('test_validation.html', 
                         title='测试验证管理',
                         disease_categories=disease_categories)

@main.route('/api/get_rules_and_conclusions', methods=['POST'])
@login_required
def get_rules_and_conclusions():
    """获取核保规则和结论"""
    try:
        # 获取最新的规则
        rule = UnderwritingRule.query.filter_by(status='启用').order_by(UnderwritingRule.id.desc()).first()
        if not rule:
            return jsonify({'error': '没有找到启用的核保规则'}), 400
            
        # 获取该规则下的所有疾病
        diseases = Disease.query.filter_by(rule_id=rule.id).all()
        
        # 获取该规则下的所有问题
        questions = Question.query.filter_by(rule_id=rule.id).all()
        
        # 获取该规则下的所有结论
        conclusions = Conclusion.query.filter_by(rule_id=rule.id).all()
        
        return jsonify({
            'rule_id': rule.id,
            'diseases': [{'id': d.id, 'name': d.name, 'code': d.code} for d in diseases],
            'questions': [{'id': q.id, 'code': q.code, 'content': q.content} for q in questions],
            'conclusions': [{'id': c.id, 'question_code': c.question_code, 'answer_content': c.answer_content} 
                          for c in conclusions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500