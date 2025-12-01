# ============================================
# 업무 일정 관리 시스템 - 설정 파일
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\config.py
# ============================================

import os

# 현재 파일의 디렉토리 경로
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """기본 설정"""
    
    # Flask 비밀키 (세션 암호화용)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "database", "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 파일 업로드 설정
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 최대 16MB
    ALLOWED_EXTENSIONS = {'hwp', 'hwpx', 'docx', 'doc', 'pdf', 'xlsx', 'xls', 'csv'}
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = 86400  # 24시간 (초)


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True


class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    # 운영 환경에서는 반드시 SECRET_KEY를 환경변수로 설정하세요


# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
