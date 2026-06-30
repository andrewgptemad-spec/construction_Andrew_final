from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # Villas
    path('villas/', views.villa_list, name='villa_list'),
    path('villas/<int:pk>/', views.villa_detail, name='villa_detail'),

    # Search & Reports
    path('search/', views.global_search, name='global_search'),
    path('reports/', views.reports, name='reports'),

    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),

    # AJAX
    path('api/categories/', views.get_categories, name='get_categories'),
]
