/* ============================================
   업무 일정 관리 시스템 - JavaScript
   위치: C:\Users\user\Desktop\인공지능산업협회AI\static\js\main.js
   ============================================ */

// 전역 변수
let currentScheduleId = null;
let calendar = null;

// DOM 로드 완료 시
document.addEventListener('DOMContentLoaded', function() {
    // 캘린더 초기화
    initCalendar();
    
    // 자동으로 알림 메시지 숨기기 (5초 후)
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(function(msg) {
            msg.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(function() {
                msg.remove();
            }, 300);
        });
    }, 5000);
    
    // 파일 업로드 미리보기
    const fileInput = document.getElementById('document');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const preview = document.getElementById('upload-preview');
            
            if (file) {
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                const fileExt = file.name.split('.').pop().toLowerCase();
                
                let fileIcon = '📄';
                if (fileExt === 'pdf') fileIcon = '📕';
                else if (fileExt === 'hwp' || fileExt === 'hwpx') fileIcon = '📘';
                else if (fileExt === 'docx' || fileExt === 'doc') fileIcon = '📗';
                
                preview.innerHTML = `
                    <div class="file-preview">
                        <span class="file-icon">${fileIcon}</span>
                        <div class="file-info">
                            <strong>${file.name}</strong>
                            <br>
                            <small>${fileSize} MB | ${fileExt.toUpperCase()} 파일</small>
                        </div>
                    </div>
                    <p class="preview-hint">✨ 업로드하면 AI가 일정을 자동으로 추출합니다.</p>
                `;
            }
        });
    }
    
    // 일정 아이템 클릭 이벤트
    const scheduleItems = document.querySelectorAll('.schedule-item');
    scheduleItems.forEach(function(item) {
        item.addEventListener('click', function(e) {
            // 버튼 클릭은 제외
            if (e.target.closest('.schedule-actions')) return;
            
            const scheduleId = this.dataset.id;
            if (scheduleId) {
                viewSchedule(scheduleId);
            }
        });
    });
});

// 캘린더 초기화
function initCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ko',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: '오늘',
            month: '월',
            week: '주',
            day: '일'
        },
        slotMinTime: '06:00:00',
        slotMaxTime: '22:00:00',
        allDaySlot: true,
        allDayText: '종일',
        nowIndicator: true,
        events: '/api/schedules',
        eventClick: function(info) {
            viewSchedule(info.event.id);
        },
        dateClick: function(info) {
            openNewScheduleModal(info.dateStr);
        },
        eventDidMount: function(info) {
            // 툴팁 추가
            if (info.event.extendedProps.task_description) {
                info.el.title = info.event.extendedProps.task_description;
            }
        }
    });
    
    calendar.render();
}

// 시간 필드 토글
function toggleTimeFields(prefix) {
    const allDayCheckbox = document.getElementById(prefix + '-all-day');
    const timeFields = document.getElementById(prefix + '-time-fields');
    
    if (allDayCheckbox && timeFields) {
        if (allDayCheckbox.checked) {
            timeFields.style.display = 'none';
        } else {
            timeFields.style.display = 'flex';
        }
    }
}

// 새 일정 모달 열기
function openNewScheduleModal(dateStr) {
    const modal = document.getElementById('new-schedule-modal');
    if (!modal) return;
    
    // 폼 초기화
    document.getElementById('new-schedule-form').reset();
    
    // 날짜 설정
    const today = dateStr || new Date().toISOString().split('T')[0];
    document.getElementById('new-start-date').value = today;
    document.getElementById('new-due-date').value = today;
    
    // 종일 체크박스 초기화
    document.getElementById('new-all-day').checked = true;
    document.getElementById('new-time-fields').style.display = 'none';
    
    modal.style.display = 'flex';
}

