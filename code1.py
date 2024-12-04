Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
from openpyxl import load_workbook

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Flask-Login 설정
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Excel 파일 경로
EXCEL_FILE = 'users.xlsx'


# 사용자 데이터 로드
def load_users():
    try:
        return pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=['username', 'password'])


# 사용자 모델
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# 로그인 사용자 로딩
@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = users.iloc[int(user_id)]
    return User(id=user_data.name, username=user_data['username'])


# 홈 페이지 (로그인 페이지로 리디렉션)
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('word_submission'))
    return redirect(url_for('login'))


# 사용자 등록 페이지
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        if username in users['username'].values:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        new_user = pd.DataFrame([[username, password]], columns=['username', 'password'])
        users = pd.concat([users, new_user], ignore_index=True)
        users.to_excel(EXCEL_FILE, index=False)

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('word_submission'))
    
    if request.method == 'POST':
        username = request.form['username']
...         password = request.form['password']
...         
...         users = load_users()
...         user_data = users[users['username'] == username]
...         
...         if not user_data.empty and user_data['password'].values[0] == password:
...             user = User(id=user_data.index[0], username=username)
...             login_user(user)
...             return redirect(url_for('word_submission'))
...         else:
...             flash('Invalid username or password', 'danger')
...     
...     return render_template('login.html')
... 
... 
... # 단어 제출 페이지
... @app.route('/word_submission', methods=['GET', 'POST'])
... @login_required
... def word_submission():
...     if request.method == 'POST':
...         word = request.form['word']
...         # 여기서 단어를 처리하거나 끝말잇기 규칙을 적용할 수 있음
...         flash(f'Your word "{word}" has been submitted!', 'success')
...     
...     return render_template('word_submission.html', username=current_user.username)
... 
... 
... # 로그아웃
... @app.route('/logout')
... @login_required
... def logout():
...     logout_user()
...     return redirect(url_for('index'))
... 
... 
... # 애플리케이션 실행
... if __name__ == "__main__":
...     app.run(debug=True)
