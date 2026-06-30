from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'lecturer', 'session_date', 'start_time', 'is_active', 'duration_minutes']
    list_filter = ['is_active', 'session_date', 'course']
    search_fields = ['course__code', 'lecturer__username']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'course', 'scan_time', 'status']
    list_filter = ['status', 'scan_time', 'course']
    search_fields = ['student__username', 'course__code']
