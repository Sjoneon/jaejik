# ============================================
# 업무 일정 관리 시스템 - 문서 모델
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\models\document.py
# ============================================

from datetime import datetime
from models import db


class Document(db.Model):
    """업로드된 문서 모델"""
    
    __tablename__ = 'documents'
    
    # 컬럼 정의
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)  # 원본 파일명
    filepath = db.Column(db.String(500), nullable=False)  # 저장 경로
    file_type = db.Column(db.String(10), nullable=False)  # hwp, docx, pdf
    file_size = db.Column(db.Integer, nullable=True)  # 파일 크기 (bytes)
    extracted_text = db.Column(db.Text, nullable=True)  # 추출된 텍스트
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    schedules = db.relationship('Schedule', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id: int, filename: str, filepath: str, file_type: str, file_size: int = None):
        """
        문서 생성
        
        Args:
            user_id: 업로더 ID
            filename: 원본 파일명
            filepath: 저장 경로
            file_type: 파일 유형
            file_size: 파일 크기
        """
        self.user_id = user_id
        self.filename = filename
        self.filepath = filepath
        self.file_type = file_type.lower()
        self.file_size = file_size
    
    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Document {self.filename}>'