// 일정 보기/수정
function viewSchedule(scheduleId) {
    fetch('/api/schedule/' + scheduleId)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const schedule = data.schedule;
                currentScheduleId = schedule.id;
                
                // 상세 패널 업데이트
                updateDetailPanel(schedule);
                
                // 수정 모달에 값 채우기
                document.getElementById('edit-id').value = schedule.id;
                document.getElementById('edit-title').value = schedule.title;
                document.getElementById('edit-task').value = schedule.task_description;
                document.getElementById('edit-start-date').value = schedule.start_date || schedule.due_date;
                document.getElementById('edit-due-date').value = schedule.due_date;
                document.getElementById('edit-type').value = schedule.schedule_type;
                document.getElementById('edit-tags').value = schedule.tags || '';
                document.getElementById('edit-memo').value = schedule.memo || '';
                document.getElementById('edit-completed').checked = schedule.is_completed;
                
                // 시간 설정
                const isAllDay = schedule.is_all_day !== false;
                document.getElementById('edit-all-day').checked = isAllDay;
                
                if (!isAllDay && schedule.start_time) {
                    document.getElementById('edit-start-time').value = schedule.start_time;
                    document.getElementById('edit-end-time').value = schedule.end_time || '';
                    document.getElementById('edit-time-fields').style.display = 'flex';
                } else {
                    document.getElementById('edit-start-time').value = '';
                    document.getElementById('edit-end-time').value = '';
                    document.getElementById('edit-time-fields').style.display = 'none';
                }
                
                // 수정 폼 액션 설정
                document.getElementById('edit-schedule-form').action = '/schedule/' + schedule.id + '/edit';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// 상세 패널 업데이트
function updateDetailPanel(schedule) {
    const panel = document.getElementById('schedule-detail');
    if (!panel) return;
    
    const timeDisplay = schedule.is_all_day ? '종일' : 
        (schedule.start_time ? schedule.start_time + (schedule.end_time ? ' ~ ' + schedule.end_time : '') : '');
    
    panel.innerHTML = `
        <div class="detail-header">
            <h3>${schedule.title}</h3>
            <button class="btn btn-sm" onclick="openEditModal()">수정</button>
        </div>
        <div class="detail-info">
            <div class="info-row">
                <span class="label">📅 시작일:</span>
                <span>${formatDate(schedule.start_date || schedule.due_date)}</span>
            </div>
            <div class="info-row">
                <span class="label">📅 종료일:</span>
                <span>${formatDate(schedule.due_date)}</span>
            </div>
            ${timeDisplay ? `
            <div class="info-row">
                <span class="label">⏰ 시간:</span>
                <span>${timeDisplay}</span>
            </div>
            ` : ''}
            <div class="info-row">
                <span class="label">📌 유형:</span>
                <span>${getTypeLabel(schedule.schedule_type)}</span>
            </div>
            <div class="info-row">
                <span class="label">⏳ D-day:</span>
                <span class="urgency-badge ${getUrgencyClass(schedule.days_left)}">${getDdayText(schedule.days_left)}</span>
            </div>
        </div>
        <div class="detail-content">
            <h4>할 일 내용</h4>
            <p>${schedule.task_description}</p>
        </div>
        ${schedule.memo ? `
        <div class="detail-memo">
            <h4>메모</h4>
            <p>${schedule.memo}</p>
        </div>
        ` : ''}
        ${schedule.document_filename ? `
        <div class="detail-source">
            <span>📄 출처: ${schedule.document_filename}</span>
        </div>
        ` : ''}
    `;
}

// 수정 모달 열기
function openEditModal() {
    if (currentScheduleId) {
        document.getElementById('edit-schedule-modal').style.display = 'flex';
    }
}

// 일정 유형 라벨
function getTypeLabel(type) {
    const labels = {
        'deadline': '마감',
        'submit': '제출',
        'meeting': '회의',
        'trip': '출장',
        'other': '기타'
    };
    return labels[type] || type;
}

// 삭제 확인
function deleteSchedule() {
    const scheduleId = document.getElementById('edit-id').value;
    if (!scheduleId) return;
    
    if (confirm('정말 이 일정을 삭제하시겠습니까?')) {
        fetch('/schedule/' + scheduleId + '/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeModal('edit-schedule-modal');
                location.reload();
            } else {
                alert(data.message || '삭제에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('오류가 발생했습니다.');
        });
    }
}

// 모달 닫기
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// 모달 열기 함수들
function openUploadModal() {
    document.getElementById('upload-modal').style.display = 'flex';
}

function openTeamScheduleModal() {
    const modal = document.getElementById('team-schedule-modal');
    if (modal) {
        modal.style.display = 'flex';
        loadTeamSchedules();
    }
}

function openSearchModal() {
    const modal = document.getElementById('search-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// 팀원 일정 로드
function loadTeamSchedules() {
    fetch('/api/team-schedules')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('team-schedule-list');
            if (!container) return;
            
            if (data.success && Object.keys(data.team_schedules).length > 0) {
                let html = '';
                for (const [username, schedules] of Object.entries(data.team_schedules)) {
                    html += `<div class="team-member-schedules">`;
                    html += `<h4>👤 ${username}</h4>`;
                    html += `<ul>`;
                    schedules.forEach(s => {
                        html += `<li>${s.title} - ${formatDate(s.due_date)}</li>`;
                    });
                    html += `</ul></div>`;
                }
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p class="empty-state">팀원 일정이 없습니다.</p>';
            }
        });
}

// 유틸리티: 날짜 포맷
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
    const weekday = weekdays[date.getDay()];
    return `${month}/${day}(${weekday})`;
}

// 유틸리티: D-day 계산
function calculateDday(dateString) {
    if (!dateString) return null;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const targetDate = new Date(dateString);
    targetDate.setHours(0, 0, 0, 0);
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// 유틸리티: D-day 텍스트
function getDdayText(days) {
    if (days === null) return '-';
    if (days < 0) return `D+${Math.abs(days)}`;
    if (days === 0) return 'D-Day';
    return `D-${days}`;
}

// 유틸리티: 긴급도 클래스
function getUrgencyClass(days) {
    if (days === null) return 'normal';
    if (days < 0) return 'overdue';
    if (days <= 2) return 'urgent';
    if (days <= 5) return 'soon';
    if (days <= 7) return 'warning';
    return 'normal';
}

// 슬라이드아웃 애니메이션 추가
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .file-preview {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .file-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    
    .file-info {
        flex: 1;
    }
    
    .preview-hint {
        font-size: 0.85rem;
        color: #28a745;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .checkbox-label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
    }
    
    .checkbox-label input[type="checkbox"] {
        width: 18px;
        height: 18px;
    }
    
    .time-fields {
        gap: 1rem;
    }
`;
document.head.appendChild(styleSheet);

// 콘솔 로그
console.log('📅 업무 일정 관리 시스템 로드 완료');
