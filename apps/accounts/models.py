from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        LECTURER = 'lecturer', 'Lecturer'
        ADMIN = 'admin', 'Administrator'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
