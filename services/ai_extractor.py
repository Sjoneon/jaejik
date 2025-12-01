# ============================================
# 업무 일정 관리 시스템 - AI 일정 추출 서비스
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\services\ai_extractor.py
# Groq API 사용 (Qwen3-32B)
# ============================================

import os
import re
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from dateutil import parser as date_parser


class AIScheduleExtractor:
    """AI를 활용한 일정 추출 서비스 (Groq API)"""
    
    def __init__(self, api_key: str = None):
        """
        AI 추출기 초기화
        
        Args:
            api_key: Groq API 키 (기본: 환경변수 GROQ_API_KEY)
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = None
        self._api_ready = False
    
    def load_model(self) -> bool:
        """Groq API 연결 확인"""
        if self._api_ready:
            return True
        
        if not self.api_key:
            print("❌ GROQ_API_KEY가 설정되지 않았습니다.")
            print("⚠️ 규칙 기반 추출만 사용합니다.")
            return False
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self._api_ready = True
            print("✅ Groq API 연결됨")
            return True
            
        except ImportError:
            print("❌ groq 라이브러리가 설치되지 않았습니다.")
            print("   pip install groq")
            return False
        except Exception as e:
            print(f"❌ Groq API 연결 실패: {str(e)}")
            print("⚠️ 규칙 기반 추출만 사용합니다.")
            return False
    
    def extract_schedules(self, text: str) -> List[Dict[str, Any]]:
        """
        텍스트에서 일정 정보 추출
        
        Args:
            text: 문서에서 추출된 텍스트
            
        Returns:
            추출된 일정 목록
        """
        if not text or not text.strip():
            return []
        
        schedules = []
        
        # 1. AI 기반 추출 (우선) - Groq API가 준비된 경우
        if self._api_ready and self.client is not None:
            try:
                ai_schedules = self._extract_by_ai(text)
                schedules.extend(ai_schedules)
                print(f"🤖 AI가 {len(ai_schedules)}개 일정 추출")
            except Exception as e:
                print(f"⚠️ AI 추출 중 오류: {str(e)}")
        
        # 2. 규칙 기반 추출 (보조/백업)
        rule_based_schedules = self._extract_by_rules(text)
        
        # AI 결과가 없으면 규칙 기반 결과 사용
        if not schedules:
            schedules = rule_based_schedules
            print(f"📋 규칙 기반으로 {len(schedules)}개 일정 추출")
        else:
            # AI 결과가 있으면 규칙 기반에서 누락된 것만 추가
            for rule_schedule in rule_based_schedules:
                if not self._is_duplicate(rule_schedule, schedules):
                    schedules.append(rule_schedule)
        
        return schedules
    
    def _extract_by_ai(self, text: str) -> List[Dict[str, Any]]:
        """Groq API를 사용한 AI 기반 일정 추출"""
        if not self._api_ready or self.client is None:
            return []
        
        # 텍스트가 너무 길면 앞부분만 사용
        max_length = 2000
        if len(text) > max_length:
            text = text[:max_length] + "\n...(이하 생략)"
        
        today = date.today().strftime("%Y-%m-%d")
        
        prompt = f"""당신은 문서에서 일정 정보를 추출하는 전문가입니다.
오늘 날짜: {today}

다음 문서에서 모든 일정, 마감일, 회의, 출장, 제출 기한 등을 찾아 JSON 배열로 출력하세요.

규칙:
1. 날짜는 YYYY-MM-DD 형식으로 변환
2. 날짜가 "12월 5일" 같이 연도가 없으면 2025년으로 가정
3. 과거 날짜는 제외
4. 각 일정마다 title, date, type(deadline/meeting/trip/submit/other), description 포함

문서 내용:
---
{text}
---

