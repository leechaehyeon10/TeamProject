Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> from flask import Flask, render_template, redirect, url_for, request
... from flask_sqlalchemy import SQLAlchemy
... from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
... 
... app = Flask(__name__)
... app.config['SECRET_KEY'] = 'your_secret_key'
... app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
... 
... # 데이터베이스 설정
... db = SQLAlchemy(app)
... 
... # Flask-Login 설정
... login_manager = LoginManager()
... login_manager.init_app(app)
... login_manager.login_view = 'login'
... 
... 
... # 데이터베이스 모델
... class User(UserMixin, db.Model):
...     id = db.Column(db.Integer, primary_key=True)
...     username = db.Column(db.String(100), unique=True, nullable=False)
...     password = db.Column(db.String(100), nullable=False)
... 
... 
... # 로그인 사용자 로딩
... @login_manager.user_loader
... def load_user(user_id):
...     return User.query.get(int(user_id))
... 
... 
... # 홈 페이지 (로그인 페이지로 리디렉션)
... @app.route('/')
... def index():
...     if current_user.is_authenticated:
...         return redirect(url_for('word_submission'))
...     return redirect(url_for('login'))


# 사용자 등록 페이지
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 사용자 정보 저장
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')


# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('word_submission'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('word_submission'))
        else:
            return 'Invalid username or password', 401
    
    return render_template('login.html')


# 단어 제출 페이지 (로그인 후 접근)
@app.route('/word_submission')
@login_required
def word_submission():
    return render_template('word_submission.html', username=current_user.username)


# 로그아웃
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# 애플리케이션 실행
if __name__ == "__main__":
    db.create_all()  # DB 초기화
    app.run(debug=True)
