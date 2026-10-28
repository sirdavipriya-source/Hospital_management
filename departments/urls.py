from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_list_view, name='department_list'),
    path('manage/', views.department_admin_list, name='department_admin'),
    path('<int:pk>/', views.department_detail_view, name='department_detail'),
    path('add/', views.department_create_view, name='department_create'),
    path('edit/<int:pk>/', views.department_update_view, name='department_update'),
    path('delete/<int:pk>/', views.department_delete_view, name='department_delete'),
    
    # Specializations
    path('specializations/', views.specialization_list_view, name='specialization_list'),
    path('specializations/add/', views.specialization_create_view, name='specialization_create'),
    path('specializations/edit/<int:pk>/', views.specialization_update_view, name='specialization_update'),
    path('specializations/delete/<int:pk>/', views.specialization_delete_view, name='specialization_delete'),
    path('api/by-department/<int:dept_id>/', views.specializations_by_department_api, name='specializations_by_dept_api'),
]

