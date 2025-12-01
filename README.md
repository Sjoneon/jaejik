# 📅 Work Schedule Management System
# 업무 일정 관리 시스템

> AI가 문서에서 자동으로 일정을 추출하여 캘린더에 등록해주는 팀 협업 일정 관리 시스템

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Overview

업무 문서(HWP, PDF, Excel 등)를 업로드하면 **AI(Groq API)**가 마감일, 회의, 출장 등의 일정을 자동으로 추출하여 캘린더에 등록해주는 웹 애플리케이션입니다.

---

## ✨ Features

### 🤖 AI 일정 추출
- Groq API 사용 (Qwen3-32B 모델)
- 문서에서 날짜, 마감일, 회의 등 자동 인식
- 규칙 기반 추출 백업 시스템

### 📄 다양한 문서 지원
- 한글 문서 (HWP, HWPX)
- MS Word (DOCX, DOC)
- PDF 문서
- Excel 스프레드시트 (XLSX, XLS)
- CSV 파일

### 📆 캘린더 관리
- FullCalendar 기반 인터랙티브 캘린더
- 월간/주간/일간 뷰 지원
- 드래그 앤 드롭 일정 수정
- 시간 단위 일정 관리 (06:00~22:00)

### 👥 팀 협업
- 회사/팀 2단계 조직 구조
- 팀원 일정 공유 및 조회
- 사용자 인증 시스템

---

## 📁 Supported File Formats

| 확장자 | 설명 | 비고 |
|--------|------|------|
| `.hwp` | 한글 문서 | 한글 97 이상 |
| `.hwpx` | 한글 문서 (XML) | 한글 2014 이상 |
| `.docx` | MS Word | Office 2007 이상 |
| `.doc` | MS Word (레거시) | Office 97-2003 |
| `.pdf` | PDF 문서 | 텍스트 기반 |
| `.xlsx` | Excel 스프레드시트 | Office 2007 이상 |
| `.xls` | Excel (레거시) | Office 97-2003 |
| `.csv` | CSV 파일 | UTF-8, CP949, EUC-KR |

---

## 🛠️ Tech Stack

| 분류 | 기술 |
|------|------|
| **Backend** | Flask 3.0, SQLAlchemy, Flask-Login |
| **Database** | SQLite |
| **AI Model** | Groq API (Qwen3-32B) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Calendar** | FullCalendar 6.x |
| **Document Parsing** | python-docx, pdfplumber, olefile, openpyxl |

---

## 📂 Project Structure

```
인공지능산업협회AI/
├── app.py                 # Flask 메인 애플리케이션
├── config.py              # 설정 파일
├── requirements.txt       # 의존성 패키지
├── migrate_db.py          # DB 마이그레이션
│
├── models/                # 데이터베이스 모델
│   ├── user.py            # 사용자 모델
│   ├── schedule.py        # 일정 모델
│   ├── document.py        # 문서 모델
│   ├── company.py         # 회사 모델
│   └── team.py            # 팀 모델
│
├── services/              # 비즈니스 로직
│   ├── ai_extractor.py    # AI 일정 추출
│   ├── document_parser.py # 문서 파싱
│   ├── auth.py            # 인증 서비스
│   └── company_service.py # 조직 관리
│
├── templates/             # HTML 템플릿
│   ├── base.html          # 기본 레이아웃
│   ├── dashboard.html     # 대시보드 (캘린더)
│   ├── login.html         # 로그인
│   ├── register.html      # 회원가입
│   ├── files.html         # 파일 관리
│   └── company.html       # 조직 관리
│
├── static/                # 정적 파일
│   ├── css/style.css
│   └── js/main.js
│
├── groq/                  # Groq API 테스트
│   └── test_groq_qwen3.py
│
├── database/              # SQLite DB
│   └── app.db
│
└── uploads/               # 업로드된 파일
```

---

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/Sjoneon/인공지능산업협회AI.git
cd 인공지능산업협회AI
```

### 2. Create Virtual Environment
```bash
python -m venv env

# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
`.env` 파일을 생성하고 Groq API 키를 설정하세요:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run Application
```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

---

## 📖 Usage

### 1️⃣ 회원가입 & 로그인
- 이메일, 비밀번호로 계정 생성
- 회사/팀 선택 또는 생성

### 2️⃣ 문서 업로드
- 대시보드에서 "파일 업로드" 클릭
- HWP, PDF, Excel 등 문서 선택
- AI가 자동으로 일정 추출

### 3️⃣ 일정 확인 & 수정
- 캘린더에서 추출된 일정 확인
- 클릭하여 상세 정보 수정
- 드래그로 날짜 변경

### 4️⃣ 팀원 일정 공유
- 같은 팀 멤버 일정 조회
- 조직 관리 페이지에서 팀 설정

---

## ⚙️ Configuration

### 환경 변수 (.env)
```env
# Groq API
GROQ_API_KEY=your_groq_api_key_here

# Flask (선택사항)
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
```

### config.py 주요 설정
```python
# 업로드 파일 크기 제한
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 지원 확장자
ALLOWED_EXTENSIONS = {'hwp', 'hwpx', 'docx', 'doc', 'pdf', 'xlsx', 'xls', 'csv'}
```

---

## 🤖 AI Schedule Extraction

### 동작 방식
```
문서 업로드 → 텍스트 추출 → Groq AI 분석 → 일정 추출 → 캘린더 등록
                              ↓
                    (AI 실패시 규칙 기반 백업)
```

### 추출 가능한 일정 유형
| 유형 | 키워드 예시 |
|------|-------------|
| 📅 마감 (deadline) | 마감, 기한, ~까지, due |
| 📤 제출 (submit) | 제출, 보고, 발송 |
| 👥 회의 (meeting) | 회의, 미팅, 간담회 |
| 🚗 출장 (trip) | 출장, 방문, 외근 |

### 인식 가능한 날짜 형식
- `2025년 12월 5일`
- `2025.12.05` / `2025-12-05`
- `12월 5일` (올해로 가정)
- `12/5`

---

## 📝 License

MIT License

---

## 👨‍💻 Author

**Sjoneon**

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - AI API
- [FullCalendar](https://fullcalendar.io/) - Calendar UI
- [Flask](https://flask.palletsprojects.com/) - Web Framework
