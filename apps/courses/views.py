from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Department, Course, Enrollment
from .serializers import DepartmentSerializer, CourseSerializer, EnrollmentSerializer, EnrollStudentsSerializer


class IsLecturerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['lecturer', 'admin']


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAdminUser]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAdminUser]


class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsLecturerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Course.objects.all()
        return Course.objects.filter(lecturer=user)

    def perform_create(self, serializer):
        serializer.save(lecturer=self.request.user if self.request.user.role == 'lecturer' else serializer.validated_data.get('lecturer'))


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsLecturerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Course.objects.all()
        return Course.objects.filter(lecturer=user)


class EnrollStudentsView(APIView):
    permission_classes = [IsLecturerOrAdmin]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        serializer = EnrollStudentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = []
        for sid in serializer.validated_data['student_ids']:
            _, was_created = Enrollment.objects.get_or_create(
                student_id=sid, course=course
            )
            if was_created:
                created.append(sid)
        return Response({'enrolled': created, 'course': course.id}, status=status.HTTP_201_CREATED)

    def delete(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({'error': 'student_id required'}, status=400)
        deleted, _ = Enrollment.objects.filter(student_id=student_id, course=course).delete()
        return Response({'deleted': deleted})


class EnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsLecturerOrAdmin]

    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        if course_id:
            return Enrollment.objects.filter(course_id=course_id)
        return Enrollment.objects.none()


class StudentCourseListView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'student':
            return Course.objects.filter(enrollments__student=self.request.user)
        return Course.objects.none()
