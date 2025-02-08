from app import create_app, db
from app.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('管理员账号创建成功')
        else:
            print('管理员账号已存在')

if __name__ == '__main__':
    create_admin()