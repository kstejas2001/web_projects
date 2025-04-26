from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('request-document/', views.request_document, name='request_document'),
    path('track-status/', views.track_status, name='track_status'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('update-request/<int:request_id>/', views.update_request, name='update_request'),
]