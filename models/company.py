# ============================================
# 업무 일정 관리 시스템 - 회사 모델
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\models\company.py
# ============================================

import secrets
import string
from datetime import datetime
from models import db


class Company(db.Model):
    """회사 모델"""
    
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 회사명
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # 회사 고유코드
    description = db.Column(db.String(200), nullable=True)  # 회사 설명
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 최초 생성자(관리자)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    teams = db.relationship('Team', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    members = db.relationship('User', backref='company', lazy='dynamic', foreign_keys='User.company_id')
    
    def __init__(self, name: str, code: str = None, description: str = None, admin_id: int = None):
        self.name = name
        self.code = code or self.generate_code()
        self.description = description
        self.admin_id = admin_id
    
    @staticmethod
    def generate_code(length: int = 8) -> str:
        """랜덤 회사 코드 생성"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            # 중복 체크
            if not Company.query.filter_by(code=code).first():
                return code
    
    def get_member_count(self) -> int:
        """회사 멤버 수"""
        return self.members.count()
    
    def get_team_count(self) -> int:
        """팀 수"""
        return self.teams.count()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'member_count': self.get_member_count(),
            'team_count': self.get_team_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Company {self.name}>'
