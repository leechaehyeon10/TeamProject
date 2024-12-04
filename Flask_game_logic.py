import os

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

# 게임 로직을 처리하는 함수
def game_logic(previous_word, input_word, used_words):
    # 1. 첫 글자와 마지막 글자 검사
    if not check_first_last_letter(previous_word, input_word):
        return False  # 게임 종료

    # 2. 단어가 .txt 파일에 있는지 검사
    if not check_word_in_file(input_word):
        return False  # 게임 종료

    # 3. 단어가 이미 사용된 단어인지 검사
    if not check_word_used(input_word, used_words):
        return False  # 게임 종료

    # 모든 조건을 만족하면 단어를 사용한 것으로 간주하고 목록에 추가
    used_words.append(input_word)
    print(f"'{input_word}'가 유효한 단어입니다. 게임을 계속합니다!")
    return True

# 디버깅용 테스트 코드
if __name__ == "__main__":
    while True:
        # 사용된 단어 목록 초기화
        used_words = []  # 게임 시작 시마다 초기화
        previous_word = "사과"  # 이전 단어 예시
        
        print("끝말잇기 게임을 시작합니다!")
        
        while True:
            input_word = input("끝말잇기 단어를 입력하세요: ")  # 사용자가 입력하는 단어

            # 게임 진행
            if not game_logic(previous_word, input_word, used_words):
                print("게임이 종료되었습니다.")
                break  # 조건이 실패하면 게임 종료

            previous_word = input_word  # 이전 단어를 업데이트하여 다음 단어 입력 대기
