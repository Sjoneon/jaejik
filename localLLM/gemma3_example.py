"""
Gemma 3 1B IT 모델 간단 사용 예제
학생들을 위한 간단한 사용법
"""
from transformers import pipeline
import torch

print("=" * 70)
print("Gemma 3 1B IT - 간단한 사용 예제")
print("=" * 70)

# 모델 로딩
print("\n1. 모델 로딩 중...")
pipe = pipeline(
    "text-generation",
    model="models/gemma-3-1b-it",  # 로컬 모델 경로
    device="cpu",                   # CPU 사용
    dtype=torch.float32
)
print("   ✓ 로딩 완료!\n")


def chat(question: str, max_length: int = 50):
    """간단한 채팅 함수"""
    # 입력 메시지 구성
    messages = [[{
        "role": "user",
        "content": [{"type": "text", "text": question}]
    }]]
    
    # 텍스트 생성
    output = pipe(messages, max_new_tokens=max_length)
    
    # 응답 추출
    try:
        messages = output[0][0]['generated_text']
        for msg in reversed(messages):
            if msg.get('role') == 'assistant':
                return msg.get('content', '')
    except:
        return "응답을 가져올 수 없습니다."
    
    return "응답을 가져올 수 없습니다."


# 예제 사용
print("2. 예제 테스트\n")

# 예제 1: 간단한 질문
print("─" * 70)
question1 = "What is Python?"
print(f"Q: {question1}")
answer1 = chat(question1, 60)
print(f"A: {answer1}\n")

# 예제 2: 수학 문제
print("─" * 70)
question2 = "Calculate 15 * 7"
print(f"Q: {question2}")
answer2 = chat(question2, 30)
print(f"A: {answer2}\n")

# 예제 3: 한국어 질문
print("─" * 70)
question3 = "인공지능이 뭔가요?"
print(f"Q: {question3}")
answer3 = chat(question3, 80)
print(f"A: {answer3}\n")

# 대화형 모드 (선택사항)
print("=" * 70)
print("대화형 모드 (종료하려면 'quit' 입력)")
print("=" * 70)

while True:
    try:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료', 'q']:
            print("\n프로그램을 종료합니다.")
            break
        
        if not user_input:
            continue
        
        response = chat(user_input, 100)
        print(f"AI:  {response}")
        
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        break
    except Exception as e:
        print(f"오류: {e}")

