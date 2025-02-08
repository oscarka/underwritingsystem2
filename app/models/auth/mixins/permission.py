from app import db
from typing import List, Set, Dict, Any
from app.models.auth.utils.permission_helper import PermissionRegistry

class PermissionMixin:
    """权限管理混入类"""
    permissions = db.Column(db.JSON)
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        if not self.permissions:
            return False
        perms = self.permissions.get('permissions', [])
        return permission in perms or '*' in perms
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """检查是否有任意一个权限"""
        return any(self.has_permission(p) for p in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """检查是否有所有权限"""
        return all(self.has_permission(p) for p in permissions)
    
    def add_permission(self, permission: str) -> None:
        """添加权限"""
        if not self.permissions:
            self.permissions = {'permissions': []}
        if permission not in self.permissions['permissions']:
            self.permissions['permissions'].append(permission)
            PermissionRegistry.register(permission)
    
    def remove_permission(self, permission: str) -> None:
        """移除权限"""
        if self.permissions and permission in self.permissions.get('permissions', []):
            self.permissions['permissions'].remove(permission)
    
    def set_permissions(self, permissions: List[str]) -> None:
        """设置权限列表"""
        self.permissions = {'permissions': permissions}
        for permission in permissions:
            PermissionRegistry.register(permission)
    
    def clear_permissions(self) -> None:
        """清空权限"""
        self.permissions = {'permissions': []}
    
    @property
    def permission_list(self) -> List[str]:
        """获取权限列表"""
        if not self.permissions:
            return []
        return self.permissions.get('permissions', []) 