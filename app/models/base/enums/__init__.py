"""枚举包"""
from enum import Enum

class StatusEnum(Enum):
    """状态枚举"""
    DRAFT = 'draft'         # 草稿
    ENABLED = 'enabled'     # 启用
    DISABLED = 'disabled'   # 禁用
    DELETED = 'deleted'     # 删除
    IMPORTED = 'imported'   # 已导入 