from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('登录')

class ProductForm(FlaskForm):
    name = StringField('产品名称', validators=[DataRequired(), Length(max=100)])
    product_code = StringField('产品编码', validators=[DataRequired(), Length(max=50)])
    channel_id = SelectField('所属渠道', coerce=int, validators=[Optional()])
    product_type = StringField('产品类型', validators=[Optional(), Length(max=50)])
    insurance_company_id = SelectField('承保公司', coerce=int, validators=[Optional()])
    ai_parameter_id = SelectField('智核参数', coerce=int, validators=[Optional()])
    submit = SubmitField('保存')

class AIParameterForm(FlaskForm):
    name = StringField('参数名称', validators=[DataRequired(), Length(max=100)])
    ai_type = SelectField('智核方式', choices=[
        ('问答', '问答'),
        ('规则', '规则')
    ], validators=[DataRequired()])
    rule_version = StringField('核保规则', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('保存') 