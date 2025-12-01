# ============================================
# 업무 일정 관리 시스템 - 사용자 모델
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\models\user.py
# ============================================

from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from models import db


class User(UserMixin, db.Model):
    """사용자 모델"""
    
    __tablename__ = 'users'
    
    # 권한 상수
    ROLE_MEMBER = 'member'          # 일반 직원
    ROLE_TEAM_LEADER = 'team_leader'  # 팀장
    ROLE_ADMIN = 'admin'            # 회사 관리자
    
    # 컬럼 정의
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 회사/팀 소속 (nullable - 기존 사용자 호환)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True, index=True)
    role = db.Column(db.String(20), default=ROLE_MEMBER)  # 권한
    
    # 기존 department 필드 유지 (하위 호환)
    department = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    documents = db.relationship('Document', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username: str, email: str, password: str, 
                 company_id: int = None, team_id: int = None, 
                 role: str = None, department: str = None):
        """
        사용자 생성
        """
        self.username = username
        self.email = email
        self.set_password(password)
        self.company_id = company_id
        self.team_id = team_id
        self.role = role or self.ROLE_MEMBER
        self.department = department
    
    def set_password(self, password: str) -> None:
        """비밀번호 해시화 저장"""
        if password is None or len(password) < 4:
            raise ValueError("비밀번호는 4자 이상이어야 합니다.")
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """비밀번호 검증"""
        if password is None or self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """회사 관리자인지 확인"""
        return self.role == self.ROLE_ADMIN
    
    def is_team_leader(self) -> bool:
        """팀장인지 확인"""
        return self.role == self.ROLE_TEAM_LEADER or self.role == self.ROLE_ADMIN
    
    def get_company_name(self) -> str:
        """소속 회사명"""
        if self.company:
            return self.company.name
        return None
    
    def get_team_name(self) -> str:
        """소속 팀명"""
        if self.team:
            return self.team.name
        return self.department  # 기존 호환
    
    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'company_id': self.company_id,
            'company_name': self.get_company_name(),
            'team_id': self.team_id,
            'team_name': self.get_team_name(),
            'role': self.role,
            'department': self.department,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
