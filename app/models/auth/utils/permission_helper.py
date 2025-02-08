from typing import List, Set, Dict, Any
from functools import wraps
from flask_login import current_user
from flask import abort

def permission_required(permission: str):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class PermissionRegistry:
    """权限注册表"""
    _permissions: Set[str] = set()
    _permission_groups: Dict[str, List[str]] = {}
    
    @classmethod
    def register(cls, permission: str) -> None:
        """注册权限"""
        cls._permissions.add(permission)
    
    @classmethod
    def register_group(cls, group: str, permissions: List[str]) -> None:
        """注册权限组"""
        cls._permission_groups[group] = permissions
        for permission in permissions:
            cls.register(permission)
    
    @classmethod
    def get_all(cls) -> List[str]:
        """获取所有权限"""
        return sorted(list(cls._permissions))
    
    @classmethod
    def get_groups(cls) -> Dict[str, List[str]]:
        """获取所有权限组"""
        return cls._permission_groups
    
    @classmethod
    def clear(cls) -> None:
        """清空权限注册表"""
        cls._permissions.clear()
        cls._permission_groups.clear() 