from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.medical_history_view, name='medical_history'),
    path('prescriptions/', views.prescriptions_view, name='prescriptions'),
    path('list/', views.patient_list_admin_view, name='patient_list'),
]
