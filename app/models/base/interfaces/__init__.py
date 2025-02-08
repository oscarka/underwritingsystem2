"""Base interfaces package."""
from app.models.base.interfaces.serializable import SerializableMixin
from app.models.base.interfaces.validatable import ValidatableMixin

__all__ = ['SerializableMixin', 'ValidatableMixin'] 