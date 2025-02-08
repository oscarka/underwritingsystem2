from flask import render_template, jsonify, request
from app.models.base.enums import StatusEnum
from app.extensions import db

class CRUDView:
    """通用CRUD视图基类"""
    
    # 配置项
    template_folder = None  # 模板文件夹
    model_class = None     # 模型类
    
    @classmethod
    def get_template(cls, name):
        """获取模板路径"""
        return f"{cls.template_folder}/{name}.html"
    
    @classmethod
    def render_template(cls, template_name, **kwargs):
        """渲染模板"""
        return render_template(cls.get_template(template_name), **kwargs)
    
    @classmethod
    def format_response(cls, success=True, message='', data=None):
        """格式化响应数据"""
        return jsonify({
            'status': 'success' if success else 'error',
            'message': message,
            'data': data
        })
    
    @classmethod
    def get_status_display(cls, status):
        """获取状态显示文本"""
        status_map = {
            StatusEnum.DRAFT.value: '草稿',
            StatusEnum.ENABLED.value: '已启用',
            StatusEnum.DISABLED.value: '已禁用',
            StatusEnum.DELETED.value: '已删除',
            StatusEnum.IMPORTED.value: '已导入'
        }
        return status_map.get(status, status)
    
    @classmethod
    def validate_data(cls, data, required_fields=None):
        """验证数据"""
        errors = []
        if required_fields:
            for field in required_fields:
                if not data.get(field):
                    errors.append(f'{field}不能为空')
        return len(errors) == 0, errors 