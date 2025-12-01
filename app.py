# ============================================
# 업무 일정 관리 시스템 - 메인 애플리케이션
# 위치: C:\Users\user\Desktop\인공지능산업협회AI\app.py
# ============================================

import os
import sys
from datetime import datetime, date
from functools import wraps

# 환경 변수 로딩 (.env 파일)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env 파일 로드됨")
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. pip install python-dotenv")

# Flask 관련
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# 설정
from config import Config

# 모델
from models import db, init_db
from models.user import User
from models.company import Company
from models.team import Team
from models.document import Document
from models.schedule import Schedule

# 서비스
from services.auth import AuthService
from services.document_parser import DocumentParser
from services.ai_extractor import AIScheduleExtractor, get_extractor
from services.company_service import CompanyService, TeamService


# ============================================
# 앱 생성 및 설정
# ============================================

def create_app():
    """Flask 앱 팩토리"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 폴더 생성 (없으면)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)
    
    # 데이터베이스 초기화
    init_db(app)
    
    # 로그인 매니저 설정
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return AuthService.get_user_by_id(int(user_id))
    
    return app


app = create_app()

# AI 추출기 (전역)
ai_extractor = None


def get_ai_extractor():
    """AI 추출기 인스턴스 반환 (Groq API)"""
    global ai_extractor
    if ai_extractor is None:
        ai_extractor = AIScheduleExtractor()
        ai_extractor.load_model()
    return ai_extractor


# ============================================
# 유틸리티 함수
# ============================================

def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config['ALLOWED_EXTENSIONS']


def get_user_stats(user_id):
    """사용자 일정 통계 계산"""
    today = date.today()
    
    total = Schedule.query.filter_by(user_id=user_id).count()
    completed = Schedule.query.filter_by(user_id=user_id, is_completed=True).count()
    pending = Schedule.query.filter_by(user_id=user_id, is_completed=False).count()
    overdue = Schedule.query.filter(
        Schedule.user_id == user_id,
        Schedule.is_completed == False,
        Schedule.due_date < today
    ).count()
    
    completion_rate = round((completed / total * 100) if total > 0 else 0)
    
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'completion_rate': completion_rate
    }


# ============================================
# 인증 라우트
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        success, message, user = AuthService.authenticate_user(username, password)
        
        if success and user:
            login_user(user, remember=True)
            flash('환영합니다!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 페이지"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        company_code = request.form.get('company_code', '').strip().upper() or None
        team_code = request.form.get('team_code', '').strip().upper() or None
        
        # 비밀번호 확인
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html')
        
        # 회사 코드 확인
        company = None
        team = None
        
        if company_code:
            company = CompanyService.get_company_by_code(company_code)
            if not company:
                flash('존재하지 않는 회사 코드입니다.', 'error')
                return render_template('register.html')
        
        # 팀 코드 확인
        if team_code:
            team = TeamService.get_team_by_code(team_code)
            if not team:
                flash('존재하지 않는 팀 코드입니다.', 'error')
                return render_template('register.html')
            
            # 팀의 회사와 입력한 회사가 일치하는지 확인
            if company and team.company_id != company.id:
                flash('해당 팀은 입력하신 회사에 속하지 않습니다.', 'error')
                return render_template('register.html')
            
            # 회사코드 없이 팀코드만 입력한 경우, 팀의 회사로 설정
            if not company:
                company = team.company
        
        success, message, user = AuthService.register_user(
            username=username,
            email=email,
            password=password,
            company_id=company.id if company else None,
            team_id=team.id if team else None
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """로그아웃"""
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))


# ============================================
# 메인 라우트
# ============================================

@app.route('/')
def index():
    """메인 페이지 - 로그인 여부에 따라 리다이렉트"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """대시보드 페이지"""
    # 사용자의 일정 목록 (마감일 순, 완료되지 않은 것 우선)
    schedules = Schedule.query.filter_by(user_id=current_user.id)\
        .order_by(Schedule.is_completed.asc(), Schedule.due_date.asc())\
        .all()
    
    # 통계
    stats = get_user_stats(current_user.id)
    
    return render_template('dashboard.html', schedules=schedules, stats=stats)


# ============================================
# 일정 라우트
# ============================================

@app.route('/schedule/add', methods=['POST'])
@login_required
def add_schedule():
    """새 일정 추가"""
    try:
        title = request.form.get('title', '').strip()
        task_description = request.form.get('task_description', '').strip()
        start_date_str = request.form.get('start_date', '')
        due_date_str = request.form.get('due_date', '')
        start_time_str = request.form.get('start_time', '')
        end_time_str = request.form.get('end_time', '')
        is_all_day = 'is_all_day' in request.form
        schedule_type = request.form.get('schedule_type', 'other')
        tags = request.form.get('tags', '').strip() or None
        memo = request.form.get('memo', '').strip() or None
        
        if not title or not task_description or not due_date_str:
            flash('제목, 할 일 내용, 종료일은 필수입니다.', 'error')
            return redirect(url_for('dashboard'))
        
        # 날짜 파싱
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else due_date
        
        # 시간 파싱
        from datetime import time
        start_time = None
        end_time = None
        
        if not is_all_day and start_time_str:
            try:
                parts = start_time_str.split(':')
                start_time = time(int(parts[0]), int(parts[1]))
            except:
                pass
        
        if not is_all_day and end_time_str:
            try:
                parts = end_time_str.split(':')
                end_time = time(int(parts[0]), int(parts[1]))
            except:
                pass
        
        # 일정 생성
        schedule = Schedule(
            user_id=current_user.id,
            title=title,
            task_description=task_description,
            start_date=start_date,
            due_date=due_date,
            start_time=start_time,
            end_time=end_time,
            is_all_day=is_all_day,
            schedule_type=schedule_type,
            tags=tags,
            memo=memo,
            is_ai_generated=False
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        flash('일정이 추가되었습니다.', 'success')
        
    except ValueError as e:
        flash(f'날짜 형식이 올바르지 않습니다.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'일정 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/schedule/<int:schedule_id>/update', methods=['POST'])
@login_required
def update_schedule(schedule_id):
    """일정 수정"""
    schedule = Schedule.query.filter_by(id=schedule_id, user_id=current_user.id).first()
    
    if not schedule:
        flash('일정을 찾을 수 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        schedule.title = request.form.get('title', schedule.title).strip()
        schedule.task_description = request.form.get('task_description', schedule.task_description).strip()
        
        # 날짜 파싱
        start_date_str = request.form.get('start_date', '')
        if start_date_str:
            schedule.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        due_date_str = request.form.get('due_date', '')
        if due_date_str:
            schedule.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        
        # 종일 여부
        schedule.is_all_day = 'is_all_day' in request.form
        
        # 시간 파싱
        from datetime import time
        start_time_str = request.form.get('start_time', '')
        end_time_str = request.form.get('end_time', '')
        
        if not schedule.is_all_day and start_time_str:
            try:
                parts = start_time_str.split(':')
                schedule.start_time = time(int(parts[0]), int(parts[1]))
            except:
                schedule.start_time = None
        else:
            schedule.start_time = None
        
        if not schedule.is_all_day and end_time_str:
            try:
                parts = end_time_str.split(':')
                schedule.end_time = time(int(parts[0]), int(parts[1]))
            except:
                schedule.end_time = None
        else:
            schedule.end_time = None
        
        schedule.schedule_type = request.form.get('schedule_type', schedule.schedule_type)
        schedule.tags = request.form.get('tags', '').strip() or None
        schedule.memo = request.form.get('memo', '').strip() or None
        schedule.is_completed = 'is_completed' in request.form
        
        db.session.commit()
        flash('일정이 수정되었습니다.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'일정 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/schedule/<int:schedule_id>/edit', methods=['POST'])
@login_required
def edit_schedule(schedule_id):
    """일정 수정 (별칭)"""
    return update_schedule(schedule_id)


@app.route('/schedule/<int:schedule_id>/delete', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    """일정 삭제"""
    schedule = Schedule.query.filter_by(id=schedule_id, user_id=current_user.id).first()
    
    if not schedule:
        return jsonify({'success': False, 'message': '일정을 찾을 수 없습니다.'})
    
    try:
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({'success': True, 'message': '일정이 삭제되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '삭제 중 오류가 발생했습니다.'})


@app.route('/schedule/<int:schedule_id>/complete', methods=['POST'])
@login_required
def complete_schedule(schedule_id):
    """일정 완료 처리"""
    schedule = Schedule.query.filter_by(id=schedule_id, user_id=current_user.id).first()
    
    if not schedule:
        return jsonify({'success': False, 'message': '일정을 찾을 수 없습니다.'})
    
    try:
        schedule.is_completed = True
        db.session.commit()
        return jsonify({'success': True, 'message': '일정이 완료되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '처리 중 오류가 발생했습니다.'})


# ============================================
# 문서 업로드 및 AI 분석
# ============================================

@app.route('/upload', methods=['POST'])
@login_required
def upload_document():
    """문서 업로드 및 AI 일정 추출"""
    if 'document' not in request.files:
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['document']
    
    if file.filename == '':
        flash('파일이 선택되지 않았습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    if not allowed_file(file.filename):
        flash('지원하지 않는 파일 형식입니다. (HWP, DOCX, PDF만 지원)', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # 파일 저장
        filename = secure_filename(file.filename)
        # 한글 파일명 처리
        original_filename = file.filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 원본 파일명에서 확장자 추출 (secure_filename 한글 문제 방지)
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        
        # 저장 파일명: 사용자ID_타임스탬프.확장자
        save_filename = f"{current_user.id}_{timestamp}.{file_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_filename)
        
        file.save(filepath)
        
        # 파일 정보
        file_size = os.path.getsize(filepath)
        
        # Document 레코드 생성
        document = Document(
            user_id=current_user.id,
            filename=original_filename,
            filepath=filepath,
            file_type=file_ext,
            file_size=file_size
        )
        
        # 문서 파싱
        success, message, extracted_text = DocumentParser.parse(filepath)
        
        if success and extracted_text:
            document.extracted_text = extracted_text
            
            # AI 일정 추출
            extractor = get_ai_extractor()
            schedules_data = extractor.extract_schedules(extracted_text)
            
            db.session.add(document)
            db.session.flush()  # document.id 생성
            
            # 추출된 일정 저장
            created_count = 0
            for sched_data in schedules_data:
                schedule = Schedule(
                    user_id=current_user.id,
                    document_id=document.id,
                    title=sched_data.get('title', '새 일정'),
                    task_description=sched_data.get('task_description', ''),
                    due_date=sched_data.get('due_date'),
                    schedule_type=sched_data.get('schedule_type', 'other'),
                    is_ai_generated=True
                )
                db.session.add(schedule)
                created_count += 1
            
            db.session.commit()
            
            if created_count > 0:
                flash(f'문서에서 {created_count}개의 일정이 추출되었습니다.', 'success')
            else:
                flash('문서를 분석했지만 일정을 찾지 못했습니다. 직접 일정을 추가해주세요.', 'info')
        else:
            db.session.add(document)
            db.session.commit()
            flash(f'문서가 업로드되었습니다. (텍스트 추출: {message})', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'파일 업로드 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/files')
@login_required
def file_archive():
    """파일 보관함"""
    documents = Document.query.filter_by(user_id=current_user.id)\
        .order_by(Document.uploaded_at.desc()).all()
    return render_template('files.html', documents=documents)


# ============================================
# API 엔드포인트
# ============================================

@app.route('/api/schedules')
@login_required
def api_get_schedules():
    """캘린더용 일정 API"""
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    events = [schedule.to_calendar_event() for schedule in schedules]
    return jsonify(events)


@app.route('/api/schedule/<int:schedule_id>')
@login_required
def api_get_schedule(schedule_id):
    """일정 상세 API"""
    schedule = Schedule.query.filter_by(id=schedule_id, user_id=current_user.id).first()
    
    if not schedule:
        return jsonify({'success': False, 'message': '일정을 찾을 수 없습니다.'})
    
    return jsonify({'success': True, 'schedule': schedule.to_dict()})


@app.route('/api/team-schedules')
@login_required
def api_get_team_schedules():
    """팀원 일정 API"""
    users = []
    
    # 팀이 있으면 같은 팀 멤버
    if current_user.team_id:
        users = AuthService.get_users_by_team(current_user.team_id)
    # 팀이 없고 회사가 있으면 같은 회사 멤버
    elif current_user.company_id:
        users = AuthService.get_users_by_company(current_user.company_id)
    # 둘 다 없으면 기존 department 기반 (하위 호환)
    elif current_user.department:
        users = AuthService.get_users_by_department(current_user.department)
    
    team_schedules = {}
    today = date.today()
    
    for user in users:
        if user.id == current_user.id:
            continue  # 본인 제외
        
        schedules = Schedule.query.filter(
            Schedule.user_id == user.id,
            Schedule.is_completed == False,
            Schedule.due_date >= today
        ).order_by(Schedule.due_date.asc()).limit(5).all()
        
        if schedules:
            team_schedules[user.username] = [
                {'title': s.title, 'due_date': s.due_date.isoformat()}
                for s in schedules
            ]
    
    return jsonify({'success': True, 'team_schedules': team_schedules})


@app.route('/api/search')
@login_required
def api_search():
    """일정 검색 API"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'success': False, 'message': '2자 이상 입력하세요.'})
    
    schedules = Schedule.query.filter(
        Schedule.user_id == current_user.id,
        (Schedule.title.ilike(f'%{query}%') | Schedule.task_description.ilike(f'%{query}%'))
    ).order_by(Schedule.due_date.asc()).limit(20).all()
    
    return jsonify({
        'success': True,
        'schedules': [
            {'id': s.id, 'title': s.title, 'due_date': s.due_date.isoformat()}
            for s in schedules
        ]
    })


