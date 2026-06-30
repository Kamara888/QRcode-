from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from apps.attendance import web_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/sessions/', include('apps.attendance.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', web_views.dashboard_redirect, name='dashboard-redirect'),
    path('dashboard/', web_views.lecturer_dashboard, name='lecturer-dashboard'),
    path('student/', web_views.student_dashboard, name='student-dashboard'),
    path('student/scan/', web_views.student_scanner, name='student-scanner'),
    path('panel/', web_views.admin_dashboard, name='admin-dashboard'),
    path('panel/sudo/', web_views.sudo_confirm, name='sudo-confirm'),
    path('panel/users/create/', web_views.admin_create_user, name='admin-create-user'),
    path('panel/users/<int:user_id>/delete/', web_views.admin_delete_user, name='admin-delete-user'),
    path('panel/users/', web_views.admin_user_list, name='admin-user-list'),
    path('sessions/create/', web_views.create_session_web, name='session-create-web'),
    path('sessions/<int:session_id>/qr/', web_views.session_qr_display, name='session-qr-display'),
    path('sessions/<int:session_id>/end/', web_views.end_session_web, name='session-end'),
    path('sessions/<int:session_id>/', web_views.session_detail_web, name='session-detail-web'),
    path('sessions/<int:session_id>/export/xlsx/', web_views.session_export_xlsx, name='session-export-xlsx'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
