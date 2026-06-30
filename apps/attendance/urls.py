from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateSessionView.as_view(), name='create-session'),
    path('active/', views.ActiveSessionView.as_view(), name='active-sessions'),
    path('<int:session_id>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('<int:session_id>/qrcode/', views.SessionQRCodeView.as_view(), name='session-qrcode'),
    path('<int:session_id>/end/', views.EndSessionView.as_view(), name='end-session'),
    path('scan/', views.ScanQRView.as_view(), name='scan-qr'),
    path('my/', views.MyAttendanceView.as_view(), name='my-attendance'),
    path('summary/', views.AttendanceSummaryView.as_view(), name='attendance-summary'),
    path('course/<int:course_id>/', views.CourseAttendanceView.as_view(), name='course-attendance'),
]
