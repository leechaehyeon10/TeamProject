from flask import Flask, render_template, request, redirect, flash, session
import os
import pandas as pd
from openpyxl import Workbook

app = Flask(__name__)
app.secret_key = "secret_key"  # 세션에 필요

# 엑셀 파일 경로
EXCEL_FILE = "user_database.xlsx"

# 엑셀 파일 초기화
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active
        ws.title = "Users"
        ws.append(["User ID", "Password", "Score"])  # 헤더 생성
        wb.save(EXCEL_FILE)

# 메인 화면
@app.route('/')
def index():
    return render_template('index.html')

# 회원가입
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form['user_id'].strip()
        password = request.form['password'].strip()

        df = pd.read_excel(EXCEL_FILE)
        if user_id in df["User ID"].values:
            flash("이미 존재하는 아이디입니다!")  # 중복 메시지 추가 방지
            return redirect('/signup')

        new_user = {"User ID": user_id, "Password": password, "Score": 0}
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)

        flash("회원가입 완료!")  # 성공 메시지를 한 번만 추가
        return redirect('/')
    return render_template('signup.html')


# 로그인
@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id'].strip()
    password = request.form['password'].strip()

    df = pd.read_excel(EXCEL_FILE)
    user = df[df["User ID"] == user_id]

    if not user.empty and str(user.iloc[0]["Password"]).strip() == password:
        # 로그인 성공
        session['user_id'] = user_id
        return redirect('/game')
    else:
        # 로그인 실패
        flash("유효한 값을 입력해주세요!")  # 메시지를 한 번만 추가
        return redirect('/')


# 게임 화면
@app.route('/game')
def game():
    if 'user_id' not in session:
        flash("로그인 후 이용해주세요!")
        return redirect('/')
    return render_template('game.html')

# 게임 종료 화면
@app.route('/game_over', methods=['GET'])
def game_over():
    if 'user_id' not in session:
        flash("로그인 후 이용해주세요!")
        return redirect('/')

    score = int(request.args.get('score', 0))
    user_id = session['user_id']

    # 엑셀 파일 로드
    df = pd.read_excel(EXCEL_FILE)

    # 유저 데이터 가져오기
    user_row = df[df["User ID"] == user_id]
    if not user_row.empty:
        current_score = user_row.iloc[0]["Score"]

        # 새 점수가 기존 점수보다 클 경우에만 업데이트
        if score > current_score:
            df.loc[df["User ID"] == user_id, "Score"] = score
            df.to_excel(EXCEL_FILE, index=False)

    return render_template('game_over.html', score=score)


# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# 랭킹 데이터 조회 API
@app.route('/get_rankings')
def get_rankings():
    if not os.path.exists(EXCEL_FILE):
        return {"rankings": []}

    df = pd.read_excel(EXCEL_FILE)
    try:
        df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    except Exception as e:
        print(f"Score 필드 처리 중 오류 발생: {e}")
        return {"rankings": []}

    df = df.dropna(subset=["Score"])
    top_rankings = df.sort_values(by="Score", ascending=False).head(3).to_dict("records")
    return {"rankings": top_rankings}

# 앱 시작 시 엑셀 초기화
init_excel()

if __name__ == "__main__":
    app.run(debug=True)
