from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
import os
import pandas as pd
from openpyxl import Workbook
import random

app = Flask(__name__)
app.secret_key = "secret_key"

# SocketIO 초기화: Flask 애플리케이션과 통합
socketio = SocketIO(app)

# Flask-Login 초기화
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# 파일 경로 설정
EXCEL_FILE = "user_database.xlsx"
NOUNS_FILE = "Nouns.txt"

# 타이머 관련 설정
initial_timer = 5  # 단어 제출 시마다 타이머를 5초로 재설정

# 단어 목록 로드 함수
def load_nouns():
    if not os.path.exists(NOUNS_FILE):
        raise FileNotFoundError(f"{NOUNS_FILE} 파일이 존재하지 않습니다.")
    with open(NOUNS_FILE, 'r', encoding='utf-8') as file:
        nouns = file.read().splitlines()
    if not nouns:
        raise ValueError(f"{NOUNS_FILE} 파일이 비어 있습니다. 단어 목록을 추가하세요.")
    return nouns

# 유저 데이터베이스 초기화 함수
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Users"
        ws.append(["User ID", "Password", "Score"])
        wb.save(EXCEL_FILE)

# 유저 정보 로드 함수 (엑셀에서 불러오기)
def load_users():
    try:
        df = pd.read_excel(EXCEL_FILE, dtype={"User ID": str, "Password": str, "Score": float})
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["User ID", "Password", "Score"])

# Flask-Login에서 사용할 User 모델
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Flask-Login에서 유저를 로드하는 함수
@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = users[users["User ID"] == user_id]
    if not user_data.empty:
        return User(id=user_id, username=user_data["User ID"].values[0])
    return None

# 상위 랭킹 불러오기 함수
def get_top_rankings():
    users = load_users()
    users["Score"] = pd.to_numeric(users["Score"], errors="coerce").fillna(0)
    return users.sort_values(by="Score", ascending=False).head(3).to_dict("records")


# -----게임 로직 함수들-----

# 1. 입력한 단어의 첫 글자가 주어진 단어의 마지막 글자와 같은지 검사
def check_first_last_letter(previous_word, input_word):
    previous_last_letter = previous_word[-1]  # 이전 단어의 마지막 글자
    input_first_letter = input_word[0]       # 현재 입력 단어의 첫 글자
    
    if previous_last_letter == input_first_letter:
        return True
    else:
        print(f"첫 글자가 '{previous_last_letter}'와 일치하지 않습니다. 게임이 종료됩니다.")
        return False

# 2. 단어 목록에 있는지 확인
def check_word_in_file(input_word):
    if not os.path.exists(NOUNS_FILE):
        print("단어 목록 파일이 존재하지 않습니다.")
        return False
    with open(NOUNS_FILE, 'r', encoding='utf-8') as file:
        words = file.read().splitlines()
    if input_word in words:
        return True
    print(f"'{input_word}'는 유효한 단어 목록에 없습니다. 게임 종료.")
    return False

# 3. 이미 사용한 단어인지 확인
def check_word_used(used_words, input_word):
    if input_word in used_words:
        print(f"'{input_word}'는 이미 사용한 단어입니다. 게임 종료.")
        return False
    return True

# 4. 단어 길이 체크 (1글자 불가)
def check_word_length(input_word):
    if len(input_word) == 1:
        print("한 글자는 입력할 수 없습니다. 게임 종료.")
        return False
    return True

# 5. 점수 계산 로직 (글자 수 * 3, 4글자 이상 +3점)
def calculate_score(input_word):
    word_length = len(input_word)
    score = word_length * 3
    if word_length >= 4:
        score += 3
    print(f"현재 점수: {score}")
    return score

# 게임 로직 통합 함수
def game_logic(previous_word, input_word, used_words):
    if not check_word_length(input_word):
        return False, "한 글자는 입력할 수 없습니다."

    if not check_first_last_letter(previous_word, input_word):
        return False, f"단어의 첫 글자는 '{previous_word[-1]}'로 시작해야 합니다."

    if not check_word_in_file(input_word):
        return False, "단어가 목록에 없습니다."

    if not check_word_used(used_words, input_word):
        return False, "단어가 이미 사용되었습니다."

    return True, ""

# 사용자별 게임 상태 저장용 딕셔너리
# key: user_id, value: {score, timer, used_words, initial_word, previous_word}
game_states = {}

@app.route("/")
def index():
    # 플래시 메시지 초기화
    session.pop('_flashes', None)
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # 회원가입 로직
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
    # 로그인 로직
    if current_user.is_authenticated:
        return redirect(url_for("game"))

    if request.method == "POST":
        user_id = request.form["user_id"].strip()
        password = request.form["password"].strip()

        users = load_users()
        user_data = users[users["User ID"] == user_id]

        if not user_data.empty and user_data["Password"].values[0] == password:
            # 로그인 성공 시 user 로드
            user = User(id=user_id, username=user_id)
            login_user(user)
            return redirect(url_for("game"))
        else:
            flash("유효한 아이디 또는 비밀번호를 입력해주세요!", "danger")
            return redirect(url_for("login"))

    return render_template("index.html")

