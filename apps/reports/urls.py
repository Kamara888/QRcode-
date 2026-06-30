from django.urls import path
from . import views

urlpatterns = [
    path('attendance/', views.AttendanceReportView.as_view(), name='attendance-report'),
    path('dashboard/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
]
