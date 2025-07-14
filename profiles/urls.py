from django.urls import path, include, reverse_lazy

from profiles import views

urlpatterns = [
    path('onboarding/', views.OnboardingFlowView.as_view(), name='onboarding_flow'),
    path('onboarding/personal-info/', views.PersonalInfoView.as_view(), name='personal_info_step'),
    path('onboarding/preferences/', views.PreferencesView.as_view(), name='preferences_step'),
    path('edit/', views.EditProfileView.as_view(), name='edit_profile'),
]