@app.route('/api/document/<int:doc_id>/text')
@login_required
def api_get_document_text(doc_id):
    """문서 추출 텍스트 API"""
    document = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()
    
    if not document:
        return jsonify({'success': False, 'message': '문서를 찾을 수 없습니다.'})
    
    return jsonify({
        'success': True,
        'text': document.extracted_text or '추출된 텍스트가 없습니다.',
        'filename': document.filename
    })


# ============================================
# 회사/팀 관리 라우트
# ============================================

@app.route('/company')
@login_required
def company_page():
    """회사/팀 관리 페이지"""
    company = None
    teams = []
    members = []
    
    if current_user.company_id:
        company = Company.query.get(current_user.company_id)
        if company:
            teams = CompanyService.get_company_teams(company.id)
            members = CompanyService.get_company_members(company.id)
    
    return render_template('company.html', 
                         company=company, 
                         teams=teams, 
                         members=members)


@app.route('/company/create', methods=['POST'])
@login_required
def create_company():
    """회사 생성"""
    if current_user.company_id:
        flash('이미 회사에 소속되어 있습니다.', 'error')
        return redirect(url_for('company_page'))
    
    name = request.form.get('company_name', '').strip()
    description = request.form.get('description', '').strip() or None
    
    if not name:
        flash('회사명을 입력해주세요.', 'error')
        return redirect(url_for('company_page'))
    
    success, message, company = CompanyService.create_company(
        name=name,
        admin_user=current_user,
        description=description
    )
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('company_page'))


