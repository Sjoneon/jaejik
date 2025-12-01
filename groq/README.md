# Groq API - Qwen3-32B 테스트

이 폴더는 Groq API를 통해 Qwen3-32B 모델을 테스트하는 예제를 포함하고 있습니다.

## 📋 목차

- [소개](#소개)
- [설치](#설치)
- [API 키 설정](#api-키-설정)
- [사용법](#사용법)
- [테스트 종류](#테스트-종류)
- [매개변수 설명](#매개변수-설명)
- [문제 해결](#문제-해결)

## 🎯 소개

**Groq**는 초고속 AI 추론을 제공하는 플랫폼으로, LPU(Language Processing Unit)를 사용하여 놀라운 속도로 LLM을 실행합니다.

**Qwen3-32B**는 Alibaba Cloud의 Qwen 시리즈 중 32B 파라미터 모델로, 다양한 언어 작업에서 우수한 성능을 보여줍니다.

### 주요 특징

- ⚡ **초고속 추론**: Groq의 LPU 기술로 빠른 응답
- 🌏 **다국어 지원**: 한국어를 포함한 다양한 언어 지원
- 💪 **강력한 성능**: 32B 파라미터의 대규모 모델
- 🔄 **스트리밍 지원**: 실시간 응답 스트리밍

## 📦 설치

### 1. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

또는 직접 설치:

```bash
pip install groq
```

## 🔑 API 키 설정

### 1. API 키 발급

1. [Groq Console](https://console.groq.com/)에 접속
2. 계정 생성 또는 로그인
3. [API Keys 페이지](https://console.groq.com/keys)로 이동
4. "Create API Key" 클릭하여 새 키 생성
5. 생성된 키를 안전한 곳에 저장

### 2. 환경 변수 설정

#### Windows (CMD)

```cmd
set GROQ_API_KEY=your_api_key_here
```

#### Windows (PowerShell)

```powershell
$env:GROQ_API_KEY='your_api_key_here'
```

#### Linux/Mac

```bash
export GROQ_API_KEY=your_api_key_here
```

#### 영구적으로 설정 (선택사항)

**Windows:**
- 시스템 속성 → 환경 변수에서 추가

**Linux/Mac:**
- `~/.bashrc` 또는 `~/.zshrc`에 추가:
  ```bash
  export GROQ_API_KEY=your_api_key_here
  ```

## 🚀 사용법

### 기본 실행

```bash
python test_groq_qwen3.py
```

이 명령으로 6가지 다른 테스트가 순차적으로 실행됩니다.

### 코드에서 직접 사용

```python
import os
from groq import Groq

# 클라이언트 생성
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 스트리밍 응답
completion = client.chat.completions.create(
    model="qwen/qwen3-32b",
    messages=[
        {
            "role": "user",
            "content": "안녕하세요! Python에 대해 설명해주세요."
        }
    ],
    temperature=0.6,
    max_completion_tokens=4096,
    top_p=0.95,
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
```

## 🧪 테스트 종류

스크립트는 다음 6가지 테스트를 실행합니다:

### 1. 기본 대화 완성
- 간단한 코딩 질문 (피보나치 수열)
- 스트리밍 응답 처리

### 2. 멀티턴 대화
- 시스템 프롬프트 활용
- 대화 히스토리 유지
- 연속적인 질의응답

### 3. 창의적 글쓰기
- 높은 temperature (1.0) 설정
- 창의적이고 다양한 응답 생성
- 짧은 이야기 생성

### 4. 코드 생성
- 낮은 temperature (0.2) 설정
- 정확하고 일관된 코드 생성
- 복잡한 자료구조 구현 (BST)

### 5. 비스트리밍 응답
- 전체 응답을 한 번에 받기
- 토큰 사용량 확인

### 6. 에러 처리
- 예외 처리 구현 예시
- 안정적인 애플리케이션 개발

## ⚙️ 매개변수 설명

### model
- **설명**: 사용할 모델 이름
- **값**: `"qwen/qwen3-32b"`
- **기타 모델**: `"llama3-70b"`, `"mixtral-8x7b"`, `"gemma2-9b"` 등
- **확인**: [Groq 지원 모델](https://console.groq.com/docs/models)

### messages
- **설명**: 대화 메시지 배열
- **형식**: 
  ```python
  [
      {"role": "system", "content": "시스템 프롬프트"},
      {"role": "user", "content": "사용자 메시지"},
      {"role": "assistant", "content": "어시스턴트 응답"}
  ]
  ```

### temperature
- **설명**: 응답의 무작위성/창의성 제어
- **범위**: 0.0 ~ 2.0
- **권장값**:
  - `0.1 ~ 0.3`: 정확한 답변, 코드 생성
  - `0.6 ~ 0.8`: 균형잡힌 응답 (기본값)
  - `0.9 ~ 1.2`: 창의적인 글쓰기

### max_completion_tokens
- **설명**: 생성할 최대 토큰 수
- **범위**: 1 ~ 모델의 최대 컨텍스트 크기
- **권장값**: 
  - 짧은 답변: 1024
  - 일반적인 답변: 2048
  - 긴 답변/코드: 4096

### top_p
- **설명**: 누적 확률 임계값 (nucleus sampling)
- **범위**: 0.0 ~ 1.0
- **기본값**: 0.95
- **설명**: 상위 확률 토큰만 선택 (temperature와 함께 사용)

### stream
- **설명**: 스트리밍 여부
- **값**: `True` (실시간 출력) / `False` (전체 응답)
- **권장**: 대화형 애플리케이션에는 `True`

### stop
- **설명**: 생성을 중단할 문자열 (배열 또는 단일 문자열)
- **예시**: `["END", "\n\n"]`
- **기본값**: `None`

### reasoning_effort (선택사항)
- **설명**: 추론 노력 수준
- **값**: `"default"`, `"low"`, `"medium"`, `"high"`
- **사용**: 일부 모델에서만 지원

## 🔍 문제 해결

### API 키 오류

```
Error: Invalid API Key
```

**해결책:**
1. API 키가 올바르게 설정되었는지 확인
2. 환경 변수가 현재 터미널 세션에 적용되었는지 확인
3. API 키에 공백이나 잘못된 문자가 없는지 확인

### 모델을 찾을 수 없음

```
Error: Model not found
```

**해결책:**
1. 모델 이름이 정확한지 확인: `"qwen/qwen3-32b"`
2. [지원 모델 목록](https://console.groq.com/docs/models) 확인
3. 계정에 해당 모델 접근 권한이 있는지 확인

### 속도 제한 오류

```
Error: Rate limit exceeded
```

**해결책:**
1. 요청 간격을 늘림
2. 무료 티어의 경우 제한 확인
3. 필요시 유료 플랜으로 업그레이드

### 네트워크 오류

```
Error: Connection failed
```

**해결책:**
1. 인터넷 연결 확인
2. 방화벽/프록시 설정 확인
3. Groq 서비스 상태 확인: [status.groq.com](https://status.groq.com/)

## 📚 추가 리소스

- [Groq 공식 문서](https://console.groq.com/docs)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [Qwen 모델 정보](https://huggingface.co/Qwen)
- [Groq API 레퍼런스](https://console.groq.com/docs/api-reference)

## 💡 팁

1. **속도 최적화**: Groq는 매우 빠르므로 스트리밍을 활용하면 더 나은 UX 제공
2. **비용 절감**: `max_completion_tokens`를 적절히 설정하여 불필요한 토큰 사용 방지
3. **품질 향상**: 명확하고 구체적인 프롬프트 작성
4. **에러 처리**: 프로덕션 환경에서는 항상 try-catch 블록 사용
5. **모니터링**: [Groq 콘솔](https://console.groq.com/)에서 사용량 모니터링

## 📝 라이선스

이 예제 코드는 교육 목적으로 자유롭게 사용할 수 있습니다.

---

**마지막 업데이트**: 2025년 11월

