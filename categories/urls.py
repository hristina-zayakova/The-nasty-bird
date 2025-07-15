from django.urls import path, include, reverse_lazy

from categories import (views)

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='categories_list'),
    path('add/', views.AddCategoryView.as_view(), name='add_category'),
    path('<int:pk>/edit/', views.EditCategoryView.as_view(), name='edit_category'),
]