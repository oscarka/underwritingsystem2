from app.models.base.model import BaseModel
from app.models.base.mixins.code import CodeMixin
from app.extensions import db

class TestCodeModel(CodeMixin, BaseModel):
    """测试带编码的模型"""
    __tablename__ = 'test_code_models'
    
    name = db.Column(db.String(50))

def test_code_mixin():
    # 测试正常创建
    model1 = TestCodeModel(name="Test", code="TEST")
    print("\n测试正常创建:")
    print(f"name: {model1.name}")
    print(f"code: {model1.code}")
    
    # 测试不传 code
    model2 = TestCodeModel(name="Test")
    print("\n测试不传 code:")
    print(f"name: {model2.name}")
    print(f"code: {model2.code if hasattr(model2, 'code') else 'None'}")
    
    # 测试传入其他字段
    model3 = TestCodeModel(name="Test", code="TEST", other="value")
    print("\n测试传入其他字段:")
    print(f"name: {model3.name}")
    print(f"code: {model3.code}")
    try:
        print(f"other: {model3.other}")
    except AttributeError as e:
        print(f"获取不存在的字段时报错: {str(e)}")

if __name__ == "__main__":
    test_code_mixin() 