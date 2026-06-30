from django.contrib import admin
from .models import Department, Course, Enrollment


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'lecturer', 'semester']
    list_filter = ['department', 'semester', 'academic_year']
    search_fields = ['code', 'name']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_date']
    list_filter = ['course']
    search_fields = ['student__username', 'course__code']
