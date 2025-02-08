class BaseService:
    @staticmethod
    def get_by_id(model, id):
        return model.query.get(id)

    @staticmethod
    def get_all(model):
        return model.query.all() 