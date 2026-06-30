from rest_framework import serializers
from .models import AttendanceSession, AttendanceRecord


class CreateSessionSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    duration_minutes = serializers.IntegerField(default=30)


class SessionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    lecturer_name = serializers.SerializerMethodField()
    record_count = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = '__all__'

    def get_lecturer_name(self, obj):
        return obj.lecturer.get_full_name() or obj.lecturer.username

    def get_record_count(self, obj):
        return obj.records.count()


class ScanQRSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    token = serializers.CharField()
    device_info = serializers.CharField(required=False, allow_blank=True)


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_username = serializers.CharField(source='student.username', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    session_date = serializers.DateField(source='session.session_date', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username


class AttendanceSummarySerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    total_classes = serializers.IntegerField()
    attended = serializers.IntegerField()
    late = serializers.IntegerField()
    absent = serializers.IntegerField()
    percentage = serializers.FloatField()
