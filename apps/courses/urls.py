from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.DepartmentListCreateView.as_view(), name='department-list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    path('', views.CourseListCreateView.as_view(), name='course-list'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<int:course_id>/enroll/', views.EnrollStudentsView.as_view(), name='enroll-students'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment-list'),
    path('my/', views.StudentCourseListView.as_view(), name='student-courses'),
]
