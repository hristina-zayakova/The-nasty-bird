from django.urls import path
from reports import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='main_dashboard'),
    path('generate/', views.generate_report_view, name='generate_report'),
]