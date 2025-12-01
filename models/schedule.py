# ============================================
# 업무 일정 관리 시스템 - 일정 모델
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\models\schedule.py
# ============================================

from datetime import datetime, date, time
from models import db


class Schedule(db.Model):
    """일정 모델"""
    
    __tablename__ = 'schedules'
    
    # 일정 유형 상수
    TYPE_DEADLINE = 'deadline'      # 마감일
    TYPE_TRIP = 'trip'              # 출장
    TYPE_MEETING = 'meeting'        # 회의
    TYPE_SUBMIT = 'submit'          # 제출
    TYPE_OTHER = 'other'            # 기타
    
    # 컬럼 정의
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True, index=True)
    
    title = db.Column(db.String(200), nullable=False)  # 일정 제목
    task_description = db.Column(db.Text, nullable=False)  # 할 일 내용
    
    # 날짜/시간 정보
    start_date = db.Column(db.Date, nullable=True, index=True)  # 시작일
    due_date = db.Column(db.Date, nullable=False, index=True)  # 마감일/종료일
    end_date = db.Column(db.Date, nullable=True)  # 종료일 (기존 호환용, due_date와 동일 취급)
    start_time = db.Column(db.Time, nullable=True)  # 시작 시간
    end_time = db.Column(db.Time, nullable=True)  # 종료 시간
    is_all_day = db.Column(db.Boolean, default=True)  # 종일 여부
    
    schedule_type = db.Column(db.String(20), default=TYPE_OTHER)  # 일정 유형
    
    tags = db.Column(db.String(200), nullable=True)  # 태그 (쉼표 구분)
    memo = db.Column(db.Text, nullable=True)  # 메모
    is_completed = db.Column(db.Boolean, default=False)  # 완료 여부
    is_ai_generated = db.Column(db.Boolean, default=False)  # AI 생성 여부
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(
        self,
        user_id: int,
        title: str,
        task_description: str,
        due_date: date,
        document_id: int = None,
        start_date: date = None,
        end_date: date = None,
        start_time: time = None,
        end_time: time = None,
        is_all_day: bool = True,
        schedule_type: str = None,
        tags: str = None,
        memo: str = None,
        is_ai_generated: bool = False
    ):
        self.user_id = user_id
        self.title = title
        self.task_description = task_description
        self.due_date = due_date
        self.document_id = document_id
        self.start_date = start_date or due_date  # 시작일 없으면 마감일과 동일
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.is_all_day = is_all_day if start_time is None else False
        self.schedule_type = schedule_type or self.TYPE_OTHER
        self.tags = tags
        self.memo = memo
        self.is_ai_generated = is_ai_generated
    
    @property
    def days_left(self) -> int:
        """남은 일수 계산 (D-day)"""
        if self.due_date is None:
            return 999
        today = date.today()
        delta = self.due_date - today
        return delta.days
    
    @property
    def urgency_level(self) -> str:
        """긴급도 레벨 반환"""
        days = self.days_left
        if self.is_completed:
            return 'completed'
        elif days < 0:
            return 'overdue'  # 지연
        elif days <= 2:
            return 'urgent'   # 긴급 (빨강)
        elif days <= 5:
            return 'soon'     # 임박 (주황)
        elif days <= 7:
            return 'warning'  # 주의 (노랑)
        elif days <= 14:
            return 'normal'   # 여유 (초록)
        else:
            return 'relaxed'  # 먼 일정 (회색)
    
    @property
    def urgency_color(self) -> str:
        """긴급도에 따른 색상 반환"""
        color_map = {
            'completed': '#6c757d',  # 회색
            'overdue': '#dc3545',    # 빨강
            'urgent': '#dc3545',     # 빨강
            'soon': '#fd7e14',       # 주황
            'warning': '#ffc107',    # 노랑
            'normal': '#28a745',     # 초록
            'relaxed': '#adb5bd'     # 연회색
        }
        return color_map.get(self.urgency_level, '#6c757d')
    
    def get_display_time(self) -> str:
        """시간 표시용 문자열"""
        if self.is_all_day:
            return "종일"
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        elif self.start_time:
            return self.start_time.strftime('%H:%M')
        return ""
    
    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_id': self.document_id,
            'title': self.title,
            'task_description': self.task_description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_all_day': self.is_all_day,
            'display_time': self.get_display_time(),
            'schedule_type': self.schedule_type,
            'tags': self.tags,
            'memo': self.memo,
            'is_completed': self.is_completed,
            'is_ai_generated': self.is_ai_generated,
            'days_left': self.days_left,
            'urgency_level': self.urgency_level,
            'urgency_color': self.urgency_color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'document_filename': self.document.filename if self.document else None
        }
    
    def to_calendar_event(self) -> dict:
        """캘린더 이벤트 형식으로 변환 (FullCalendar 호환)"""
        # 시작 시간 결합
        if self.start_date and self.start_time and not self.is_all_day:
            start = datetime.combine(self.start_date, self.start_time).isoformat()
        elif self.start_date:
            start = self.start_date.isoformat()
        else:
            start = self.due_date.isoformat()
        
        # 종료 시간 결합
        end_dt = self.end_date or self.due_date
        if end_dt and self.end_time and not self.is_all_day:
            end = datetime.combine(end_dt, self.end_time).isoformat()
        elif end_dt:
            end = end_dt.isoformat()
        else:
            end = None
        
        return {
            'id': self.id,
            'title': self.title,
            'start': start,
            'end': end,
            'allDay': self.is_all_day,
            'color': self.urgency_color,
            'extendedProps': {
                'task_description': self.task_description,
                'schedule_type': self.schedule_type,
                'is_completed': self.is_completed,
                'document_filename': self.document.filename if self.document else None,
                'days_left': self.days_left,
                'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
                'end_time': self.end_time.strftime('%H:%M') if self.end_time else None
            }
        }
    
    def __repr__(self) -> str:
        return f'<Schedule {self.title} ({self.due_date})>'
