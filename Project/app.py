from flask import Flask, render_template, request
import os
import pandas as pd
from openpyxl import Workbook

app = Flask(__name__)

# 메인 화면
@app.route('/')
def index():
    return render_template('index.html')

# 게임 화면
@app.route('/game')
def game():
    return render_template('game.html')

# 게임 종료 화면
@app.route('/game_over', methods=['GET'])
def game_over():
    score = request.args.get('score', 0)  # GET 요청으로 점수를 받음
    return render_template('game_over.html', score=score)

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

# 랭킹 데이터 조회 API
@app.route('/get_rankings')
def get_rankings():
    # 엑셀 파일 로드
    if not os.path.exists(EXCEL_FILE):
        return {"rankings": []}  # 엑셀 파일이 없으면 빈 리스트 반환

    df = pd.read_excel(EXCEL_FILE)
    if df.empty:
        return {"rankings": []}  # 데이터가 없으면 빈 리스트 반환

    # 점수 기준으로 정렬하여 상위 3명 반환
    top_rankings = df.sort_values(by="Score", ascending=False).head(3).to_dict("records")
    return {"rankings": top_rankings}

# 앱 시작 시 엑셀 초기화
init_excel()

# 기존 코드 유지
if __name__ == "__main__":
    app.run(debug=True)