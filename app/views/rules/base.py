from flask import render_template, request, jsonify
from app.models.base.enums import StatusEnum
from app.views.base import CRUDView

class RuleBaseView(CRUDView):
    """规则模块基础视图类"""
    
    template_folder = 'rules'  # 模板文件夹
    model_class = None  # 模型类
    list_template = None  # 列表页模板
    detail_template = None  # 详情页模板
    
    @classmethod
    def get_template(cls, name):
        """获取模板路径"""
        return f"{cls.template_folder}/{name}.html"
    
    @classmethod
    def render_list(cls, **kwargs):
        """渲染列表页"""
        return cls.render_template(cls.list_template, **kwargs)
    
    @classmethod
    def render_detail(cls, **kwargs):
        """渲染详情页"""
        return cls.render_template(cls.detail_template, **kwargs)
    
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
    def format_response(cls, success=True, message='', data=None):
        """格式化响应数据"""
        return jsonify({
            'success': success,
            'message': message,
            'data': data
        }) 