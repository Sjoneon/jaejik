"""
Groq API - Qwen3-32B 간단한 예제

사용자가 제공한 기본 코드를 완성한 간단한 예제입니다.
"""

import os
from groq import Groq

def main():
    # API 키 확인
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("⚠️  GROQ_API_KEY 환경 변수를 설정해주세요.")
        print("\nWindows (CMD): set GROQ_API_KEY=your_api_key")
        print("Windows (PowerShell): $env:GROQ_API_KEY='your_api_key'")
        return
    
    # Groq 클라이언트 초기화
    client = Groq()
    
    # 사용자 입력 받기
    user_input = input("\n질문을 입력하세요: ")
    
    if not user_input.strip():
        user_input = "Python의 장점과 단점을 설명해주세요."
        print(f"기본 질문 사용: {user_input}")
    
    print("\n응답:")
    print("-" * 60)
    
    # 채팅 완성 요청
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None
    )
    
    # 스트리밍 응답 출력
    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
    
    print("\n" + "-" * 60)

if __name__ == "__main__":
    main()

