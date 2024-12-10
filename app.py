from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
import os
import pandas as pd
from openpyxl import Workbook
import random

app = Flask(__name__)
app.secret_key = "secret_key"
socketio = SocketIO(app)

# Flask-Login 초기화
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# 파일 경로
EXCEL_FILE = "user_database.xlsx"
NOUNS_FILE = "Nouns.txt"

# 타이머 초기값 및 설정
initial_timer = 10  # 타이머 시작 시간 (초)
min_timer = 2       # 최소 타이머 제한
timer = initial_timer

#Nouns 파일 확인
def load_nouns():
    if not os.path.exists(NOUNS_FILE):
        raise FileNotFoundError(f"{NOUNS_FILE} 파일이 존재하지 않습니다.")
    with open(NOUNS_FILE, 'r', encoding='utf-8') as file:
        nouns = file.read().splitlines()
    if not nouns:
        raise ValueError(f"{NOUNS_FILE} 파일이 비어 있습니다. 단어 목록을 추가하세요.")
    return nouns

# 엑셀 초기화
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Users"
        ws.append(["User ID", "Password", "Score"])
        wb.save(EXCEL_FILE)

def load_users():
    try:
        return pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["User ID", "Password", "Score"])

# 사용자 모델
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Flask-Login 사용자 로딩
@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = users.iloc[int(user_id)]
    return User(id=user_data.name, username=user_data["User ID"])

# 랭킹 업데이트 함수
def get_top_rankings():
    users = load_users()
    users["Score"] = pd.to_numeric(users["Score"], errors="coerce").fillna(0)
    return users.sort_values(by="Score", ascending=False).head(3).to_dict("records")

# 게임 로직 함수들

# 사용한 단어 저장 (집합으로 변경)
USED_WORDS = set()

# 타이머 감소 로직
def update_timer():
    timer = session.get('timer', initial_timer)
    if timer > min_timer:
        timer = max(min_timer, timer * 0.95)
    session['timer'] = round(timer, 1)
    return session['timer']

# 두음법칙을 우선적으로 처리하기 위한 초성 추출 함수
def get_chosung(char):
    chosung_list = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    if char in chosung_list:
        return char
    return None

# 두음법칙을 체크하는 함수 (초성만 비교)
def allow_dueum_rule(previous_last_letter, input_first_letter):
    previous_chosung = get_chosung(previous_last_letter)
    input_chosung = get_chosung(input_first_letter)
    
    dueum_rules = {
        'ㄴ': ['ㄹ', 'ㅇ'],  # '로', '옹' → '노'
        'ㄹ': ['ㄴ', 'ㅇ'],  # '노', '옹' → '로'
    }

    if input_chosung in dueum_rules.get(previous_chosung, []):
        return True
    return False

#1 첫 글자와 마지막 글자 검사 (두음법칙 우선 적용)
def check_first_last_letter(previous_word, input_word):
    previous_last_letter = previous_word[-1]  # 이전 단어의 마지막 글자
    input_first_letter = input_word[0]       # 현재 입력 단어의 첫 글자

    # 두음법칙을 우선 적용
    if allow_dueum_rule(previous_last_letter, input_first_letter):
        return True  # 두음법칙을 우선 적용

    # 두음법칙이 적용되지 않으면 첫 글자와 마지막 글자가 일치하는지 검사
    if previous_last_letter == input_first_letter:
        return True
    else:
        print(f"첫 글자가 '{previous_last_letter}'와 일치하지 않으며 두음법칙도 적용되지 않습니다. 게임이 종료됩니다.")
        return False


# 2. 입력한 단어가 .txt 파일에 있는지 검사
def check_word_in_file(input_word):
    if not os.path.exists(NOUNS_FILE):
        print("단어 목록 파일이 존재하지 않습니다.")
        return False

    with open(NOUNS_FILE, 'r', encoding='utf-8') as file:
        words = file.read().splitlines()  # 파일에 있는 단어들을 줄 단위로 읽음

    if input_word in words:
        return True
    else:
        print(f"'{input_word}'는 유효한 단어 목록에 없습니다. 게임이 종료됩니다.")
        return False

# 3. 입력한 단어가 이미 입력한 단어가 아닌지 검사
def check_word_used(input_word):
    if input_word in USED_WORDS:
        print(f"'{input_word}'는 이미 사용한 단어입니다. 게임이 종료됩니다.")
        return False
    return True

# 4. 입력한 단어가 한 글자인지 검사
def check_word_length(input_word):
    if len(input_word) == 1:
        print("한 글자는 입력할 수 없습니다. 게임이 종료됩니다.")
        return False
    return True