@app.route('/company/join', methods=['POST'])
@login_required
def join_company():
    """회사 가입"""
    code = request.form.get('company_code', '').strip()
    
    if not code:
        flash('회사 코드를 입력해주세요.', 'error')
        return redirect(url_for('company_page'))
    
    success, message, company = CompanyService.join_company(code, current_user)
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('company_page'))


@app.route('/team/create', methods=['POST'])
@login_required
def create_team():
    """팀 생성"""
    if not current_user.company_id:
        flash('먼저 회사에 가입해주세요.', 'error')
        return redirect(url_for('company_page'))
    
    # 관리자 또는 팀장만 팀 생성 가능
    if not current_user.is_admin() and not current_user.is_team_leader():
        flash('팀 생성 권한이 없습니다.', 'error')
        return redirect(url_for('company_page'))
    
    name = request.form.get('team_name', '').strip()
    description = request.form.get('description', '').strip() or None
    
    if not name:
        flash('팀명을 입력해주세요.', 'error')
        return redirect(url_for('company_page'))
    
    success, message, team = TeamService.create_team(
        company_id=current_user.company_id,
        name=name,
        leader_user=current_user,
        description=description
    )
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('company_page'))


@app.route('/team/join', methods=['POST'])
@login_required
def join_team():
    """팀 가입"""
    code = request.form.get('team_code', '').strip()
    
    if not code:
        flash('팀 코드를 입력해주세요.', 'error')
        return redirect(url_for('company_page'))
    
    success, message, team = TeamService.join_team(code, current_user)
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('company_page'))


@app.route('/team/leave', methods=['POST'])
@login_required
def leave_team():
    """팀 탈퇴"""
    success, message = TeamService.leave_team(current_user)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('company_page'))


@app.route('/api/company/teams')
@login_required
def api_get_company_teams():
    """회사 팀 목록 API"""
    if not current_user.company_id:
        return jsonify({'success': False, 'teams': []})
    
    teams = CompanyService.get_company_teams(current_user.company_id)
    return jsonify({
        'success': True,
        'teams': [t.to_dict() for t in teams]
    })


# ============================================
# 에러 핸들러
# ============================================

@app.errorhandler(404)
def not_found_error(error):
    """404 에러 핸들러"""
    return render_template('base.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    db.session.rollback()
    return render_template('base.html'), 500


# ============================================
# 메인 실행
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("📅 업무 일정 관리 시스템")
    print("=" * 60)
    print(f"🌐 서버 주소: http://localhost:5000")
    print(f"📁 업로드 폴더: {app.config['UPLOAD_FOLDER']}")
    print(f"💾 데이터베이스: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 60)
    print("⚠️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
