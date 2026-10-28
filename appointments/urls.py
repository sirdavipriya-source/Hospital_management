from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list_view, name='appointment_list'),
    path('book/', views.book_appointment_view, name='book_appointment'),
    path('<int:pk>/status/', views.update_appointment_status_view, name='update_appointment_status'),
    path('<int:pk>/prescription/', views.add_diagnosis_prescription_view, name='add_prescription'),
    path('api/availability/', views.check_doctor_availability_api, name='api_check_availability'),
]
