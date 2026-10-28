from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('doctor/login/', views.doctor_login_view, name='doctor_login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard-redirect/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('profile/', views.profile_view, name='profile'),
]
