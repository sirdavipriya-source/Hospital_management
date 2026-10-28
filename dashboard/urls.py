from django.urls import path
from . import views

urlpatterns = [
    path('patient/dashboard/', views.patient_dashboard_view, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('reports/', views.reports_view, name='reports'),
    path('api/dashboard-stats/', views.dashboard_stats_api, name='api_dashboard_stats'),
]


