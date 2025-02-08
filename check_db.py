from app import create_app, db
from app.models import Disease, Question, Conclusion

app = create_app()

with app.app_context():
    # 删除现有的表（如果需要重建）
    # db.drop_all()
    
    # 创建所有表
    db.create_all()
    
    # 验证表是否存在
    tables = db.engine.table_names()
    print("现有数据库表:", tables)
    
    # 检查特定表
    required_tables = ['disease', 'question', 'conclusion']
    for table in required_tables:
        if table in tables:
            print(f"表 {table} 已存在")
        else:
            print(f"警告: 表 {table} 不存在")