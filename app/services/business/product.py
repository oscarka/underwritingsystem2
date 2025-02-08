from app.services import BaseService
from app.models.business.product.product import Product
from app.extensions import db

class ProductService(BaseService):
    @staticmethod
    def get_all_products():
        return Product.query.all()

    @staticmethod
    def get_product_by_id(id):
        return Product.query.get(id)

    @staticmethod
    def create_product(data):
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_product(id, data):
        product = Product.query.get(id)
        if product:
            for key, value in data.items():
                setattr(product, key, value)
            db.session.commit()
        return product

    @staticmethod
    def delete_product(id):
        product = Product.query.get(id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False 