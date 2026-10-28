from django.urls import path
from . import views

urlpatterns = [
    # Medicine inventory CRUD
    path('', views.medicine_list_view, name='medicine_list'),
    path('add/', views.medicine_create_view, name='medicine_create'),
    path('edit/<int:pk>/', views.medicine_update_view, name='medicine_update'),
    path('delete/<int:pk>/', views.medicine_delete_view, name='medicine_delete'),
    path('category/add/', views.category_create_view, name='category_create'),

    # Prescriptions CRUD
    path('prescriptions/', views.prescription_list_view, name='prescription_list'),
    path('prescriptions/create/', views.prescription_create_view, name='prescription_create'),
    path('prescriptions/<int:pk>/', views.prescription_detail_view, name='prescription_detail'),
    path('prescriptions/edit/<int:pk>/', views.prescription_update_view, name='prescription_update'),
    path('prescriptions/delete/<int:pk>/', views.prescription_delete_view, name='prescription_delete'),
]
