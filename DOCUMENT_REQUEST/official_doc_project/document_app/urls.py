from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-home/', views.admin_home, name='admin_home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('settings/', views.user_settings, name='user_settings'),
    path('logout/', views.logout_view, name='logout'),
    path('request-document/', views.request_document, name='request_document'),
    path('track-status/', views.track_status, name='track_status'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('update-request/<int:request_id>/', views.update_request, name='update_request'),
    path('download/<int:request_id>/', views.download_document, name='download_document'),
    path('admin-download-logs/', views.view_download_logs, name='admin_download_logs'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='document_app/change_password.html', success_url='/password-changed/'), name='change_password'),
    path('password-changed/', auth_views.PasswordChangeDoneView.as_view(template_name='document_app/password_changed.html'), name='password_changed_done'),
]