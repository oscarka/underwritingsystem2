from typing import Optional

class AuthenticatableMixin:  # 改为普通类而不是ABC
    """认证接口"""
    
    def authenticate(self, password: str) -> bool:
        """验证密码"""
        return False
    
    def get_id(self) -> str:
        """获取用户ID"""
        return str(getattr(self, 'id', None))
    
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return True
    
    def is_active(self) -> bool:
        """是否激活"""
        return True
    
    def is_anonymous(self) -> bool:
        """是否匿名用户"""
        return False 