JSON 배열만 출력하세요 (다른 설명 없이):"""

        try:
            completion = self.client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=2048,
                top_p=0.95,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            return self._parse_ai_response(response_text)
            
        except Exception as e:
            print(f"⚠️ Groq API 호출 오류: {str(e)}")
            return []
    
    def _parse_ai_response(self, response: str) -> List[Dict[str, Any]]:
        """AI 응답 파싱"""
        schedules = []
        
        if not response:
            return []
        
        # JSON 배열 찾기
        # 마크다운 코드 블록 제거
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        response = response.strip()
        
        try:
            # JSON 배열 파싱
            data = json.loads(response)
            
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'schedules' in data:
                items = data['schedules']
            elif isinstance(data, dict):
                items = [data]
            else:
                return []
            
            for item in items:
                schedule = self._convert_ai_item(item)
                if schedule:
                    schedules.append(schedule)
                    
        except json.JSONDecodeError:
            # JSON 파싱 실패시 개별 객체 찾기
            json_matches = re.findall(r'\{[^{}]+\}', response)
            for match in json_matches:
                try:
                    item = json.loads(match)
                    schedule = self._convert_ai_item(item)
                    if schedule:
                        schedules.append(schedule)
                except:
                    continue
        
        return schedules
    
    def _convert_ai_item(self, item: dict) -> Optional[Dict[str, Any]]:
        """AI 응답 아이템을 일정 형식으로 변환"""
        try:
            # 날짜 추출
            date_str = item.get('date') or item.get('날짜') or item.get('due_date')
            if not date_str:
                return None
            
            # 날짜 파싱
            try:
                if isinstance(date_str, str):
                    parsed_date = date_parser.parse(date_str).date()
                else:
                    return None
            except:
                return None
            
            # 과거 날짜 제외
            if parsed_date < date.today():
                return None
            
            # 제목/설명 추출
            title = item.get('title') or item.get('제목') or item.get('task') or ""
            description = item.get('description') or item.get('설명') or item.get('task_description') or title
            schedule_type = item.get('type') or item.get('유형') or item.get('schedule_type') or 'other'
            
            # 유형 정규화
            type_mapping = {
                '마감': 'deadline', '기한': 'deadline', 'deadline': 'deadline',
                '회의': 'meeting', '미팅': 'meeting', 'meeting': 'meeting',
                '출장': 'trip', '방문': 'trip', 'trip': 'trip',
                '제출': 'submit', '보고': 'submit', 'submit': 'submit',
            }
            schedule_type = type_mapping.get(str(schedule_type).lower(), 'other') if schedule_type else 'other'
            
            if not title:
                title = description[:50] if description else "일정"
            
            return {
                'title': self._generate_title(title, schedule_type),
                'task_description': description,
                'due_date': parsed_date,
                'schedule_type': schedule_type,
                'is_ai_generated': True
            }
            
        except Exception as e:
            print(f"⚠️ 아이템 변환 오류: {str(e)}")
            return None
    
    def _extract_by_rules(self, text: str) -> List[Dict[str, Any]]:
        """규칙 기반 일정 추출"""
        schedules = []
        
        # 날짜 패턴들
        date_patterns = [
            # YYYY년 MM월 DD일
            r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',
            # YYYY.MM.DD 또는 YYYY-MM-DD
            r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})',
            # MM월 DD일 (올해로 가정)
            r'(\d{1,2})월\s*(\d{1,2})일',
            # MM/DD
            r'(\d{1,2})[/](\d{1,2})(?!\d)',
        ]
        
        # 키워드 패턴들 (일정 유형 판별용)
        keyword_patterns = {
            'deadline': [
                r'까지', r'마감', r'기한', r'제출일', r'납기',
                r'데드라인', r'deadline', r'due'
            ],
            'submit': [
                r'제출', r'보고', r'보내', r'발송', r'송부',
                r'submit', r'report'
            ],
            'trip': [
                r'출장', r'방문', r'미팅', r'외근',
                r'trip', r'visit'
            ],
            'meeting': [
                r'회의', r'미팅', r'간담회', r'협의', r'회합',
                r'meeting', r'conference'
            ]
        }
        
        # 텍스트를 문장 단위로 분리
        sentences = re.split(r'[.\n]', text)
        
        current_year = datetime.now().year
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 5:
                continue
            
            # 날짜 찾기
            found_date = None
            
            for pattern in date_patterns:
                match = re.search(pattern, sentence)
                if match:
                    groups = match.groups()
                    try:
                        if len(groups) == 3:
                            year = int(groups[0])
                            month = int(groups[1])
                            day = int(groups[2])
                            # 연도가 너무 작으면 현재 연도로 대체
                            if year < 2000:
                                year = current_year
                        elif len(groups) == 2:
                            year = current_year
                            month = int(groups[0])
                            day = int(groups[1])
                        else:
                            continue
                        
                        # 유효한 날짜인지 확인
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            found_date = date(year, month, day)
                            # 과거 날짜면 다음 해로
                            if found_date < date.today():
                                found_date = date(year + 1, month, day)
                            break
                    except ValueError:
                        continue
            
            if found_date is None:
                continue
            
            # 일정 유형 판별
            schedule_type = 'other'
            for stype, keywords in keyword_patterns.items():
                for keyword in keywords:
                    if re.search(keyword, sentence, re.IGNORECASE):
                        schedule_type = stype
                        break
                if schedule_type != 'other':
                    break
            
            # 할 일 내용 추출 (문장 정리)
            task_description = self._clean_task_description(sentence)
            
            # 제목 생성
            title = self._generate_title(task_description, schedule_type)
            
            schedule = {
                'title': title,
                'task_description': task_description,
                'due_date': found_date,
                'schedule_type': schedule_type,
                'is_ai_generated': False  # 규칙 기반
            }
            
            # 중복 확인 후 추가
            if not self._is_duplicate(schedule, schedules):
                schedules.append(schedule)
        
        return schedules
    
    def _clean_task_description(self, sentence: str) -> str:
        """할 일 설명 정리"""
        # 불필요한 공백 제거
        cleaned = ' '.join(sentence.split())
        
        # 너무 길면 자르기
        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."
        
        return cleaned
    
    def _generate_title(self, description: str, schedule_type: str) -> str:
        """제목 생성"""
        # 유형별 접두어
        type_prefix = {
            'deadline': '📅 마감: ',
            'submit': '📤 제출: ',
            'trip': '🚗 출장: ',
            'meeting': '👥 회의: ',
            'other': '📋 '
        }
        
        prefix = type_prefix.get(schedule_type, '📋 ')
        
        # 제목은 간결하게
        title = description[:50]
        if len(description) > 50:
            title += "..."
        
        return prefix + title
    
    def _is_duplicate(self, new_schedule: Dict, existing: List[Dict]) -> bool:
        """중복 일정 확인"""
        for schedule in existing:
            # 같은 날짜에 비슷한 내용이면 중복
            if schedule.get('due_date') == new_schedule.get('due_date'):
                existing_task = schedule.get('task_description', '').lower()
                new_task = new_schedule.get('task_description', '').lower()
                
                # 70% 이상 유사하면 중복으로 판단
                if self._text_similarity(existing_task, new_task) > 0.7:
                    return True
        
        return False
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """간단한 텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


# 싱글톤 인스턴스
_extractor_instance = None


def get_extractor(api_key: str = None) -> AIScheduleExtractor:
    """추출기 인스턴스 반환"""
    global _extractor_instance
    
    if _extractor_instance is None:
        _extractor_instance = AIScheduleExtractor(api_key)
        _extractor_instance.load_model()
    
    return _extractor_instance
