"""
Ollama API를 통해 gemma3:1b 모델 테스트
공식 문서: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

import requests
import json

OLLAMA_BASE_URL = "http://localhost:11434"

def check_ollama_status():
    """Ollama 서버가 실행 중인지 확인"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/")
        if response.status_code == 200:
            print("✓ Ollama 서버가 실행 중입니다.")
            return True
        else:
            print(f"✗ Ollama 서버 응답 이상: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Ollama 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인해주세요.")
        return False
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return False

def list_models():
    """설치된 모델 목록 조회"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"\n설치된 모델 목록 ({len(models)}개):")
            for model in models:
                print(f"  - {model['name']} (크기: {model.get('size', 'N/A')} bytes)")
            return models
        else:
            print(f"✗ 모델 목록 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ 모델 목록 조회 오류: {e}")
        return []

def pull_model(model_name="gemma2:2b"):
    """모델 다운로드 (필요시)"""
    print(f"\n'{model_name}' 모델 다운로드 시도 중...")
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/pull",
            json={"name": model_name},
            stream=True
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get('status', '')
                    print(f"  {status}")
                    if 'error' in data:
                        print(f"  ✗ 오류: {data['error']}")
                        return False
            print(f"✓ '{model_name}' 모델 다운로드 완료")
            return True
        else:
            print(f"✗ 모델 다운로드 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 모델 다운로드 오류: {e}")
        return False

def test_generate(model_name="gemma2:2b", prompt="안녕하세요! 자기소개를 해주세요."):
    """텍스트 생성 API 테스트"""
    print(f"\n=== 텍스트 생성 테스트 ({model_name}) ===")
    print(f"프롬프트: {prompt}")
    print("\n응답:")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": True
            },
            stream=True
        )
        
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        chunk = data['response']
                        print(chunk, end='', flush=True)
                        full_response += chunk
                    if data.get('done', False):
                        print("\n")
                        # 성능 정보 출력
                        if 'total_duration' in data:
                            print(f"\n성능 정보:")
                            print(f"  - 총 소요 시간: {data['total_duration'] / 1e9:.2f}초")
                            if 'eval_count' in data and 'eval_duration' in data:
                                tokens_per_sec = data['eval_count'] / (data['eval_duration'] / 1e9)
                                print(f"  - 생성 속도: {tokens_per_sec:.2f} tokens/sec")
            return True
        else:
            print(f"✗ 생성 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 생성 오류: {e}")
        return False

def test_chat(model_name="gemma2:2b"):
    """채팅 API 테스트"""
    print(f"\n=== 채팅 API 테스트 ({model_name}) ===")
    
    messages = [
        {"role": "user", "content": "파이썬에서 리스트와 튜플의 차이점을 간단히 설명해주세요."}
    ]
    
    print(f"질문: {messages[0]['content']}")
    print("\n응답:")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model_name,
                "messages": messages,
                "stream": True
            },
            stream=True
        )
        
        if response.status_code == 200:
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
            return True
        else:
            print(f"✗ 채팅 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 채팅 오류: {e}")
        return False

def main():
    print("=" * 60)
    print("Ollama Gemma 모델 테스트")
    print("=" * 60)
    
    # 1. Ollama 서버 상태 확인
    if not check_ollama_status():
        print("\n안내: Ollama 서버를 먼저 실행해주세요.")
        print("명령: ollama serve")
        return
    
    # 2. 설치된 모델 확인
    models = list_models()
    model_names = [m['name'] for m in models]
    
    # 3. gemma3 또는 gemma2 모델 찾기
    target_model = None
    for name in model_names:
        if 'gemma' in name.lower():
            target_model = name
            print(f"\n✓ 사용 가능한 Gemma 모델 발견: {target_model}")
            break
    
    # gemma 모델이 없으면 gemma2:2b 다운로드 시도 (gemma3:1b는 아직 미지원일 수 있음)
    if not target_model:
        print("\n⚠ Gemma 모델이 설치되어 있지 않습니다.")
        user_input = input("gemma2:2b 모델을 다운로드하시겠습니까? (y/n): ")
        if user_input.lower() == 'y':
            if pull_model("gemma2:2b"):
                target_model = "gemma2:2b"
            else:
                print("모델 다운로드에 실패했습니다.")
                return
        else:
            print("테스트를 종료합니다.")
            return
    
    # 4. 텍스트 생성 테스트
    test_generate(target_model)
    
    # 5. 채팅 API 테스트
    test_chat(target_model)
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()

