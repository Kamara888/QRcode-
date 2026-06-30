from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.courses.models import Department, Course, Enrollment


class Command(BaseCommand):
    help = 'Seed the database with demo users, departments, courses, and enrollments'

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@school.edu', 'role': 'admin',
            'first_name': 'System', 'last_name': 'Admin', 'is_staff': True, 'is_superuser': True,
        })
        admin.set_password('password123')
        admin.save()
        self.stdout.write(self.style.SUCCESS(f'  admin / password123  (admin)'))

        lec, _ = User.objects.get_or_create(username='lecturer1', defaults={
            'email': 'lecturer@school.edu', 'role': 'lecturer',
            'first_name': 'John', 'last_name': 'Doe',
        })
        lec.set_password('password123')
        lec.save()
        self.stdout.write(self.style.SUCCESS(f'  lecturer1 / password123  (lecturer)'))

        stu, _ = User.objects.get_or_create(username='student1', defaults={
            'email': 'student@school.edu', 'role': 'student',
            'first_name': 'Jane', 'last_name': 'Smith',
        })
        stu.set_password('password123')
        stu.save()
        self.stdout.write(self.style.SUCCESS(f'  student1 / password123  (student)'))

        dept, _ = Department.objects.get_or_create(name='Computer Science', code='CS')

        course, _ = Course.objects.get_or_create(
            code='CS301', defaults={
                'name': 'Software Engineering', 'credits': 3,
                'department': dept, 'lecturer': lec,
                'semester': '1', 'academic_year': '2025/2026',
            }
        )

        Enrollment.objects.get_or_create(student=stu, course=course)

        self.stdout.write(self.style.SUCCESS('\nSeed complete. All passwords are: password123'))
