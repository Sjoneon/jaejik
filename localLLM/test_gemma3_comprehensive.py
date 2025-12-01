"""
Gemma 3 1B IT 모델 종합 테스트
로컬 모델의 CPU 동작을 체계적으로 테스트합니다.
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# UTF-8 출력 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class Gemma3Tester:
    """Gemma 3 모델 테스터"""
    
    def __init__(self, model_path: str = "models/gemma-3-1b-it"):
        self.model_path = Path(model_path).absolute()
        self.pipe = None
        self.test_results = []
        
    def print_header(self, text: str, char: str = "="):
        """헤더 출력"""
        print("\n" + char * 80)
        print(text.center(80))
        print(char * 80)
    
    def print_section(self, text: str):
        """섹션 출력"""
        print(f"\n{'─' * 80}")
        print(f"▶ {text}")
        print('─' * 80)
    
    def check_model_exists(self) -> bool:
        """모델 파일 존재 확인"""
        self.print_section("1. 모델 파일 확인")
        
        print(f"📁 모델 경로: {self.model_path}")
        
        if not self.model_path.exists():
            print(f"❌ 모델 디렉토리가 존재하지 않습니다.")
            return False
        
        # 필수 파일 확인
        required_files = [
            "model.safetensors",
            "config.json",
            "tokenizer.json",
            "tokenizer.model"
        ]
        
        print("\n필수 파일 체크:")
        all_exist = True
        total_size = 0
        
        for filename in required_files:
            filepath = self.model_path / filename
            if filepath.exists():
                size = filepath.stat().st_size
                total_size += size
                size_mb = size / (1024 * 1024)
                size_gb = size / (1024 * 1024 * 1024)
                
                if size_gb >= 1:
                    size_str = f"{size_gb:.2f} GB"
                else:
                    size_str = f"{size_mb:.1f} MB"
                
                print(f"  ✅ {filename:30s} {size_str:>12s}")
            else:
                print(f"  ❌ {filename:30s} {'없음':>12s}")
                all_exist = False
        
        total_gb = total_size / (1024 * 1024 * 1024)
        print(f"\n총 크기: {total_gb:.2f} GB")
        
        if all_exist:
            print("\n✅ 모든 필수 파일이 존재합니다.")
        else:
            print("\n❌ 일부 파일이 누락되었습니다.")
        
        return all_exist
    
    def load_model(self) -> bool:
        """모델 로딩"""
        self.print_section("2. 모델 로딩")
        
        try:
            print("라이브러리 import 중...")
            from transformers import pipeline
            import torch
            
            print(f"  ✅ PyTorch 버전: {torch.__version__}")
            print(f"  ✅ CUDA 사용 가능: {'예' if torch.cuda.is_available() else '아니오 (CPU 전용)'}")
            
            print(f"\n모델 로딩 중... (시간이 걸릴 수 있습니다)")
            print(f"  경로: {self.model_path}")
            
            start_time = time.time()
            
            self.pipe = pipeline(
                "text-generation",
                model=str(self.model_path),
                device="cpu",
                dtype=torch.float32
            )
            
            load_time = time.time() - start_time
            
            print(f"\n✅ 모델 로딩 완료!")
            print(f"  소요 시간: {load_time:.2f}초")
            
            self.test_results.append({
                "test": "모델 로딩",
                "status": "성공",
                "time": load_time
            })
            
            return True
            
        except Exception as e:
            print(f"\n❌ 모델 로딩 실패: {e}")
            self.test_results.append({
                "test": "모델 로딩",
                "status": "실패",
                "error": str(e)
            })
            return False
    
    def extract_response(self, output) -> Optional[str]:
        """생성된 응답 추출
        
        출력 구조: [[{'generated_text': [user_msg, assistant_msg]}]]
        """
        try:
            # output[0][0]['generated_text']로 접근
            if not isinstance(output, list) or len(output) == 0:
                return None
            
            # 첫 번째 레벨 리스트
            first_level = output[0]
            if not isinstance(first_level, list) or len(first_level) == 0:
                return None
            
            # 두 번째 레벨 딕셔너리
            second_level = first_level[0]
            if not isinstance(second_level, dict) or 'generated_text' not in second_level:
                return None
            
            # generated_text는 메시지 리스트
            messages = second_level['generated_text']
            if not isinstance(messages, list) or len(messages) == 0:
                return None
            
            # assistant 메시지 찾기 (역순으로 검색)
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get('role') == 'assistant':
                    content = msg.get('content', '')
                    
                    # content가 문자열이면 직접 반환
                    if isinstance(content, str):
                        return content
                    
                    # content가 리스트면 첫 번째 아이템에서 text 추출
                    elif isinstance(content, list) and len(content) > 0:
                        first_item = content[0]
                        if isinstance(first_item, dict):
                            return first_item.get('text', str(first_item))
                        return str(first_item)
            
            return None
            
        except Exception as e:
            print(f"  ⚠️  응답 추출 오류: {e}")
            return None
    
    def test_generation(self, test_name: str, prompt: str, max_tokens: int = 50) -> Dict:
        """텍스트 생성 테스트"""
        print(f"\n  📝 {test_name}")
        print(f"      입력: {prompt}")
        
        try:
            messages = [[{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }]]
            
            start_time = time.time()
            output = self.pipe(messages, max_new_tokens=max_tokens)
            gen_time = time.time() - start_time
            
            response = self.extract_response(output)
            
            if response:
                # 응답을 50자로 제한하여 출력
                display_response = response[:100] + "..." if len(response) > 100 else response
                print(f"      응답: {display_response}")
                print(f"      시간: {gen_time:.2f}초")
                
                return {
                    "test": test_name,
                    "prompt": prompt,
                    "response": response,
                    "time": gen_time,
                    "status": "성공",
                    "tokens": max_tokens
                }
            else:
                print(f"      ❌ 응답 추출 실패")
                return {
                    "test": test_name,
                    "prompt": prompt,
                    "status": "응답 추출 실패",
                    "time": gen_time
                }
                
        except Exception as e:
            print(f"      ❌ 오류: {e}")
            return {
                "test": test_name,
                "prompt": prompt,
                "status": "실패",
                "error": str(e)
            }
    
    def run_generation_tests(self):
        """다양한 생성 테스트 실행"""
        self.print_section("3. 텍스트 생성 테스트")
        
        test_cases = [
            ("간단한 수학 문제", "What is 2 + 2?", 20),
            ("한국어 인사", "안녕하세요! 간단히 인사해주세요.", 30),
            ("영어 인사", "Hello! Please introduce yourself briefly.", 40),
            ("코드 요청", "Write a simple Python hello world.", 50),
            ("한국어 설명", "Python이 뭔가요? 한 문장으로 설명해주세요.", 50),
            ("긴 응답", "Explain what artificial intelligence is.", 100),
        ]
        
        print(f"\n총 {len(test_cases)}개의 테스트 케이스 실행 중...\n")
        
        for test_name, prompt, max_tokens in test_cases:
            result = self.test_generation(test_name, prompt, max_tokens)
            self.test_results.append(result)
            time.sleep(0.5)  # 테스트 간 짧은 대기
    
    def test_system_prompt(self):
        """시스템 프롬프트 테스트"""
        self.print_section("4. 시스템 프롬프트 테스트")
        
        print("\n  📝 시스템 프롬프트 포함 테스트")
        
        try:
            messages = [[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are a helpful AI assistant that always responds in Korean."}]
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "What is AI?"}]
                }
            ]]
            
            start_time = time.time()
            output = self.pipe(messages, max_new_tokens=60)
            gen_time = time.time() - start_time
            
            response = self.extract_response(output)
            
            if response:
                display_response = response[:100] + "..." if len(response) > 100 else response
                print(f"      응답: {display_response}")
                print(f"      시간: {gen_time:.2f}초")
                
                self.test_results.append({
                    "test": "시스템 프롬프트",
                    "status": "성공",
                    "time": gen_time
                })
                print("\n  ✅ 시스템 프롬프트 정상 작동")
            else:
                print("      ❌ 응답 추출 실패")
                self.test_results.append({
                    "test": "시스템 프롬프트",
                    "status": "응답 추출 실패"
                })
                
        except Exception as e:
            print(f"      ❌ 오류: {e}")
            self.test_results.append({
                "test": "시스템 프롬프트",
                "status": "실패",
                "error": str(e)
            })
    
    def test_performance(self):
        """성능 테스트"""
        self.print_section("5. 성능 테스트")
        
        print("\n  ⚡ 연속 생성 성능 측정 (5회)")
        
        times = []
        test_prompt = "Count from 1 to 5."
        
        for i in range(5):
            messages = [[{
                "role": "user",
                "content": [{"type": "text", "text": test_prompt}]
            }]]
            
            start_time = time.time()
            output = self.pipe(messages, max_new_tokens=30)
            gen_time = time.time() - start_time
            times.append(gen_time)
            
            print(f"      시도 {i+1}: {gen_time:.2f}초")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n  📊 성능 통계:")
        print(f"      평균: {avg_time:.2f}초")
        print(f"      최소: {min_time:.2f}초")
        print(f"      최대: {max_time:.2f}초")
        
        self.test_results.append({
            "test": "성능 측정",
            "status": "성공",
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time
        })
    
    def generate_report(self):
        """테스트 결과 리포트 생성"""
        self.print_header("테스트 결과 리포트", "=")
        
        # 통계
        total_tests = len(self.test_results)
        successful = sum(1 for r in self.test_results if r.get("status") == "성공")
        failed = total_tests - successful
        
        print(f"\n📊 전체 통계:")
        print(f"  • 총 테스트: {total_tests}개")
        print(f"  • 성공: {successful}개 ✅")
        print(f"  • 실패: {failed}개 {'❌' if failed > 0 else '✅'}")
        
        # 성능 요약
        gen_results = [r for r in self.test_results if "time" in r and r.get("status") == "성공" and "prompt" in r]
        
        if gen_results:
            times = [r["time"] for r in gen_results]
            avg_time = sum(times) / len(times)
            
            print(f"\n⚡ 생성 성능:")
            print(f"  • 평균 생성 시간: {avg_time:.2f}초")
            print(f"  • 최소 생성 시간: {min(times):.2f}초")
            print(f"  • 최대 생성 시간: {max(times):.2f}초")
        
        # 실패한 테스트
        failed_tests = [r for r in self.test_results if r.get("status") != "성공"]
        if failed_tests:
            print(f"\n❌ 실패한 테스트:")
            for test in failed_tests:
                print(f"  • {test.get('test', 'Unknown')}: {test.get('error', test.get('status'))}")
        
        # JSON 리포트 저장
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "model_path": str(self.model_path),
                    "summary": {
                        "total": total_tests,
                        "successful": successful,
                        "failed": failed
                    },
                    "results": self.test_results
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 상세 리포트 저장: {report_file}")
        except Exception as e:
            print(f"\n⚠️  리포트 저장 실패: {e}")
        
        # 최종 결과
        print("\n" + "=" * 80)
        if failed == 0:
            print("✅ 모든 테스트 통과! CPU에서 정상 작동합니다.".center(80))
        else:
            print(f"⚠️  {failed}개의 테스트가 실패했습니다.".center(80))
        print("=" * 80 + "\n")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.print_header("Gemma 3 1B IT - 종합 테스트", "=")
        
        print(f"\n테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 모델 파일 확인
        if not self.check_model_exists():
            print("\n❌ 모델 파일이 없어 테스트를 중단합니다.")
            return False
        
        # 2. 모델 로딩
        if not self.load_model():
            print("\n❌ 모델 로딩 실패로 테스트를 중단합니다.")
            return False
        
        # 3. 텍스트 생성 테스트
        self.run_generation_tests()
        
        # 4. 시스템 프롬프트 테스트
        self.test_system_prompt()
        
        # 5. 성능 테스트
        self.test_performance()
        
        # 6. 리포트 생성
        self.generate_report()
        
        return True


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemma 3 1B IT 모델 종합 테스트")
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/gemma-3-1b-it",
        help="모델 경로 (기본값: models/gemma-3-1b-it)"
    )
    
    args = parser.parse_args()
    
    tester = Gemma3Tester(model_path=args.model_path)
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 테스트를 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

