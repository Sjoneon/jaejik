# ============================================
# 업무 일정 관리 시스템 - 회사/팀 관리 서비스
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\services\company_service.py
# ============================================

from typing import Optional, Tuple, List
from models import db
from models.company import Company
from models.team import Team
from models.user import User


class CompanyService:
    """회사 관리 서비스"""
    
    @staticmethod
    def create_company(name: str, admin_user: User, description: str = None) -> Tuple[bool, str, Optional[Company]]:
        """
        회사 생성
        
        Args:
            name: 회사명
            admin_user: 관리자가 될 사용자
            description: 회사 설명
            
        Returns:
            Tuple[성공여부, 메시지, Company객체]
        """
        if not name or len(name) < 2:
            return False, "회사명은 2자 이상이어야 합니다.", None
        
        # 중복 회사명 체크
        existing = Company.query.filter_by(name=name).first()
        if existing:
            return False, "이미 존재하는 회사명입니다.", None
        
        try:
            # 회사 생성
            company = Company(
                name=name,
                description=description,
                admin_id=admin_user.id
            )
            db.session.add(company)
            db.session.flush()  # ID 생성
            
            # 사용자를 관리자로 설정
            admin_user.company_id = company.id
            admin_user.role = User.ROLE_ADMIN
            
            db.session.commit()
            
            return True, f"회사가 생성되었습니다. 회사코드: {company.code}", company
            
        except Exception as e:
            db.session.rollback()
            return False, f"회사 생성 중 오류: {str(e)}", None
    
    @staticmethod
    def join_company(code: str, user: User) -> Tuple[bool, str, Optional[Company]]:
        """
        회사 가입 (코드로)
        
        Args:
            code: 회사 코드
            user: 가입할 사용자
            
        Returns:
            Tuple[성공여부, 메시지, Company객체]
        """
        if not code:
            return False, "회사 코드를 입력해주세요.", None
        
        company = Company.query.filter_by(code=code.upper()).first()
        
        if not company:
            return False, "존재하지 않는 회사 코드입니다.", None
        
        if user.company_id == company.id:
            return False, "이미 해당 회사에 소속되어 있습니다.", None
        
        try:
            user.company_id = company.id
            user.role = User.ROLE_MEMBER
            db.session.commit()
            
            return True, f"{company.name}에 가입되었습니다.", company
            
        except Exception as e:
            db.session.rollback()
            return False, f"회사 가입 중 오류: {str(e)}", None
    
    @staticmethod
    def get_company_by_code(code: str) -> Optional[Company]:
        """코드로 회사 조회"""
        if not code:
            return None
        return Company.query.filter_by(code=code.upper()).first()
    
    @staticmethod
    def get_company_members(company_id: int) -> List[User]:
        """회사 멤버 목록"""
        return User.query.filter_by(company_id=company_id).order_by(User.username).all()
    
    @staticmethod
    def get_company_teams(company_id: int) -> List[Team]:
        """회사 팀 목록"""
        return Team.query.filter_by(company_id=company_id).order_by(Team.name).all()


class TeamService:
    """팀 관리 서비스"""
    
    @staticmethod
    def create_team(company_id: int, name: str, leader_user: User = None, description: str = None) -> Tuple[bool, str, Optional[Team]]:
        """
        팀 생성
        
        Args:
            company_id: 회사 ID
            name: 팀명
            leader_user: 팀장이 될 사용자
            description: 팀 설명
            
        Returns:
            Tuple[성공여부, 메시지, Team객체]
        """
        if not name or len(name) < 2:
            return False, "팀명은 2자 이상이어야 합니다.", None
        
        # 같은 회사 내 중복 팀명 체크
        existing = Team.query.filter_by(company_id=company_id, name=name).first()
        if existing:
            return False, "이미 존재하는 팀명입니다.", None
        
        try:
            # 팀 생성
            team = Team(
                company_id=company_id,
                name=name,
                description=description,
                leader_id=leader_user.id if leader_user else None
            )
            db.session.add(team)
            db.session.flush()
            
            # 팀장 설정
            if leader_user:
                leader_user.team_id = team.id
                leader_user.role = User.ROLE_TEAM_LEADER
            
            db.session.commit()
            
            return True, f"팀이 생성되었습니다. 팀코드: {team.code}", team
            
        except Exception as e:
            db.session.rollback()
            return False, f"팀 생성 중 오류: {str(e)}", None
    
    @staticmethod
    def join_team(code: str, user: User) -> Tuple[bool, str, Optional[Team]]:
        """
        팀 가입 (코드로)
        
        Args:
            code: 팀 코드
            user: 가입할 사용자
            
        Returns:
            Tuple[성공여부, 메시지, Team객체]
        """
        if not code:
            return False, "팀 코드를 입력해주세요.", None
        
        team = Team.query.filter_by(code=code.upper()).first()
        
        if not team:
            return False, "존재하지 않는 팀 코드입니다.", None
        
        # 같은 회사인지 확인
        if user.company_id != team.company_id:
            return False, "다른 회사의 팀에는 가입할 수 없습니다.", None
        
        if user.team_id == team.id:
            return False, "이미 해당 팀에 소속되어 있습니다.", None
        
        try:
            user.team_id = team.id
            # 권한은 유지 (이미 팀장이면 팀장으로 유지)
            if user.role == User.ROLE_MEMBER:
                user.role = User.ROLE_MEMBER
            db.session.commit()
            
            return True, f"{team.name}팀에 가입되었습니다.", team
            
        except Exception as e:
            db.session.rollback()
            return False, f"팀 가입 중 오류: {str(e)}", None
    
    @staticmethod
    def get_team_by_code(code: str) -> Optional[Team]:
        """코드로 팀 조회"""
        if not code:
            return None
        return Team.query.filter_by(code=code.upper()).first()
    
    @staticmethod
    def get_team_members(team_id: int) -> List[User]:
        """팀 멤버 목록"""
        return User.query.filter_by(team_id=team_id).order_by(User.username).all()
    
    @staticmethod
    def leave_team(user: User) -> Tuple[bool, str]:
        """팀 탈퇴"""
        if not user.team_id:
            return False, "소속된 팀이 없습니다."
        
        try:
            team_name = user.team.name if user.team else "팀"
            user.team_id = None
            if user.role == User.ROLE_TEAM_LEADER:
                user.role = User.ROLE_MEMBER
            db.session.commit()
            
            return True, f"{team_name}에서 탈퇴했습니다."
            
        except Exception as e:
            db.session.rollback()
            return False, f"팀 탈퇴 중 오류: {str(e)}"
