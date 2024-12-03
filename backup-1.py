def backup_files():
    try:
        # 로그: 백업 시작
        print(f"Starting backup: Source={SOURCE_DIR}, Backup={BACKUP_DIR}")

        # 소스 디렉토리 확인
        if not os.path.exists(SOURCE_DIR):
            return {"status": "error", "message": f"Source directory does not exist: {SOURCE_DIR}"}

        # 백업 디렉토리가 없으면 생성
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            print(f"Created backup directory: {BACKUP_DIR}")

        # 타임스탬프와 고유 ID 추가
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}_{unique_id}")

        # 디렉터리 복사
        shutil.copytree(SOURCE_DIR, backup_path)

        # 파일과 디렉토리 개수 계산
        file_count = sum(len(files) for _, _, files in os.walk(backup_path))
        dir_count = sum(len(dirs) for _, dirs, _ in os.walk(backup_path))

        print(f"Backup completed successfully: {backup_path}")
        return {
            "status": "success",
            "backup_path": backup_path,
            "file_count": file_count,
            "directory_count": dir_count
        }
    except Exception as e:
        print(f"Backup failed: {str(e)}")
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"} 