from django.urls import path, include, reverse_lazy

from subscriptions import views

urlpatterns = [
    path('', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('add/', views.AddSubscriptionView.as_view(), name='add_subscription'),
    path('<int:pk>/edit/', views.EditSubscriptionView.as_view(), name='edit_subscription'),
    path('<int:pk>/delete/', views.DeleteSubscriptionView.as_view(), name='delete_subscription'),
]