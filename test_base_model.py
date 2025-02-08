from app.models.base.model import BaseModel
from app.extensions import db

class TestModel(BaseModel):
    """测试模型"""
    __tablename__ = 'test_models'
    
    name = db.Column(db.String(50))
    code = db.Column(db.String(30))

def test_base_model():
    # 测试正常字段
    model1 = TestModel(name="Test", code="TEST")
    print("\n测试正常字段:")
    print(f"name: {model1.name}")
    print(f"code: {model1.code}")
    
    # 测试不存在的字段
    model2 = TestModel(name="Test", code="TEST", not_exist="value")
    print("\n测试不存在的字段:")
    print(f"name: {model2.name}")
    print(f"code: {model2.code}")
    try:
        print(f"not_exist: {model2.not_exist}")
    except AttributeError as e:
        print(f"获取不存在的字段时报错: {str(e)}")

if __name__ == "__main__":
    test_base_model() 