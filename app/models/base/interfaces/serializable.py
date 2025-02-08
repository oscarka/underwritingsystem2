from abc import ABC, abstractmethod
from typing import Dict, Any

class SerializableMixin:
    """序列化接口"""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        pass
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """从字典加载"""
        pass 