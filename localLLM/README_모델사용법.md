# Gemma 3 1B IT 모델 - 빠른 시작 가이드

## 📁 프로젝트 구조

```
koreaspray/
├── models/
│   └── gemma-3-1b-it/          # 로컬 모델 파일 (1.90 GB)
│       ├── model.safetensors   # 모델 웨이트
│       ├── tokenizer.json      # 토크나이저
│       └── ... (설정 파일들)
│
├── test_gemma3_comprehensive.py  # 🧪 종합 테스트 스크립트
├── GEMMA3_강의자료.md            # 📖 상세 강의 자료
└── README_모델사용법.md          # 이 파일

```

## 🧪 빠른 테스트

```bash
# 종합 테스트 실행 (권장)
python test_gemma3_comprehensive.py

# 다른 모델 경로로 테스트
python test_gemma3_comprehensive.py --model-path /path/to/model
```

테스트는 다음을 자동으로 수행합니다:
- ✅ 모델 파일 존재 확인
- ✅ 모델 로딩 및 시간 측정
- ✅ 6가지 다양한 생성 테스트 (한국어/영어, 수학, 코드 등)
- ✅ 시스템 프롬프트 테스트
- ✅ 성능 측정 (5회 연속 생성)
- ✅ JSON 리포트 자동 생성

## 🚀 빠른 시작

### 1. 로컬 모델로 실행 (강의용 권장)

```python
from transformers import pipeline
import torch

# 로컬 경로에서 모델 로드
pipe = pipeline(
    "text-generation",
    model="models/gemma-3-1b-it",
    device="cpu",
    dtype=torch.float32
)

# 질문하기
messages = [[{
    "role": "user",
    "content": [{"type": "text", "text": "안녕하세요!"}]
}]]

output = pipe(messages, max_new_tokens=50)
print(output)
```

### 2. 응답 추출 헬퍼 함수

```python
def extract_response(output):
    """생성된 응답을 추출하는 헬퍼 함수"""
    try:
        # 출력 구조: [[{'generated_text': [user_msg, assistant_msg]}]]
        messages = output[0][0]['generated_text']
        
        # assistant 메시지 찾기
        for msg in reversed(messages):
            if msg.get('role') == 'assistant':
                return msg.get('content', '')
        
        return None
    except:
        return None

# 사용 예
output = pipe(messages, max_new_tokens=50)
response = extract_response(output)
print(response)
```

## ✅ 동작 확인 완료

- ✅ 모델 다운로드: 완료 (1.90 GB)
- ✅ 로컬 경로 복사: `models/gemma-3-1b-it/`
- ✅ CPU 동작 테스트: 성공
- ✅ 모델 로딩 시간: 약 2.4초
- ✅ 텍스트 생성 속도: 약 2.3초 (30-50 토큰)
- ✅ 응답 추출: 정상 작동

### 테스트 결과 예시

```
간단한 수학 문제
  입력: What is 2 + 2?
  응답: 2 + 2 = 4
  시간: 2.25초
```

## 📦 강의 자료 배포

이 폴더 전체를 USB나 클라우드로 공유하면 됩니다:

```
koreaspray/
├── models/gemma-3-1b-it/    # ← 이 폴더가 핵심!
└── GEMMA3_강의자료.md        # ← 강의 자료
```

학생들은:
1. 이 폴더를 받아서
2. `pip install transformers torch accelerate`
3. `python test_local_model.py` 실행

인터넷 없이도 바로 동작합니다! 🎉

## 📖 상세 문서

더 자세한 내용은 `GEMMA3_강의자료.md`를 참고하세요.

- 다양한 사용 예제
- 최적화 팁
- 문제 해결 가이드
- API 참조

