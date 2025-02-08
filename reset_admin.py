from app import create_app, db
from app.models import User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.set_password('admin123')
            db.session.commit()
            print('管理员密码重置成功')
        else:
            print('管理员账号不存在')

if __name__ == '__main__':
    reset_admin_password() 