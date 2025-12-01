# ============================================
# 업무 일정 관리 시스템 - 팀 모델
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\models\team.py
# ============================================

import secrets
import string
from datetime import datetime
from models import db


class Team(db.Model):
    """팀 모델"""
    
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)  # 팀명
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # 팀 고유코드
    description = db.Column(db.String(200), nullable=True)  # 팀 설명
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 팀장
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    members = db.relationship('User', backref='team', lazy='dynamic', foreign_keys='User.team_id')
    
    def __init__(self, company_id: int, name: str, code: str = None, description: str = None, leader_id: int = None):
        self.company_id = company_id
        self.name = name
        self.code = code or self.generate_code()
        self.description = description
        self.leader_id = leader_id
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """랜덤 팀 코드 생성"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            # 중복 체크
            if not Team.query.filter_by(code=code).first():
                return code
    
    def get_member_count(self) -> int:
        """팀 멤버 수"""
        return self.members.count()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'leader_id': self.leader_id,
            'member_count': self.get_member_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Team {self.name}>'
