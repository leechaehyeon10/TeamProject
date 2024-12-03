from flask import Flask, jsonify
import os
import shutil
from datetime import datetime

app = Flask(__name__)

# 백업 설정
SOURCE_DIR = "/path/to/your/source_directory"  # 백업할 디렉터리
BACKUP_DIR = "/path/to/your/backup_directory"  # 백업이 저장될 디렉터리

# 백업 함수
def backup_files():
    try:
        # 백업 디렉터리가 없으면 생성
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        # 타임스탬프 추가
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        
        # 디렉터리 복사
        shutil.copytree(SOURCE_DIR, backup_path)
        return {"status": "success", "backup_path": backup_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 백업 API
@app.route('/backup', methods=['GET'])
def backup():
    result = backup_files()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)