# Gemma 3 1B IT 모델 - 강의 자료

## 📦 모델 정보

- **모델명**: google/gemma-3-1b-it
- **크기**: 1.90 GB
- **타입**: Instruction-tuned 텍스트 생성 모델
- **컨텍스트 윈도우**: 32K 토큰 (1B 모델)
- **라이선스**: Gemma License (승인 필요)

## 📁 로컬 모델 위치

### 현재 프로젝트 경로
```
C:\Users\Pc\koreaspray\models\gemma-3-1b-it\
```

### 포함 파일
- `model.safetensors` (1.86 GB) - 모델 웨이트
- `tokenizer.json` (31.8 MB) - 토크나이저
- `tokenizer.model` (4.5 MB)
- `config.json` - 모델 설정
- `generation_config.json` - 생성 설정
- `tokenizer_config.json` - 토크나이저 설정
- `special_tokens_map.json` - 특수 토큰 맵핑
- `added_tokens.json` - 추가 토큰

## ✅ CPU 동작 테스트 결과

### 성능
- ✅ **모델 로딩**: 약 2.8초
- ✅ **텍스트 생성**: 약 1.7초 (30 토큰)
- ✅ **CPU 전용**: GPU 없이도 정상 작동

### 환경
- PyTorch: 2.9.1+cpu
- Transformers: 4.57.1
- Device: CPU
- OS: Windows 11

## 💻 사용 방법

### 1. 온라인 모델 사용 (Hugging Face)

```python
from transformers import pipeline
import torch

# Hugging Face에서 자동 다운로드
pipe = pipeline(
    "text-generation",
    model="google/gemma-3-1b-it",
    device="cpu",
    dtype=torch.float32
)

messages = [[{
    "role": "user",
    "content": [{"type": "text", "text": "안녕하세요!"}]
}]]

output = pipe(messages, max_new_tokens=50)
```

**장점**: 항상 최신 버전
**단점**: 인터넷 필요, Hugging Face 로그인 필요

### 2. 로컬 모델 사용 (권장 - 강의용)

```python
from transformers import pipeline
import torch

# 로컬 경로에서 모델 로드
model_path = "models/gemma-3-1b-it"

pipe = pipeline(
    "text-generation",
    model=model_path,
    device="cpu",
    dtype=torch.float32
)

messages = [[{
    "role": "user",
    "content": [{"type": "text", "text": "What is 2+2?"}]
}]]

output = pipe(messages, max_new_tokens=50)

# 응답 추출
if isinstance(output, list) and len(output) > 0:
    result = output[0]
    if isinstance(result, list) and len(result) > 0:
        last_message = result[-1]
        if 'content' in last_message:
            content = last_message['content']
            if isinstance(content, list):
                print(content[0]['text'])
```

**장점**: 
- 인터넷 불필요
- 강의실에서 안정적
- 빠른 로딩 (캐시 활용)

**단점**: 
- 초기 2GB 다운로드 필요
- 디스크 공간 사용

## 📚 강의 자료 배포 방법

### 방법 1: 모델 폴더 직접 배포

1. `models/gemma-3-1b-it` 폴더 전체를 USB나 클라우드에 복사
2. 학생들은 프로젝트 루트에 `models/` 디렉토리 생성
3. 받은 `gemma-3-1b-it` 폴더를 `models/` 안에 복사
4. 위의 로컬 모델 사용 코드로 실행

### 방법 2: Hugging Face 캐시 활용

원본 캐시 위치:
```
C:\Users\Pc\.cache\huggingface\hub\models--google--gemma-3-1b-it
```

이 폴더를 학생 PC의 같은 경로에 복사하면 자동 인식됩니다.

### 방법 3: 학생들이 직접 다운로드 (권장)

1. Hugging Face 계정 생성: https://huggingface.co
2. 모델 페이지에서 라이선스 동의: https://huggingface.co/google/gemma-3-1b-it
3. Hugging Face 토큰 생성 (READ 권한)
4. 로그인:
```python
from huggingface_hub import login
login(token="your_token_here")
```
5. 첫 실행 시 자동 다운로드

**장점**: 
- 저작권 안전
- 각자 최신 버전 사용
- 재배포 문제 없음

## 🔧 필수 라이브러리

```bash
pip install transformers torch accelerate sentencepiece protobuf
```

또는 `requirements.txt`:
```
transformers>=4.50.0
torch>=2.0.0
accelerate
sentencepiece
protobuf
```

## 📝 예제 코드

### 간단한 채팅
```python
from transformers import pipeline
import torch

pipe = pipeline(
    "text-generation",
    model="models/gemma-3-1b-it",  # 로컬 경로
    device="cpu",
    dtype=torch.float32
)

def chat(question):
    messages = [[{
        "role": "user",
        "content": [{"type": "text", "text": question}]
    }]]
    
    output = pipe(messages, max_new_tokens=100)
    
    # 응답 추출
    if isinstance(output, list) and len(output) > 0:
        result = output[0]
        if isinstance(result, list) and len(result) > 0:
            last = result[-1]
            if 'content' in last:
                return last['content'][0]['text']
    return "응답 생성 실패"

# 사용 예
print(chat("Python이란 무엇인가요?"))
print(chat("1+1은?"))
```

### 시스템 프롬프트 포함
```python
messages = [[
    {
        "role": "system",
        "content": [{"type": "text", "text": "당신은 친절한 AI 어시스턴트입니다."}]
    },
    {
        "role": "user",
        "content": [{"type": "text", "text": "안녕하세요!"}]
    }
]]

output = pipe(messages, max_new_tokens=50)
```

## ⚠️ 주의사항

1. **라이선스**: Gemma License 동의 필요
2. **CPU 전용**: GPU 없이도 동작하지만 느림
3. **메모리**: 최소 4GB RAM 권장
4. **첫 실행**: 모델 로딩에 2-5초 소요
5. **생성 속도**: CPU에서 초당 5-10 토큰 정도

## 🚀 최적화 팁

### 더 빠른 생성
```python
output = pipe(
    messages,
    max_new_tokens=50,
    do_sample=False,  # 그리디 디코딩 (더 빠름)
    num_beams=1       # 빔 서치 비활성화
)
```

### 메모리 절약
```python
import torch

pipe = pipeline(
    "text-generation",
    model="models/gemma-3-1b-it",
    device="cpu",
    dtype=torch.float16,  # 반정밀도 (메모리 절약)
    torch_dtype=torch.float16
)
```

## 📞 문제 해결

### "Access denied" 오류
→ Hugging Face 로그인 필요: https://huggingface.co/google/gemma-3-1b-it

### 메모리 부족 오류
→ 다른 프로그램 종료, 브라우저 탭 닫기

### 너무 느림
→ max_new_tokens 값 줄이기 (100 → 50)
→ GPU가 있다면 device="cuda" 사용

### 한글 깨짐
→ tokenizer는 한국어 지원함 (140개 언어)
→ 출력 인코딩 확인: sys.stdout.reconfigure(encoding='utf-8')

## 📖 참고 자료

- Hugging Face 모델 페이지: https://huggingface.co/google/gemma-3-1b-it
- Gemma 공식 문서: https://ai.google.dev/gemma
- Transformers 문서: https://huggingface.co/docs/transformers

---

**작성일**: 2025-11-16
**테스트 환경**: Windows 11, Python 3.11, CPU

