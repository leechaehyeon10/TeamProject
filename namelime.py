from openpyxl import Workbook
import os

# ���� ���� ���� �Լ�
def create_excel_file(file_name):
    # ���� ������ �̹� �����ϸ� ������ �ǳʶݴϴ�.
    if os.path.exists(file_name):
        print(f"{file_name} ������ �̹� �����մϴ�.")
        return

    # ���ο� ���� ��ũ�� ����
    wb = Workbook()
    ws = wb.active

    # ��� �߰�
    ws.append(["�г���", "���̵�", "��й�ȣ", "�ְ� ���"])

    # ���� ����
    wb.save(file_name)
    print(f"{file_name} ������ �����߽��ϴ�.")

# ����� ������ ������ �߰��ϴ� �Լ�
def add_user_to_excel(file_name, nickname, user_id, password, high_score):
    if not os.path.exists(file_name):
        print(f"{file_name} ������ �����ϴ�. ���� ������ �����ϼ���.")
        return

    # ���� ���� ����
    from openpyxl import load_workbook
    wb = load_workbook(file_name)
    ws = wb.active

    print(f"���� {file_name}�� �������ϴ�. ������ �߰� ��...")

    # ������ �߰�
    ws.append([nickname, user_id, password, high_score])

    # ���� ����
    wb.save(file_name)
    print(f"����� ���� [{nickname}, {user_id}, {high_score}]�� �߰��Ǿ����ϴ�.")

# ������ �׽�Ʈ �ڵ�
file_name = "user_data.xlsx"

try:
    # ���� ���� ����
    create_excel_file(file_name)

    # ����� ���� �߰�
    add_user_to_excel(file_name, "�г���1", "user1", "password123", 5000)
    add_user_to_excel(file_name, "�г���2", "user2", "mypassword", 8500)
    add_user_to_excel(file_name, "�г���3", "user3", "securepass", 10000)

except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError �߻�: {e}")
except Exception as e:
    print(f"�� �� ���� ���� �߻�: {e}")
