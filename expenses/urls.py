from django.urls import path, include
from . import views

urlpatterns = [
    path('add/', views.AddExpenseView.as_view(), name='add_expense'),
    path('<int:pk>/edit/', views.EditExpenseView.as_view(), name='edit_expense'),
    path('<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('category/<int:category_id>/', views.CategoryExpensesView.as_view(), name='category_expenses'),
]