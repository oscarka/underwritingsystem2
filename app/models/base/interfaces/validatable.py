from typing import List, Tuple

class ValidatableMixin:  # 改为普通类而不是ABC
    """数据验证接口"""
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证数据有效性"""
        return True, []

    def validate_create(self) -> Tuple[bool, List[str]]:
        """验证创建数据"""
        return self.validate()

    def validate_update(self) -> Tuple[bool, List[str]]:
        """验证更新数据"""
        return self.validate() 