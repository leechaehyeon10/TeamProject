from openpyxl import Workbook
import os

# 엑셀 파일 생성 함수
def create_excel_file(file_name):
    # 엑셀 파일이 이미 존재하면 생성을 건너뜁니다.
    if os.path.exists(file_name):
        print(f"{file_name} 파일이 이미 존재합니다.")
        return

    # 새로운 엑셀 워크북 생성
    wb = Workbook()
    ws = wb.active

    # 헤더 추가
    ws.append(["닉네임", "아이디", "비밀번호", "최고 기록"])

    # 파일 저장
    wb.save(file_name)
    print(f"{file_name} 파일을 생성했습니다.")

# 사용자 정보를 엑셀에 추가하는 함수
def add_user_to_excel(file_name, nickname, user_id, password, high_score):
    if not os.path.exists(file_name):
        print(f"{file_name} 파일이 없습니다. 먼저 파일을 생성하세요.")
        return

    # 엑셀 파일 열기
    from openpyxl import load_workbook
    wb = load_workbook(file_name)
    ws = wb.active

    print(f"파일 {file_name}을 열었습니다. 데이터 추가 중...")

    # 데이터 추가
    ws.append([nickname, user_id, password, high_score])

    # 파일 저장
    wb.save(file_name)
    print(f"사용자 정보 [{nickname}, {user_id}, {high_score}]가 추가되었습니다.")

# 디버깅용 테스트 코드
file_name = "user_data.xlsx"

try:
    # 엑셀 파일 생성
    create_excel_file(file_name)

    # 사용자 정보 추가
    add_user_to_excel(file_name, "닉네임1", "user1", "password123", 5000)
    add_user_to_excel(file_name, "닉네임2", "user2", "mypassword", 8500)
    add_user_to_excel(file_name, "닉네임3", "user3", "securepass", 10000)

except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError 발생: {e}")
except Exception as e:
    print(f"알 수 없는 에러 발생: {e}")
