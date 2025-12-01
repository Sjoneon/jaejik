"""
Groq API를 사용한 Qwen3-32B 모델 테스트 스크립트

이 스크립트는 Groq API를 통해 qwen/qwen3-32b 모델을 테스트합니다.
"""

import os
from groq import Groq
import dotenv
dotenv.load_dotenv()

def test_simple_completion():
    """기본 대화 완성 테스트"""
    print("\n" + "="*80)
    print("테스트 1: 기본 대화 완성")
    print("="*80)
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": "Python으로 피보나치 수열을 구현하는 간단한 함수를 작성해주세요."
            }
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None
    )
    
    print("\n응답:")
    full_response = ""
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)
        full_response += content
    
    print("\n")
    return full_response


def test_conversation():
    """멀티턴 대화 테스트"""
    print("\n" + "="*80)
    print("테스트 2: 멀티턴 대화")
    print("="*80)
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    messages = [
        {
            "role": "system",
            "content": "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 한국어로 답변해주세요."
        },
        {
            "role": "user",
            "content": "인공지능이란 무엇인가요?"
        }
    ]
    
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=messages,
        temperature=0.6,
        max_completion_tokens=2048,
        top_p=0.95,
        stream=True,
        stop=None
    )
    
    print("\n응답:")
    full_response = ""
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)
        full_response += content
    
    print("\n")
    
    # 후속 질문
    messages.append({
        "role": "assistant",
        "content": full_response
    })
    messages.append({
        "role": "user",
        "content": "그렇다면 머신러닝과 딥러닝의 차이는 무엇인가요?"
    })
    
    print("\n후속 질문 응답:")
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=messages,
        temperature=0.6,
        max_completion_tokens=2048,
        top_p=0.95,
        stream=True,
        stop=None
    )
    
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)
    
    print("\n")


def test_creative_writing():
    """창의적 글쓰기 테스트 (높은 temperature)"""
    print("\n" + "="*80)
    print("테스트 3: 창의적 글쓰기 (temperature=1.0)")
    print("="*80)
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": "미래의 AI 세상을 배경으로 한 짧은 이야기를 써주세요. (200자 이내)"
            }
        ],
        temperature=1.0,
        max_completion_tokens=1024,
        top_p=0.95,
        stream=True,
        stop=None
    )
    
    print("\n응답:")
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)
    
    print("\n")


def test_code_generation():
    """코드 생성 테스트 (낮은 temperature)"""
    print("\n" + "="*80)
    print("테스트 4: 코드 생성 (temperature=0.2)")
    print("="*80)
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "system",
                "content": "당신은 전문 프로그래머입니다. 깔끔하고 효율적인 코드를 작성해주세요."
            },
            {
                "role": "user",
                "content": "Python으로 이진 탐색 트리(Binary Search Tree)를 구현해주세요. 삽입, 검색, 삭제 메서드를 포함해주세요."
            }
        ],
        temperature=0.2,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None
    )
    
    print("\n응답:")
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)
    
    print("\n")


def test_non_streaming():
    """비스트리밍 응답 테스트"""
    print("\n" + "="*80)
    print("테스트 5: 비스트리밍 응답")
    print("="*80)
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "user",
                "content": "양자컴퓨터의 원리를 간단히 설명해주세요."
            }
        ],
        temperature=0.6,
        max_completion_tokens=2048,
        top_p=0.95,
        stream=False,
        stop=None
    )
    
    print("\n응답:")
    print(completion.choices[0].message.content)
    print("\n")
    
    # 토큰 사용량 출력
    print(f"사용된 토큰:")
    print(f"  - Prompt: {completion.usage.prompt_tokens}")
    print(f"  - Completion: {completion.usage.completion_tokens}")
    print(f"  - Total: {completion.usage.total_tokens}")


def test_with_error_handling():
    """에러 처리를 포함한 테스트"""
    print("\n" + "="*80)
    print("테스트 6: 에러 처리")
    print("="*80)
    
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role": "user",
                    "content": "안녕하세요! Qwen3 모델입니다."
                }
            ],
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=0.95,
            stream=True,
            stop=None
        )
        
        print("\n응답:")
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
        
        print("\n")
        
    except Exception as e:
        print(f"\n에러 발생: {type(e).__name__}")
        print(f"상세 내용: {str(e)}")


def main():
    """메인 실행 함수"""
    print("="*80)
    print("Groq API - Qwen3-32B 모델 테스트")
    print("="*80)
    
    # API 키 확인
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n⚠️  GROQ_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("\n설정 방법:")
        print("  Windows (CMD): set GROQ_API_KEY=your_api_key_here")
        print("  Windows (PowerShell): $env:GROQ_API_KEY='your_api_key_here'")
        print("  Linux/Mac: export GROQ_API_KEY=your_api_key_here")
        print("\nGroq API 키는 https://console.groq.com/keys 에서 발급받을 수 있습니다.")
        return
    
    print(f"\n✓ API 키 확인됨 (길이: {len(api_key)} 문자)")
    
    try:
        # 각 테스트 실행
        test_simple_completion()
        test_conversation()
        test_creative_writing()
        test_code_generation()
        test_non_streaming()
        test_with_error_handling()
        
        print("\n" + "="*80)
        print("모든 테스트 완료!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n예상치 못한 오류 발생: {type(e).__name__}")
        print(f"상세 내용: {str(e)}")
        print("\n문제가 지속되면 다음을 확인해주세요:")
        print("  1. API 키가 올바른지 확인")
        print("  2. 네트워크 연결 상태 확인")
        print("  3. Groq API 서비스 상태 확인 (https://status.groq.com/)")


if __name__ == "__main__":
    main()