# 5. 단어의 길이에 따른 점수 계산
def calculate_score(input_word):
    word_length = len(input_word)
    
    # 기본 점수: 글자 수 * 3
    score = word_length * 3

    # 4글자 이상이면 추가로 3점 부여
    if word_length >= 4:
        score += 3
    
    print(f"현재 점수: {score}")
    return score

# 게임 로직을 처리하는 함수
def game_logic(previous_word, input_word):
    # 4. 한 글자인지 확인
    if not check_word_length(input_word):
        return False, "한 글자는 입력할 수 없습니다."

    # 1. 첫 글자와 마지막 글자 검사
    if not check_first_last_letter(previous_word, input_word):
        return False, f"단어의 첫 글자는 '{previous_word[-1]}'로 시작해야 합니다."

    # 2. 단어가 .txt 파일에 있는지 검사
    if not check_word_in_file(input_word):
        return False, "단어가 목록에 없습니다."

    # 3. 단어가 이미 사용된 단어인지 검사
    if not check_word_used(input_word):
        return False, "단어가 이미 사용되었습니다."

    # 모든 조건을 만족하면 True를 반환
    return True, ""


# Flask 라우트
@app.route("/")
def index():
    # 플래시 메시지 초기화
    session.pop('_flashes', None)
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_id = request.form["user_id"].strip()
        password = request.form["password"].strip()

        users = load_users()
        if user_id in users["User ID"].values:
            flash("이미 존재하는 아이디입니다!", "danger")
            return redirect(url_for("signup"))

        new_user = pd.DataFrame([[user_id, password, 0]], columns=["User ID", "Password", "Score"])
        users = pd.concat([users, new_user], ignore_index=True)
        users.to_excel(EXCEL_FILE, index=False)

        flash("회원가입 완료!", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("game"))

    if request.method == "POST":
        user_id = request.form["user_id"].strip()
        password = request.form["password"].strip()

        users = load_users()
        user_data = users[users["User ID"] == user_id]

        if not user_data.empty and ["Password"].values[0] == password:
            user = User(id=user_data.index[0], username=user_id)
            login_user(user)
            return redirect(url_for("game"))
        else:
            flash("유효한 아이디 또는 비밀번호를 입력해주세요!", "danger")
            return redirect(url_for("login"))

    return render_template("index.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("로그아웃되었습니다!", "info")
    return redirect(url_for("index"))

# 타이머 초기화
@app.route('/start_game', methods=['POST'])
def start_game():
    global score, timer, used_words
    score = 0  # 게임 시작 시 점수 초기화
    timer = initial_timer  # 타이머 초기화
    used_words = set()  # 사용한 단어 집합 초기화

    return jsonify({
        "message": "게임이 시작되었습니다!",
        "score": score,
        "timer": timer
    })
    
@app.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    if request.method == 'POST':
        input_word = request.form['input_word'].strip()
        previous_word = session.get('previous_word', session.get('initial_word', ''))
        used_words = session.get('USED_WORDS', [])  # 기본값 빈 리스트
        score = session.get('score', 0)

        # game_logic 호출: valid와 message를 언팩
        valid, message = game_logic(previous_word, input_word)
        if not valid:
            flash(message, "game")
            return redirect('/game_over')

        # 점수와 사용한 단어 업데이트
        score += calculate_score(input_word)
        used_words.append(input_word)
        session['score'] = score
        session['previous_word'] = input_word
        session['USED_WORDS'] = used_words

        # 타이머 업데이트
        session['timer'] = update_timer()
        if session['timer'] <= 0:
            flash("시간이 초과되었습니다!", "game")
            return redirect('/game_over')

    else:
        # 게임 시작 초기화
        session['score'] = 0
        session['timer'] = initial_timer
        nouns = load_nouns()
        initial_word = random.choice(nouns)
        session['initial_word'] = initial_word
        session['previous_word'] = initial_word
        session['USED_WORDS'] = []

    return render_template('game.html',
                           previous_word=session.get('previous_word', ''),
                           score=session.get('score', 0),
                           timer=session.get('timer', initial_timer),
                           used_words=session.get('USED_WORDS', []))





@app.route("/game_over")
@login_required
def game_over():
    score = session.pop("score", 0)
    user_id = current_user.username

    users = load_users()
    user_data = users[users["User ID"] == user_id]
    if not user_data.empty:
        current_score = user_data["Score"].values[0]
        if score > current_score:
            users.loc[users["User ID"] == user_id, "Score"] = score
            users.to_excel(EXCEL_FILE, index=False)

    rankings = get_top_rankings()
    socketio.emit("update_rankings", rankings)

    return render_template("game_over.html", score=score)

@app.route("/get_rankings")
def get_rankings():
    rankings = get_top_rankings()
    return jsonify(rankings=rankings)

# SocketIO 이벤트

@socketio.on("update_request")
def handle_update_request():
    rankings = get_top_rankings()
    emit("update_rankings", rankings, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)