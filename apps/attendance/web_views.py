from collections import Counter
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from apps.accounts.models import User
from apps.courses.models import Course
from apps.attendance.models import AttendanceSession, AttendanceRecord
from apps.attendance.utils import generate_qr_code_base64
from apps.attendance.decorators import sudo_required
from django.http import HttpResponse
from apps.reports.views import DashboardStatsView
from apps.reports.utils import export_excel
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


@login_required
def dashboard_redirect(request):
    if request.user.role == 'admin':
        return redirect('admin-dashboard')
    elif request.user.role == 'lecturer':
        return redirect('lecturer-dashboard')
    else:
        return redirect('student-dashboard')


@login_required
def student_dashboard(request):
    records = AttendanceRecord.objects.filter(student=request.user).select_related('session', 'course')
    status_counts = Counter(records.values_list('status', flat=True))
    total = len(records)
    present = status_counts.get('present', 0)
    late = status_counts.get('late', 0)
    absent = status_counts.get('absent', 0)
    return render(request, 'attendance/student_dashboard.html', {
        'records': records,
        'total': total,
        'present': present,
        'late': late,
        'absent': absent,
    })


@login_required
def student_scanner(request):
    return render(request, 'attendance/student_scanner.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('login')
    total_students = User.objects.filter(role='student').count()
    total_lecturers = User.objects.filter(role='lecturer').count()
    total_courses = Course.objects.count()
    total_sessions = AttendanceSession.objects.count()
    total_records = AttendanceRecord.objects.count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    now = datetime.now()
    hour = now.hour
    if hour < 12: greeting = 'Good Morning'
    elif hour < 17: greeting = 'Good Afternoon'
    else: greeting = 'Good Evening'
    return render(request, 'attendance/admin_dashboard.html', {
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_courses': total_courses,
        'total_sessions': total_sessions,
        'total_records': total_records,
        'recent_users': recent_users,
        'greeting': greeting,
        'today': now.strftime('%A, %B %d, %Y'),
    })


@login_required
@sudo_required
def admin_create_user(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('login')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        if not username or not password or not role:
            messages.error(request, 'Username, password, and role are required.')
            return redirect('admin-create-user')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admin-create-user')
        user = User.objects.create_user(
            username=username, email=email, password=password,
            role=role, first_name=first_name, last_name=last_name, phone=phone,
        )
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
        messages.success(request, f'{role.capitalize()} "{username}" created successfully.')
        return redirect('admin-dashboard')
    return render(request, 'attendance/admin_create_user.html')


@login_required
def admin_user_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('login')
    role_filter = request.GET.get('role', '')
    search = request.GET.get('search', '')
    users = User.objects.all()
    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(
            Q(username__icontains=search) | Q(email__icontains=search) |
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
        )
    users = users.order_by('-date_joined')
    return render(request, 'attendance/admin_user_list.html', {
        'users': users,
        'role_filter': role_filter,
        'search': search,
    })


@login_required
def lecturer_dashboard(request):
    if request.user.role not in ['lecturer', 'admin']:
        messages.error(request, 'Access denied')
        return redirect('login')
    courses = Course.objects.filter(lecturer=request.user) if request.user.role == 'lecturer' else Course.objects.all()
    active_sessions = AttendanceSession.objects.filter(
        lecturer=request.user if request.user.role == 'lecturer' else request.user,
        is_active=True
    ).select_related('course') if request.user.role == 'lecturer' else AttendanceSession.objects.filter(is_active=True).select_related('course')
    recent_sessions = AttendanceSession.objects.filter(
        lecturer=request.user if request.user.role == 'lecturer' else request.user
    ).select_related('course')[:10] if request.user.role == 'lecturer' else AttendanceSession.objects.all().select_related('course')[:10]
    factory = APIRequestFactory()
    drf_request = Request(factory.get('/'))
    drf_request.user = request.user
    stats_view = DashboardStatsView()
    stats = stats_view.get(drf_request).data
    return render(request, 'attendance/lecturer_dashboard.html', {
        'courses': courses,
        'active_sessions': active_sessions,
        'recent_sessions': recent_sessions,
        'stats': stats,
    })


@login_required
def create_session_web(request):
    if request.user.role != 'lecturer':
        messages.error(request, 'Access denied')
        return redirect('login')
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        duration = int(request.POST.get('duration_minutes', 30))
        course = get_object_or_404(Course, id=course_id, lecturer=request.user)
        with transaction.atomic():
            session = AttendanceSession.objects.create(
                course=course,
                lecturer=request.user,
                duration_minutes=duration,
            )
            token = session.generate_token()
            session.save()
        messages.success(request, f'Session created for {course.code}')
        return redirect('session-qr-display', session_id=session.id)
    return redirect('lecturer-dashboard')


@login_required
def session_qr_display(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    if request.user.role == 'lecturer' and session.lecturer != request.user:
        messages.error(request, 'Access denied')
        return redirect('lecturer-dashboard')
    with transaction.atomic():
        token = session.generate_token()
        session.save(update_fields=['qr_token_hash', 'qr_token_plain', 'qr_generated_at', 'token_expires_at'])
    qr_b64 = generate_qr_code_base64(session.qr_data)
    records = AttendanceRecord.objects.filter(session=session).select_related('student')
    enrolled_count = session.course.enrollments.count()
    scanned_count = records.count()
    return render(request, 'attendance/qr_display.html', {
        'session': session,
        'qr_b64': qr_b64,
        'records': records,
        'enrolled_count': enrolled_count,
        'scanned_count': scanned_count,
    })


@login_required
def end_session_web(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    if request.user.role == 'lecturer' and session.lecturer != request.user:
        messages.error(request, 'Access denied')
        return redirect('lecturer-dashboard')
    session.end_session()
    messages.success(request, 'Session ended')
    return redirect('lecturer-dashboard')


@login_required
def session_detail_web(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    if request.user.role == 'lecturer' and session.lecturer != request.user:
        messages.error(request, 'Access denied')
        return redirect('lecturer-dashboard')
    records = AttendanceRecord.objects.filter(session=session).select_related('student')
    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'records': records,
    })


@login_required
def sudo_confirm(request):
    if request.user.role != 'admin':
        return redirect('login')
    if request.method == 'POST':
        password = request.POST.get('password', '')
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            request.session['sudo_verified'] = True
            next_url = request.session.pop('sudo_redirect', 'admin-dashboard')
            return redirect(next_url)
        messages.error(request, 'Incorrect password.')
        return redirect('sudo-confirm')
    next_url = request.GET.get('next') or request.session.get('sudo_redirect', '')
    return render(request, 'attendance/sudo_confirm.html', {'next': next_url})


@login_required
@sudo_required
def admin_delete_user(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('login')
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.error(request, 'You cannot delete yourself.')
        return redirect('admin-user-list')
    if request.method == 'POST':
        name = target.get_full_name() or target.username
        target.delete()
        messages.success(request, f'User "{name}" deleted successfully.')
        return redirect('admin-user-list')
    return render(request, 'attendance/admin_delete_confirm.html', {'target': target})


@login_required
def session_export_xlsx(request, session_id):
    session = get_object_or_404(AttendanceSession, id=session_id)
    if request.user.role == 'lecturer' and session.lecturer != request.user:
        messages.error(request, 'Access denied')
        return redirect('lecturer-dashboard')
    records = AttendanceRecord.objects.filter(session=session).select_related('student', 'course', 'session')
    filename = f"{session.course.code}_{session.session_date}_attendance.xlsx"
    excel_data = export_excel(records, title=f"{session.course.code} Attendance")
    return HttpResponse(
        excel_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )
