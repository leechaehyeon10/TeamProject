Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
from flask import Flask, render_template, request, jsonify
import random
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = 'users_data.xlsx'  # 엑셀 파일 경로

# User 클래스 정의
class User:
    def __init__(self, username):
        self.username = username
        self.games_played = 0
        self.successful_games = 0
        self.score = 0

    def add_game_result(self, success, points):
        self.games_played += 1
        if success:
            self.successful_games += 1
        self.score += points

# RankingSystem 클래스 정의
class RankingSystem:
    def __init__(self):
        self.users = {}

    def add_user(self, username):
        if username not in self.users:
            self.users[username] = User(username)

    def update_user_score(self, username, success, points):
        user = self.users.get(username)
        if user:
            user.add_game_result(success, points)

    def get_sorted_ranking(self):
        return sorted(self.users.values(), key=lambda user: (-user.score, -user.games_played))

    def save_to_excel(self):
        data = []
        for user in self.users.values():
            data.append([user.username, user.games_played, user.successful_games, user.score])
        df = pd.DataFrame(data, columns=['Username', 'Games Played', 'Successful Games', 'Score'])
        df.to_excel(EXCEL_FILE, index=False)

    def load_from_excel(self):
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            for _, row in df.iterrows():
                user = User(row['Username'])
                user.games_played = row['Games Played']
                user.successful_games = row['Successful Games']
                user.score = row['Score']
                self.users[user.username] = user

    def play_multiple_games(self, user1_name, user2_name, game_count):
        """게임 횟수만큼 게임을 실행하고 점수 업데이트"""
        total_success1, total_points1 = 0, 0
        total_success2, total_points2 = 0, 0

        # 게임 횟수만큼 반복
        for _ in range(game_count):
            game = Game(user1_name, user2_name)
            success1, points1, success2, points2 = game.play()

            total_success1 += success1
            total_points1 += points1
            total_success2 += success2
            total_points2 += points2

            # 각 게임의 결과를 업데이트
            self.update_user_score(user1_name, success1, points1)
            self.update_user_score(user2_name, success2, points2)

        # 최종 점수 저장
        self.save_to_excel()

        return {
            user1_name: {'games_played': game_count, 'success': total_success1, 'score': total_points1},
            user2_name: {'games_played': game_count, 'success': total_success2, 'score': total_points2},
        }

# Game 클래스 정의
class Game:
    def __init__(self, user1, user2):
        self.user1 = user1
        self.user2 = user2

    def play(self):
        success1 = random.choice([True, False])
        success2 = random.choice([True, False])
        points1 = random.randint(1, 100) if success1 else 0
        points2 = random.randint(1, 100) if success2 else 0
        return (success1, points1, success2, points2)
... 
... 
... # 인스턴스 생성
... ranking_system = RankingSystem()
... ranking_system.load_from_excel()
... 
... # 홈 페이지
... @app.route('/')
... def index():
...     ranking_list = ranking_system.get_sorted_ranking()
...     return render_template('index.html', ranking_list=ranking_list)
... 
... # 게임 실행
... @app.route('/game', methods=['POST'])
... def game():
...     user1_name = request.form['user1']
...     user2_name = request.form['user2']
...     game_count = int(request.form['game_count'])  # 게임 횟수 받아오기
...     
...     # 사용자 추가 (이미 존재할 수 있기 때문에 add_user로 처리)
...     ranking_system.add_user(user1_name)
...     ranking_system.add_user(user2_name)
... 
...     # 여러 게임을 처리하는 메서드 호출
...     result = ranking_system.play_multiple_games(user1_name, user2_name, game_count)
...     
...     return jsonify(result)
... 
... # 랭킹 조회
... @app.route('/get_ranking', methods=['GET'])
... def get_ranking():
...     ranking_list = ranking_system.get_sorted_ranking()
...     result = [{'username': user.username, 'score': user.score, 'games_played': user.games_played} for user in ranking_list]
...     return jsonify(result)
... 
... # 서버 실행
... if __name__ == '__main__':
