from app import db
from app.models.base.enums import StatusEnum

class RuleStatusMixin:
    """规则状态混入类"""
    status = db.Column(db.String(20), default=StatusEnum.DRAFT.value)
    
    @property
    def status_display(self):
        """获取状态的显示文本"""
        status_map = {
            StatusEnum.DRAFT.value: '草稿',
            StatusEnum.ENABLED.value: '已启用',
            StatusEnum.DISABLED.value: '已禁用',
            StatusEnum.DELETED.value: '已删除'
        }
        return status_map.get(self.status, self.status)
    
    @property
    def is_draft(self) -> bool:
        """是否为草稿状态"""
        return self.status == StatusEnum.DRAFT.value
    
    @property
    def is_enabled(self) -> bool:
        """是否已启用"""
        return self.status == StatusEnum.ENABLED.value
    
    @property
    def is_disabled(self) -> bool:
        """是否已禁用"""
        return self.status == StatusEnum.DISABLED.value
    
    @property
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.status == StatusEnum.DELETED.value 