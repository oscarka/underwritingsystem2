from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.auth.user import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("User already authenticated")
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt: username={username}, password={password}")  # 打印密码用于调试
        
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: id={user.id}, password_hash={user.password_hash}")  # 打印密码哈希
            if user.check_password(password):
                print("Password correct")
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.index')
                print(f"Redirecting to: {next_page}")
                return redirect(next_page)
            else:
                print("Password incorrect")
        else:
            print("User not found")
            
        flash('用户名或密码错误')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 