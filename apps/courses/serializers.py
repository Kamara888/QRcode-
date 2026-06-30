from rest_framework import serializers
from .models import Department, Course, Enrollment
from apps.accounts.serializers import UserSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    lecturer_name = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lecturer_name(self, obj):
        if obj.lecturer:
            return obj.lecturer.get_full_name() or obj.lecturer.username
        return None

    def get_student_count(self, obj):
        return obj.enrollments.count()


class EnrollmentSerializer(serializers.ModelSerializer):
    student_detail = UserSerializer(source='student', read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'


class EnrollStudentsSerializer(serializers.Serializer):
    student_ids = serializers.ListField(child=serializers.IntegerField())
