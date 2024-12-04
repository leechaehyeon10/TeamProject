from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 점수 및 Best_Score 초기화
score = 0
best_score = 0  # 게임이 종료되었을 때 저장할 최고 점수

# 단어 목록이 저장된 파일 경로
word_file = "Nouns.txt"

# 1. 입력한 단어의 첫 글자가 주어진 단어의 마지막 글자와 같은지 검사
def check_first_last_letter(previous_word, input_word):
    if previous_word[-1] == input_word[0]:
        return True
    else:
        print(f"첫 글자가 '{previous_word[-1]}'와 일치하지 않습니다. 게임이 종료됩니다.")
        return False

# 2. 입력한 단어가 .txt 파일에 있는지 검사
def check_word_in_file(input_word):
    if not os.path.exists(word_file):
        print("단어 목록 파일이 존재하지 않습니다.")
        return False

    with open(word_file, 'r', encoding='utf-8') as file:
        words = file.read().splitlines()  # 파일에 있는 단어들을 줄 단위로 읽음

    if input_word in words:
        return True
    else:
        print(f"'{input_word}'는 유효한 단어 목록에 없습니다. 게임이 종료됩니다.")
        return False

# 3. 입력한 단어가 이미 입력한 단어가 아닌지 검사
def check_word_used(input_word, used_words):
    if input_word in used_words:
        print(f"'{input_word}'는 이미 사용한 단어입니다. 게임이 종료됩니다.")
        return False
    else:
        return True

# 4. 입력한 단어가 한 글자인지 검사
def check_word_length(input_word):
    if len(input_word) == 1:
        print("한 글자는 입력할 수 없습니다. 게임이 종료됩니다.")
        return False
    return True

# 5. 단어의 길이에 따른 점수 계산
def calculate_score(input_word):
    global score
    word_length = len(input_word)
    
    # 기본 점수: 글자 수 * 3
    score += word_length * 3

    # 4글자 이상이면 추가로 3점 부여
    if word_length >= 4:
        score += 3
    
    print(f"현재 점수: {score}")
    return score

# 게임 로직을 처리하는 함수
def game_logic(previous_word, input_word, used_words):
    # 4. 한 글자인지 확인
    if not check_word_length(input_word):
        return False  # 게임 종료

    # 1. 첫 글자와 마지막 글자 검사
    if not check_first_last_letter(previous_word, input_word):
        return False  # 게임 종료

    # 2. 단어가 .txt 파일에 있는지 검사
    if not check_word_in_file(input_word):
        return False  # 게임 종료

    # 3. 단어가 이미 사용된 단어인지 검사
    if not check_word_used(input_word, used_words):
        return False  # 게임 종료

    # 5. 점수 계산
    calculate_score(input_word)

    # 모든 조건을 만족하면 단어를 사용한 것으로 간주하고 목록에 추가
    used_words.append(input_word)
    print(f"'{input_word}'가 유효한 단어입니다. 게임을 계속합니다!")
    return True

@app.route('/start_game', methods=['POST'])
def start_game():
    global score
    score = 0  # 게임 시작 시 점수 초기화
    used_words = []  # 게임 시작 시마다 초기화
    previous_word = "사과"  # 게임 시작 시 첫 번째 단어 예시

    return jsonify({"message": "게임이 시작되었습니다!", "score": score, "previous_word": previous_word})


@app.route('/play_game', methods=['POST'])
def play_game():
    global score, best_score
    data = request.get_json()
    input_word = data.get('input_word')
    previous_word = data.get('previous_word')
    used_words = data.get('used_words', [])

    # 게임 진행
    if not game_logic(previous_word, input_word, used_words):
        # 게임 종료 후 최고 점수 비교 및 저장
        if score > best_score:
            best_score = score  # 최고 점수 갱신
        return jsonify({
            "message": f"게임이 종료되었습니다. 최종 점수: {score}, 최고 점수: {best_score}",
            "score": score,
            "best_score": best_score
        })

    return jsonify({
        "message": f"'{input_word}'가 유효한 단어입니다. 게임을 계속합니다!",
        "score": score,
        "previous_word": input_word,
        "used_words": used_words
    })

if __name__ == "__main__":
    app.run(debug=True)
