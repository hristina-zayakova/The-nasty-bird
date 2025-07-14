from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import EmailLoginForm, EmailSignUpForm

User = get_user_model()

# Create your views here.
class CustomLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        print(f"User onboarding step: {self.request.user.onboarding_step}")
        print(f"Is onboarding complete: {self.request.user.is_onboarding_complete}")

        if not self.request.user.is_onboarding_complete:
            return reverse_lazy('onboarding_flow')
        return reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'Welcome back!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password.')
        return super().form_invalid(form)


class SignUpView(CreateView):
    model = User
    form_class = EmailSignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('onboarding_flow')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        user.onboarding_step = 'personal_info'
        user.save()

        login(self.request, user)
        messages.success(self.request, 'Account created successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There were errors with your signup. Please check the form below.')
        return super().form_invalid(form)

# class CustomLogoutView(LogoutView):
#     http_method_names = ['get', 'post']
#
#     def dispatch(self, request, *args, **kwargs):
#         logout(request)
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         logout(request)
#         return redirect('/')

def custom_logout(request):
    logout(request)
    return redirect('/')