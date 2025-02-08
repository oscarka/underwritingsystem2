class StatusMixin:
    status = None  # 将在具体模型中定义
    
    @property
    def is_enabled(self):
        return self.status == 'enabled' 