# 끝말잇기 게임 프로젝트

## 프로젝트 개요
* **끝말잇기 게임은 Flask를 기반으로 제작된 웹 애플리케이션**
* **회원가입, 로그인 후 게임 참여 가능**
* **실시간으로 점수가 계산되며 상위 랭킹 확인 가능**

### 주요 기능
* **회원가입 및 로그인 가능**
* **끝말잇기 게임 진행**
  * **단어의 첫 글자와 이전 단어의 마지막 글자가 일치해야 함**
  * **단어 목록에 없는 단어는 사용 불가**
  * **1글자 단어는 허용되지 않음**
* **실시간 타이머로 게임 진행**
* **상위 3명의 랭킹 확인 가능**

### 프로젝트 구조
```
flask_project/
├── app.py                  # 라우터
├── user_database.xlsx      # 유저 데이터베이스
├── backup_log.xlsx         # 백업 로그
├── Nouns.txt               # 단어 목록
├── templates/              # HTML 템플릿 폴더
│   ├── game.html           # 게임 화면
│   ├── game_over.html      # 게임 종료 화면
│   ├── index.html          # 로그인 및 메인 화면
│   └── signup.html         # 회원가입 화면
├── static/                 # 정적 파일 폴더
│   ├── style.css           # CSS 파일
│   └── images/             # 이미지 파일 폴더
│       ├── game_over.png   # 게임 종료 이미지
│       └── title_image.png # 타이틀 이미지
```

---

## 설치 및 실행 방법

### 1. 의존성 설치
* **필요한 Python 패키지를 설치함:**
```bash
pip install flask flask-login flask-socketio pandas openpyxl
```

### 2. 프로젝트 실행
* **Flask 애플리케이션 실행:**
```bash
python app.py
```

### 3. 웹 브라우저에서 접속
* **로컬 환경에서 접속:**
```
http://127.0.0.1:5000
```

### 4. GCP 배포 링크
* **배포된 링크로 바로 접속 가능:**
```
[끝말잇기 게임 GCP 링크](https://your-gcp-deployment-link.com)
```

---

## 주요 파일 설명

### `app.py`
* **Flask 애플리케이션의 메인 라우터 역할**
* **회원가입, 로그인, 끝말잇기 게임 로직 포함**
* **SocketIO를 활용해 실시간 점수 업데이트 및 타이머 동기화**

### `user_database.xlsx`
* **유저 정보 저장**
* **`User ID`, `Password`, `Score` 관리**

### `backup_log.xlsx`
* **유저 데이터베이스의 백업 로그를 기록**

### `Nouns.txt`
* **끝말잇기에서 사용되는 단어 목록**
* **줄바꿈으로 단어 구분**

### `templates/`
* **HTML 템플릿 저장**
  * `index.html`: 로그인 화면
  * `signup.html`: 회원가입 화면
  * `game.html`: 게임 진행 화면
  * `game_over.html`: 게임 종료 화면

### `static/`
* **CSS 및 이미지 파일 저장**
  * `style.css`: 스타일링 파일
  * `images/`: 이미지 파일 (타이틀, 게임 종료 등)

---
