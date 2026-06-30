from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'role': 'lecturer'}, related_name='courses'
    )
    semester = models.CharField(max_length=20, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}, related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} -> {self.course.code}"
