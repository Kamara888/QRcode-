from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q, Sum, Case, When, IntegerField
from datetime import timedelta
from .models import AttendanceSession, AttendanceRecord
from .serializers import (
    CreateSessionSerializer, SessionSerializer, ScanQRSerializer,
    AttendanceRecordSerializer, AttendanceSummarySerializer
)
from .utils import generate_qr_code_base64
from apps.courses.models import Course, Enrollment


class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'lecturer'


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'


class CreateSessionView(APIView):
    permission_classes = [IsLecturer]

    def post(self, request):
        serializer = CreateSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(Course, id=serializer.validated_data['course_id'])
        if course.lecturer != request.user and request.user.role != 'admin':
            return Response({'error': 'You are not the lecturer for this course'}, status=403)
        session = AttendanceSession.objects.create(
            course=course,
            lecturer=request.user if request.user.role == 'lecturer' else course.lecturer,
            duration_minutes=serializer.validated_data['duration_minutes'],
        )
        token = session.generate_token()
        session.save()
        qr_data = session.qr_data
        qr_b64 = generate_qr_code_base64(qr_data)
        return Response({
            'session': SessionSerializer(session).data,
            'qr_code': qr_b64,
            'scan_token': token,
        }, status=status.HTTP_201_CREATED)


class ActiveSessionView(APIView):
    permission_classes = [IsLecturer]

    def get(self, request):
        sessions = AttendanceSession.objects.filter(
            lecturer=request.user, is_active=True
        ).select_related('course')
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)


class SessionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(AttendanceSession, id=session_id)
        if request.user.role == 'lecturer' and session.lecturer != request.user:
            return Response({'error': 'Not your session'}, status=403)
        serializer = SessionSerializer(session)
        return Response(serializer.data)


class SessionQRCodeView(APIView):
    permission_classes = [IsLecturer]

    def get(self, request, session_id):
        session = get_object_or_404(AttendanceSession, id=session_id, lecturer=request.user)
        if not session.is_active:
            return Response({'error': 'Session is not active'}, status=400)
        token = session.generate_token()
        session.save()
        qr_data = session.qr_data
        qr_b64 = generate_qr_code_base64(qr_data)
        return Response({
            'qr_code': qr_b64,
            'scan_token': token,
            'expires_at': session.token_expires_at,
        })


class EndSessionView(APIView):
    permission_classes = [IsLecturer]

    def post(self, request, session_id):
        session = get_object_or_404(AttendanceSession, id=session_id, lecturer=request.user)
        session.end_session()
        return Response({'message': 'Session ended'})


class ScanQRView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        serializer = ScanQRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = get_object_or_404(
            AttendanceSession,
            id=serializer.validated_data['session_id'],
            is_active=True
        )
        if not session.validate_token(serializer.validated_data['token']):
            return Response({'error': 'Invalid or expired QR code'}, status=400)
        enrolled = Enrollment.objects.filter(
            student=request.user, course=session.course
        ).exists()
        if not enrolled:
            return Response({'error': 'You are not enrolled in this course'}, status=403)
        if AttendanceRecord.objects.filter(student=request.user, session=session).exists():
            existing = AttendanceRecord.objects.get(student=request.user, session=session)
            return Response({
                'message': 'Already recorded',
                'status': existing.status,
                'scan_time': existing.scan_time,
            })
        record = AttendanceRecord.objects.create(
            student=request.user,
            session=session,
            scan_time=timezone.now(),
            ip_address=request.META.get('REMOTE_ADDR'),
            device_info=serializer.validated_data.get('device_info', ''),
        )
        return Response({
            'message': 'Attendance recorded',
            'status': record.status,
            'scan_time': record.scan_time,
        }, status=status.HTTP_201_CREATED)


class MyAttendanceView(generics.ListAPIView):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        qs = AttendanceRecord.objects.filter(student=self.request.user)
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs.select_related('session', 'course')


class AttendanceSummaryView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        records = AttendanceRecord.objects.filter(student=request.user)
        course_ids = records.values_list('course_id', flat=True).distinct()
        summaries = []
        for cid in course_ids:
            course = Course.objects.get(id=cid)
            total = AttendanceSession.objects.filter(course_id=cid).count()
            attended = records.filter(course_id=cid, status='present').count()
            late = records.filter(course_id=cid, status='late').count()
            absent = records.filter(course_id=cid, status='absent').count()
            total_attended = attended + late
            percentage = round((total_attended / total * 100), 1) if total > 0 else 0
            summaries.append({
                'course_id': cid,
                'course_name': f"{course.code} - {course.name}",
                'total_classes': total,
                'attended': attended,
                'late': late,
                'absent': absent,
                'percentage': percentage,
            })
        return Response(summaries)


class CourseAttendanceView(APIView):
    permission_classes = [IsLecturer]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if course.lecturer != request.user and request.user.role != 'admin':
            return Response({'error': 'Not your course'}, status=403)
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        sessions = AttendanceSession.objects.filter(course=course)
        if date_from:
            sessions = sessions.filter(session_date__gte=date_from)
        if date_to:
            sessions = sessions.filter(session_date__lte=date_to)
        records = AttendanceRecord.objects.filter(session__in=sessions).select_related('student', 'session')
        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data)
