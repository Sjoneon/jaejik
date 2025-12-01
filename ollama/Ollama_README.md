# Ollama 사용 가이드

## 목차
- [Ollama란?](#ollama란)
- [설치 방법](#설치-방법)
  - [Windows PATH 설정 문제 해결](#️-windows에서-ollama-명령을-찾을-수-없습니다-오류-해결)
- [기본 사용법](#기본-사용법)
- [Python API 사용](#python-api-사용)
- [주요 명령어](#주요-명령어)
- [API 레퍼런스](#api-레퍼런스)
- [성능 최적화](#성능-최적화)
- [트러블슈팅](#트러블슈팅)

---

## Ollama란?

**Ollama**는 로컬에서 LLM(대규모 언어 모델)을 쉽게 실행할 수 있게 해주는 오픈소스 도구입니다.

### 주요 특징
- 🚀 **간편한 설치**: 한 줄 명령으로 모델 다운로드 및 실행
- 💻 **로컬 실행**: 인터넷 연결 없이도 사용 가능
- 🔒 **프라이버시**: 데이터가 외부로 전송되지 않음
- 🎯 **다양한 모델**: Llama, Gemma, Mistral, Qwen 등 지원
- 🌐 **REST API**: HTTP API로 다양한 언어에서 활용 가능

### 지원 모델 (2025년 기준)
- **Gemma 3** (1B, 2B, 7B)
- **Llama 3.3** (1B, 3B, 70B)
- **Qwen 2.5** (0.5B~72B)
- **Mistral** (7B)
- **DeepSeek** (1.3B, 7B)
- 기타 100+ 모델

---

## 설치 방법

### Windows
```bash
# 1. Ollama 다운로드 및 설치
# https://ollama.com/download 에서 Windows 설치 파일 다운로드

# 2. 설치 후 터미널에서 확인
ollama --version
```

#### ⚠️ Windows에서 "ollama 명령을 찾을 수 없습니다" 오류 해결

설치 후 터미널에서 `ollama` 명령어가 인식되지 않는 경우가 있습니다. 이는 PATH 환경 변수에 Ollama가 등록되지 않았기 때문입니다.

**1단계: Ollama 설치 위치 확인**

일반적으로 다음 위치에 설치됩니다:
```
C:\Users\사용자명\AppData\Local\Programs\Ollama
```

확인 방법:
```cmd
# CMD에서 실행
dir "%LOCALAPPDATA%\Programs\Ollama"
```

**2단계: PATH 환경 변수에 추가 (영구적 해결)**

방법 A - GUI로 설정 (권장):
1. `Win + R` 키를 누르고 `sysdm.cpl` 입력 후 엔터
2. **고급** 탭 → **환경 변수** 클릭
3. **사용자 변수** 섹션에서 `Path` 선택 → **편집** 클릭
4. **새로 만들기** 클릭
5. `C:\Users\사용자명\AppData\Local\Programs\Ollama` 입력
   - `사용자명`을 본인의 사용자명으로 변경
6. **확인** → **확인** → **확인**
7. **터미널을 완전히 닫고 다시 열기**

방법 B - PowerShell로 설정:
```powershell
# PowerShell을 관리자 권한으로 실행
$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$ollamaPath", "User")

# 터미널 재시작 후 확인
ollama --version
```

**3단계: 임시 사용 (현재 세션만)**

터미널을 재시작하고 싶지 않다면:
```cmd
# CMD에서
set PATH=%PATH%;C:\Users\사용자명\AppData\Local\Programs\Ollama
ollama --version

# PowerShell에서
$env:Path += ";$env:LOCALAPPDATA\Programs\Ollama"
ollama --version
```

**4단계: 전체 경로로 실행 (PATH 설정 없이)**

```cmd
# 전체 경로를 입력하여 직접 실행
C:\Users\사용자명\AppData\Local\Programs\Ollama\ollama.exe --version
C:\Users\사용자명\AppData\Local\Programs\Ollama\ollama.exe list
```

**확인 방법:**
```cmd
# 어느 터미널에서든 실행
ollama --version

# 출력 예시:
# ollama version is 0.12.11
```

### macOS
```bash
# Homebrew를 통한 설치
brew install ollama

# 또는 공식 사이트에서 다운로드
# https://ollama.com/download
```

### Linux
```bash
# 한 줄 설치 스크립트
curl -fsSL https://ollama.com/install.sh | sh

# 수동 설치
wget https://ollama.com/download/linux
sudo install linux /usr/local/bin/ollama
```

---

## 기본 사용법

### 1. 모델 다운로드 및 실행
```bash
# Gemma 3 1B 모델 다운로드
ollama pull gemma3:1b

# 모델 실행 (대화형 모드)
ollama run gemma3:1b

# 종료: /bye 입력
```

### 2. 설치된 모델 확인
```bash
# 모델 목록 조회
ollama list

# 출력 예시:
# NAME              ID            SIZE      MODIFIED
# gemma3:1b         a1b2c3d4      815 MB    2 days ago
```

### 3. 모델 삭제
```bash
# 특정 모델 삭제
ollama rm gemma3:1b
```

### 4. 서버 실행 (백그라운드)
```bash
# Ollama 서버 시작 (기본 포트: 11434)
ollama serve

# 백그라운드 실행 (Linux/macOS)
ollama serve &

# Windows에서는 자동으로 백그라운드 서비스로 실행됨
```

---

## Python API 사용

### 설치
```bash
pip install requests
```

### 기본 예제

#### 1. 서버 상태 확인
```python
import requests

OLLAMA_URL = "http://localhost:11434"

# 서버 상태 확인
response = requests.get(f"{OLLAMA_URL}/")
print("서버 상태:", response.status_code)  # 200 = 정상
```

#### 2. 텍스트 생성 (Generate API)
```python
import requests
import json

def generate_text(prompt, model="gemma3:1b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": True  # 스트리밍 방식
        },
        stream=True
    )
    
    print("응답: ", end="")
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if 'response' in data:
                print(data['response'], end='', flush=True)
            if data.get('done', False):
                print("\n")
                # 성능 통계
                print(f"소요 시간: {data.get('total_duration', 0) / 1e9:.2f}초")
                break

# 사용 예시
generate_text("파이썬의 장점을 3가지만 설명해줘")
```

#### 3. 대화 (Chat API)
```python
def chat(messages, model="gemma3:1b"):
    """
    messages: [{"role": "user", "content": "질문"}]
    """
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": True
        },
        stream=True
    )
    
    full_response = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if 'message' in data:
                chunk = data['message'].get('content', '')
                print(chunk, end='', flush=True)
                full_response += chunk
            if data.get('done', False):
                print("\n")
                break
    
    return full_response

# 대화 예시
conversation = [
    {"role": "user", "content": "안녕! 나는 철수야."},
]
response1 = chat(conversation)

# 대화 이어서 진행
conversation.append({"role": "assistant", "content": response1})
conversation.append({"role": "user", "content": "내 이름이 뭐였지?"})
response2 = chat(conversation)
```

#### 4. 비스트리밍 방식
```python
def generate_non_stream(prompt, model="gemma3:1b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False  # 한 번에 전체 응답 받기
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data['response']
    else:
        return None

# 사용 예시
result = generate_non_stream("간단히 자기소개 해줘")
print(result)
```

### 완전한 테스트 스크립트
```bash
# 프로젝트에 포함된 테스트 스크립트 실행
python ollama/test_ollama_gemma3.py
```

---

## 주요 명령어

### 모델 관리
```bash
# 모델 검색
ollama search gemma

# 모델 다운로드
ollama pull gemma3:1b
ollama pull llama3.3:1b

# 설치된 모델 목록
ollama list

# 모델 정보 확인
ollama show gemma3:1b

# 모델 삭제
ollama rm gemma3:1b
```

### 실행 및 대화
```bash
# 대화형 모드로 실행
ollama run gemma3:1b

# 한 번만 질문하고 종료
ollama run gemma3:1b "파이썬이란?"

# 시스템 프롬프트와 함께 실행
ollama run gemma3:1b --system "You are a helpful coding assistant"
```

### 서버 관리
```bash
# 서버 시작
ollama serve

# 포트 변경하여 시작 (환경변수)
OLLAMA_HOST=0.0.0.0:8080 ollama serve

# Windows에서 포트 변경
set OLLAMA_HOST=0.0.0.0:8080
ollama serve
```

---

## API 레퍼런스

### 엔드포인트 목록

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 서버 상태 확인 |
| `/api/generate` | POST | 텍스트 생성 |
| `/api/chat` | POST | 대화형 응답 |
| `/api/tags` | GET | 모델 목록 조회 |
| `/api/pull` | POST | 모델 다운로드 |
| `/api/show` | POST | 모델 정보 조회 |
| `/api/delete` | DELETE | 모델 삭제 |

### Generate API 파라미터

```python
{
    "model": "gemma3:1b",           # 필수: 모델 이름
    "prompt": "질문 내용",           # 필수: 프롬프트
    "stream": true,                  # 옵션: 스트리밍 여부 (기본: true)
    "options": {
        "temperature": 0.7,          # 생성 다양성 (0.0~2.0, 기본: 0.8)
        "top_k": 40,                 # Top-K 샘플링 (기본: 40)
        "top_p": 0.9,                # Top-P 샘플링 (기본: 0.9)
        "num_predict": 128,          # 최대 토큰 수 (기본: 128)
        "stop": ["\n", "END"]        # 중단 문자열 리스트
    },
    "system": "시스템 프롬프트",     # 옵션: 시스템 메시지
    "context": []                    # 옵션: 이전 대화 컨텍스트
}
```

### Chat API 파라미터

```python
{
    "model": "gemma3:1b",
    "messages": [
        {"role": "system", "content": "시스템 프롬프트"},
        {"role": "user", "content": "질문"},
        {"role": "assistant", "content": "이전 응답"},
        {"role": "user", "content": "다음 질문"}
    ],
    "stream": true,
    "options": {
        "temperature": 0.7,
        "top_p": 0.9
    }
}
```

### 응답 형식

#### Stream 응답 (stream=true)
```json
{"model":"gemma3:1b","created_at":"2025-11-16T...","response":"안","done":false}
{"model":"gemma3:1b","created_at":"2025-11-16T...","response":"녕","done":false}
{"model":"gemma3:1b","created_at":"2025-11-16T...","response":"하","done":false}
{
    "model": "gemma3:1b",
    "created_at": "2025-11-16T...",
    "response": "",
    "done": true,
    "total_duration": 2270000000,
    "load_duration": 50000000,
    "prompt_eval_count": 10,
    "eval_count": 197,
    "eval_duration": 2200000000
}
```

#### Non-stream 응답 (stream=false)
```json
{
    "model": "gemma3:1b",
    "created_at": "2025-11-16T...",
    "response": "안녕하세요! 저는 AI 어시스턴트입니다...",
    "done": true,
    "total_duration": 2270000000,
    "eval_count": 197
}
```

---

## 성능 최적화

### 1. 모델 선택
```bash
# 용도별 권장 모델
# - 빠른 응답 필요: gemma3:1b, qwen2.5:0.5b
# - 균형잡힌 성능: gemma3:2b, llama3.3:3b
# - 높은 품질: gemma3:7b, llama3.3:8b
```

### 2. 파라미터 튜닝
```python
# 빠른 응답이 필요한 경우
options = {
    "num_predict": 64,        # 짧은 응답
    "temperature": 0.5,       # 낮은 다양성
    "top_k": 20,             # 작은 샘플링
}

# 창의적인 응답이 필요한 경우
options = {
    "num_predict": 256,       # 긴 응답
    "temperature": 1.0,       # 높은 다양성
    "top_p": 0.95,           # 넓은 샘플링
}
```

### 3. GPU 사용 (NVIDIA)
```bash
# Ollama는 자동으로 GPU를 감지하고 사용
# CUDA 11.8+ 필요

# GPU 사용 확인
nvidia-smi

# 환경 변수 설정 (필요시)
# Linux/macOS:
export CUDA_VISIBLE_DEVICES=0

# Windows:
set CUDA_VISIBLE_DEVICES=0
```

### 4. 메모리 관리
```bash
# 여러 모델 동시 사용 시 메모리 설정
# Linux/macOS:
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_MAX_QUEUE=512

# Windows:
set OLLAMA_MAX_LOADED_MODELS=2
set OLLAMA_MAX_QUEUE=512
```

---

## 트러블슈팅

### 문제 0: Windows에서 "ollama 명령을 찾을 수 없습니다" 오류
```cmd
# 원인: PATH 환경 변수에 Ollama가 등록되지 않음
# 해결: 위 [설치 방법 - Windows PATH 설정 문제 해결] 섹션 참조

# 빠른 임시 해결 (현재 세션만):
set PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama
ollama --version

# 영구적 해결:
# Win + R → sysdm.cpl → 고급 → 환경 변수 → Path 편집
# 추가: C:\Users\사용자명\AppData\Local\Programs\Ollama
```

### 문제 1: "Connection refused" 오류
```bash
# 원인: Ollama 서버가 실행되지 않음
# 해결:
ollama serve

# 백그라운드 실행 확인
# Windows: 작업 관리자에서 ollama.exe 확인
# Linux/macOS: 
ps aux | grep ollama
```

### 문제 2: 포트 충돌 (11434 포트 사용 중)
```bash
# 다른 포트로 실행
# Linux/macOS:
OLLAMA_HOST=0.0.0.0:8080 ollama serve

# Windows:
set OLLAMA_HOST=0.0.0.0:8080
ollama serve

# Python 코드도 수정
OLLAMA_URL = "http://localhost:8080"
```

### 문제 3: 모델 다운로드 실패
```bash
# 네트워크 확인
ping ollama.com

# 수동 다운로드 및 설치
# 1. 모델 파일을 직접 다운로드
# 2. ~/.ollama/models/ 디렉토리에 배치
# Windows: C:\Users\사용자명\.ollama\models\
```

### 문제 4: GPU 인식 안 됨
```bash
# NVIDIA GPU 드라이버 확인
nvidia-smi

# CUDA 버전 확인 (11.8 이상 필요)
nvcc --version

# Ollama 재설치 (GPU 버전)
# https://ollama.com/download
```

### 문제 5: 응답이 너무 느림
```bash
# 1. 더 작은 모델 사용
ollama pull gemma3:1b  # 대신 2b나 7b 대신

# 2. num_predict 줄이기
options = {"num_predict": 64}

# 3. GPU 사용 확인
# CPU 사용 시 GPU로 전환
```

### 문제 6: Python에서 한글 깨짐
```python
# UTF-8 인코딩 명시
response = requests.post(
    url,
    json=data,
    headers={"Content-Type": "application/json; charset=utf-8"}
)

# 또는 응답 인코딩 설정
response.encoding = 'utf-8'
```

---

## 추가 리소스

### 공식 문서
- **공식 사이트**: https://ollama.com
- **GitHub**: https://github.com/ollama/ollama
- **API 문서**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **모델 라이브러리**: https://ollama.com/library

### 커뮤니티
- **Discord**: https://discord.gg/ollama
- **Reddit**: r/ollama
- **GitHub Discussions**: https://github.com/ollama/ollama/discussions

### 관련 프로젝트
- **Open WebUI**: Ollama용 웹 인터페이스
- **LangChain**: Ollama 통합 지원
- **LlamaIndex**: Ollama를 통한 RAG 구현

---

## 라이선스 및 주의사항

### Ollama
- **라이선스**: MIT License
- **상업적 사용**: 가능

### 모델 라이선스
각 모델마다 다른 라이선스가 적용됩니다:
- **Gemma**: Google의 Gemma Terms of Use
- **Llama**: Meta의 Llama 3 Community License
- **Qwen**: Apache 2.0 (일부 모델)

사용 전 각 모델의 라이선스를 확인하세요.

---

## 버전 정보

- **문서 작성일**: 2025-11-16
- **Ollama 버전**: 0.5.0+
- **테스트 환경**: Windows 11, Python 3.11

---

## 예제 코드 위치

```
프로젝트 구조:
koreaspray/
├── ollama/
│   └── test_ollama_gemma3.py    # 통합 테스트 스크립트
├── Ollama_README.md              # 이 문서
└── requirements.txt              # 필요한 패키지
```

### 빠른 시작
```bash
# 1. Ollama 설치 (위 설치 방법 참조)
# Windows: https://ollama.com/download

# 2. PATH 설정 확인 (Windows만 해당)
ollama --version
# "명령을 찾을 수 없습니다" 오류 시 → 위 Windows PATH 설정 섹션 참조

# 3. 모델 다운로드
ollama pull gemma3:1b

# 4. 서버 시작 (자동 실행되지 않은 경우)
ollama serve

# 5. Python 테스트 실행
python ollama/test_ollama_gemma3.py
```

---

**질문이나 문제가 있으시면 GitHub Issues에 올려주세요!** 🚀

