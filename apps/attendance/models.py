import uuid
import hashlib
import hmac
import json
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone


class AttendanceSession(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='sessions')
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'lecturer'}, related_name='sessions'
    )
    session_date = models.DateField(auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    qr_token_hash = models.CharField(max_length=64, blank=True)
    qr_token_plain = models.CharField(max_length=255, blank=True)
    qr_generated_at = models.DateTimeField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'attendance_sessions'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.course.code} - {self.session_date}"

    def generate_token(self):
        raw = f"{self.id}:{uuid.uuid4().hex}:{timezone.now().timestamp()}"
        secret = settings.SECRET_KEY.encode()
        token = hmac.new(secret, raw.encode(), hashlib.sha256).hexdigest()
        self.qr_token_hash = hashlib.sha256(token.encode()).hexdigest()
        self.qr_token_plain = token
        self.qr_generated_at = timezone.now()
        self.token_expires_at = timezone.now() + timedelta(minutes=5)
        return token

    def validate_token(self, token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash != self.qr_token_hash:
            return False
        if timezone.now() > self.token_expires_at:
            return False
        return True

    def end_session(self):
        self.is_active = False
        self.end_time = timezone.now()
        self.save()

    @property
    def qr_data(self):
        data = {
            'session_id': self.id,
            'course_id': self.course_id,
            'lecturer': self.lecturer_id,
        }
        if self.qr_token_plain:
            data['token'] = self.qr_token_plain
        return json.dumps(data)


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        LATE = 'late', 'Late'
        ABSENT = 'absent', 'Absent'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}, related_name='attendance_records'
    )
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='attendance_records')
    scan_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_info = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'attendance_records'
        unique_together = ['student', 'session']
        ordering = ['-scan_time']

    def __str__(self):
        return f"{self.student.username} - {self.session} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.course_id:
            self.course = self.session.course
        if not self.pk:
            grace_minutes = 15
            session_start = self.session.start_time
            if self.scan_time and session_start:
                if self.scan_time <= session_start + timedelta(minutes=grace_minutes):
                    self.status = self.Status.PRESENT
                else:
                    self.status = self.Status.LATE
        super().save(*args, **kwargs)
