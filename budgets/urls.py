from django.urls import path
from . import views

urlpatterns = [
    path('', views.BudgetListView.as_view(), name='budget_list'),
    path('set/', views.SetBudgetView.as_view(), name='set_budget'),
    path('<int:pk>/edit/', views.EditBudgetView.as_view(), name='edit_budget'),
    path('<int:pk>/delete/', views.delete_budget, name='delete_budget'),
]