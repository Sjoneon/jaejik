# ============================================
# 업무 일정 관리 시스템 - 모델 패키지
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\models\__init__.py
# ============================================

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 인스턴스 생성
db = SQLAlchemy()


def init_db(app):
    """데이터베이스 초기화 함수"""
    db.init_app(app)
    
    with app.app_context():
        # 모든 모델 import (테이블 생성을 위해)
        from models.user import User
        from models.company import Company
        from models.team import Team
        from models.document import Document
        from models.schedule import Schedule
        
        # 모든 테이블 생성
        db.create_all()
        print("✅ 데이터베이스 테이블이 생성되었습니다.")