@app.route("/logout")
@login_required
def logout():
    # 로그아웃 시 해당 유저의 게임 상태 제거
    user_id = current_user.username
    if user_id in game_states:
        del game_states[user_id]
    logout_user()
    flash("로그아웃되었습니다!", "info")
    return redirect(url_for("index"))

@app.route('/start_game', methods=['POST'])
def start_game():
    # 게임 시작 API 예시
    if not current_user.is_authenticated:
        return jsonify({"message": "로그인이 필요합니다."}), 403

    user_id = current_user.username
    nouns = load_nouns()
    initial_word = random.choice(nouns)
    game_states[user_id] = {
        'score': 0,
        'timer': initial_timer,
        'used_words': [],
        'initial_word': initial_word,
        'previous_word': initial_word
    }

    return jsonify({
        "message": "게임이 시작되었습니다!",
        "score": game_states[user_id]['score'],
        "timer": game_states[user_id]['timer']
    })

@app.route('/game', methods=['GET'])
@login_required
def game():
    # 게임 페이지 진입 시 초기 상태 설정
    user_id = current_user.username
    nouns = load_nouns()
    initial_word = random.choice(nouns)
    game_states[user_id] = {
        'score': 0,
        'timer': initial_timer,
        'used_words': [],
        'initial_word': initial_word,
        'previous_word': initial_word
    }

    # 템플릿에 timer를 int로 전달하여 {{ timer }}가 정상적으로 숫자로 렌더링되게 함
    return render_template('game.html',
                       previous_word=game_states[user_id]['previous_word'],
                       score=game_states[user_id]['score'],
                       timer=int(game_states[user_id]['timer']),
                       used_words=game_states[user_id]['used_words'])

@app.route("/game_over")
@login_required
def game_over():
    # 게임 종료 처리
    user_id = current_user.username
    state = game_states.get(user_id, {})
    score = state.get('score', 0)

    # 기존 점수보다 높으면 엑셀에 업데이트
    users = load_users()
    user_data = users[users["User ID"] == user_id]
    if not user_data.empty:
        current_score = user_data["Score"].values[0]
        if score > current_score:
            users.loc[users["User ID"] == user_id, "Score"] = score
            users.to_excel(EXCEL_FILE, index=False)

    # 랭킹 업데이트 이벤트 전송
    rankings = get_top_rankings()
    socketio.emit("update_rankings", rankings)

    # 게임 상태 제거
    if user_id in game_states:
        del game_states[user_id]

    return render_template("game_over.html", score=score)

@app.route("/get_rankings")
def get_rankings():
    # 상위 3명 랭킹 반환
    rankings = get_top_rankings()
    return jsonify(rankings=rankings)

@socketio.on('word_submitted')
def handle_word_submitted(data):
    # 소켓 이벤트: 단어 제출 처리
    if not current_user.is_authenticated:
        emit('game_over', {'message': "로그인이 필요합니다."})
        return

    user_id = current_user.username
    state = game_states.get(user_id, None)

    if state is None:
        emit('game_over', {'message': "게임 상태가 없습니다. 새로 시작해주세요."})
        return

    input_word = data.get('word', '').strip()
    previous_word = state['previous_word']
    used_words = state['used_words']
    score = state['score']

    # 게임 로직 검증
    valid, message = game_logic(previous_word, input_word, used_words)
    if not valid:
        emit('game_over', {'message': message})
        return

    # 점수 업데이트
    gained_score = calculate_score(input_word)
    score += gained_score
    used_words.append(input_word)

    # 상태 반영
    state['score'] = score
    state['previous_word'] = input_word

    # 단어 제출 후 타이머를 5초로 재설정
    state['timer'] = 5
    # 클라이언트에 상태 업데이트
    emit('score_update', {'score': score})
    emit('word_list_update', {'used_words': used_words})
    emit('timer_update', {'timer': 5})
    emit('previous_word_update', {'previous_word': input_word})

@socketio.on('time_up')
def handle_time_up():
    # 클라이언트에서 타이머 0초 알림 수신 시 게임 종료
    if not current_user.is_authenticated:
        return
    user_id = current_user.username
    emit('game_over', {'message': "시간이 초과되었습니다!"})

@socketio.on("update_request")
def handle_update_request():
    # 클라이언트 요청 시 랭킹 업데이트 방송
    rankings = get_top_rankings()
    emit("update_rankings", rankings, broadcast=True)

if __name__ == '__main__':
    init_excel()
    socketio.run(app, host='0.0.0.0', debug=True)
