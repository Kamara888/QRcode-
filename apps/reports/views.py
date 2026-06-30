from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import date, timedelta
from apps.attendance.models import AttendanceRecord, AttendanceSession
from apps.courses.models import Course, Department
from .utils import export_csv, export_pdf, export_excel


class AttendanceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        records = AttendanceRecord.objects.select_related('student', 'course', 'session')
        if user.role == 'lecturer':
            records = records.filter(session__lecturer=user)
        elif user.role == 'student':
            records = records.filter(student=user)
        course = request.query_params.get('course')
        dept = request.query_params.get('department')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        period = request.query_params.get('period')
        if course:
            records = records.filter(course_id=course)
        if dept:
            records = records.filter(course__department_id=dept)
        if date_from:
            records = records.filter(session__session_date__gte=date_from)
        if date_to:
            records = records.filter(session__session_date__lte=date_to)
        if period == 'today':
            records = records.filter(session__session_date=date.today())
        elif period == 'week':
            week_start = date.today() - timedelta(days=date.today().weekday())
            records = records.filter(session__session_date__gte=week_start)
        elif period == 'month':
            records = records.filter(session__session_date__month=date.today().month)
        data = []
        for r in records:
            data.append({
                'id': r.id,
                'student': r.student.get_full_name() or r.student.username,
                'course': r.course.code,
                'course_name': r.course.name,
                'date': str(r.session.session_date),
                'time': r.scan_time.strftime('%H:%M:%S'),
                'status': r.status,
            })
        fmt = request.query_params.get('format')
        if fmt == 'csv':
            csv_data = export_csv(records)
            return HttpResponse(csv_data, content_type='text/csv', headers={
                'Content-Disposition': 'attachment; filename="attendance_report.csv"'
            })
        elif fmt == 'pdf':
            pdf_data = export_pdf(records)
            return HttpResponse(pdf_data, content_type='application/pdf', headers={
                'Content-Disposition': 'attachment; filename="attendance_report.pdf"'
            })
        elif fmt == 'xlsx':
            xlsx_data = export_excel(records)
            return HttpResponse(xlsx_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={
                'Content-Disposition': 'attachment; filename="attendance_report.xlsx"'
            })
        return Response(data)


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        total_sessions = AttendanceSession.objects.count()
        total_records = AttendanceRecord.objects.count()
        if user.role == 'lecturer':
            total_sessions = AttendanceSession.objects.filter(lecturer=user).count()
            total_records = AttendanceRecord.objects.filter(session__lecturer=user).count()
        elif user.role == 'student':
            total_records = AttendanceRecord.objects.filter(student=user).count()
            total_sessions = AttendanceSession.objects.filter(
                course__in=user.enrollments.values('course')
            ).count()
        present = AttendanceRecord.objects.filter(status='present').count()
        late = AttendanceRecord.objects.filter(status='late').count()
        absent = AttendanceRecord.objects.filter(status='absent').count()
        if user.role == 'lecturer':
            present = AttendanceRecord.objects.filter(session__lecturer=user, status='present').count()
            late = AttendanceRecord.objects.filter(session__lecturer=user, status='late').count()
            absent = AttendanceRecord.objects.filter(session__lecturer=user, status='absent').count()
        elif user.role == 'student':
            present = AttendanceRecord.objects.filter(student=user, status='present').count()
            late = AttendanceRecord.objects.filter(student=user, status='late').count()
            absent = AttendanceRecord.objects.filter(student=user, status='absent').count()
        return Response({
            'total_sessions': total_sessions,
            'total_records': total_records,
            'present': present,
            'late': late,
            'absent': absent,
        })
