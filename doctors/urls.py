from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list_view, name='doctor_list'),
    path('manage/', views.doctor_admin_list, name='doctor_admin'),
    path('<int:pk>/', views.doctor_detail_view, name='doctor_detail'),
    path('add/', views.doctor_create_view, name='doctor_create'),
    path('edit/<int:pk>/', views.doctor_update_view, name='doctor_update'),
    path('delete/<int:pk>/', views.doctor_delete_view, name='doctor_delete'),
]

