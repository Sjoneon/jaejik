# ============================================
# 업무 일정 관리 시스템 - 인증 서비스
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\services\auth.py
# ============================================

from typing import Optional, Tuple
from models import db
from models.user import User


class AuthService:
    """인증 관련 서비스"""
    
    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        company_id: int = None,
        team_id: int = None,
        department: str = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        사용자 회원가입
        
        Returns:
            Tuple[성공여부, 메시지, User객체]
        """
        # 입력값 검증
        if not username or len(username) < 2:
            return False, "사용자명은 2자 이상이어야 합니다.", None
        
        if not email or '@' not in email:
            return False, "올바른 이메일 형식이 아닙니다.", None
        
        if not password or len(password) < 4:
            return False, "비밀번호는 4자 이상이어야 합니다.", None
        
        # 중복 검사
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user is not None:
            if existing_user.username == username:
                return False, "이미 사용 중인 사용자명입니다.", None
            else:
                return False, "이미 사용 중인 이메일입니다.", None
        
        try:
            # 새 사용자 생성
            user = User(
                username=username,
                email=email,
                password=password,
                company_id=company_id,
                team_id=team_id,
                department=department
            )
            db.session.add(user)
            db.session.commit()
            
            return True, "회원가입이 완료되었습니다.", user
            
        except Exception as e:
            db.session.rollback()
            return False, f"회원가입 중 오류가 발생했습니다: {str(e)}", None
    
    @staticmethod
    def authenticate_user(username_or_email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        사용자 로그인 인증
        
        Returns:
            Tuple[성공여부, 메시지, User객체]
        """
        if not username_or_email or not password:
            return False, "사용자명/이메일과 비밀번호를 입력해주세요.", None
        
        # 사용자 조회 (사용자명 또는 이메일로)
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user is None:
            return False, "등록되지 않은 사용자입니다.", None
        
        if not user.check_password(password):
            return False, "비밀번호가 일치하지 않습니다.", None
        
        return True, "로그인 성공", user
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        if user_id is None:
            return None
        return User.query.get(user_id)
    
    @staticmethod
    def get_all_users() -> list:
        """모든 사용자 목록 조회"""
        return User.query.order_by(User.username).all()
    
    @staticmethod
    def get_users_by_department(department: str) -> list:
        """부서별 사용자 목록 조회"""
        if not department:
            return []
        return User.query.filter_by(department=department).order_by(User.username).all()
    
    @staticmethod
    def get_users_by_company(company_id: int) -> list:
        """회사별 사용자 목록 조회"""
        if not company_id:
            return []
        return User.query.filter_by(company_id=company_id).order_by(User.username).all()
    
    @staticmethod
    def get_users_by_team(team_id: int) -> list:
        """팀별 사용자 목록 조회"""
        if not team_id:
            return []
        return User.query.filter_by(team_id=team_id).order_by(User.username).all()
