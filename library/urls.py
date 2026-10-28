from django.urls import path
from . import views

urlpatterns = [
    # Books catalog
    path('', views.book_list_view, name='book_list'),
    path('books/add/', views.book_create_view, name='book_create'),
    path('books/edit/<int:pk>/', views.book_update_view, name='book_update'),
    path('books/delete/<int:pk>/', views.book_delete_view, name='book_delete'),
    path('categories/add/', views.book_category_create_view, name='book_category_create'),

    # Members / Students
    path('members/', views.member_list_view, name='member_list'),
    path('members/add/', views.member_create_view, name='member_create'),
    path('members/edit/<int:pk>/', views.member_update_view, name='member_update'),
    path('members/delete/<int:pk>/', views.member_delete_view, name='member_delete'),

    # Issue / Return Circulation
    path('circulation/', views.issue_list_view, name='issue_list'),
    path('circulation/issue/', views.issue_create_view, name='issue_create'),
    path('circulation/return/<int:pk>/', views.return_book_view, name='return_book'),
]
