from django.contrib.auth.views import LogoutView
from django.urls import path, include, reverse_lazy
from accounts.views import CustomLoginView, SignUpView, custom_logout

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', custom_logout, name='logout'),
]