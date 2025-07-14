from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, View
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Profile
from .forms import PersonalInfoForm, PreferencesForm, EditProfileForm


# Create your views here.


class OnboardingMixin(LoginRequiredMixin):
    model = Profile

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class PersonalInfoView(OnboardingMixin, UpdateView):
    form_class = PersonalInfoForm
    template_name = 'profiles/personal_info.html'

    def get_success_url(self):
        return reverse_lazy('preferences_step')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        user.onboarding_step = user.get_next_onboarding_step()
        user.save()
        messages.success(self.request, 'Personal information saved!')
        return response


class PreferencesView(OnboardingMixin, UpdateView):
    form_class = PreferencesForm
    template_name = 'profiles/preferences.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        user.onboarding_step = 'complete'
        user.save()
        messages.success(self.request, 'Welcome to Budgie! Your account is now set up.')
        return response


class OnboardingFlowView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        if user.is_onboarding_complete:
            return redirect('home')

        if user.onboarding_step == 'personal_info':
            return redirect('personal_info_step')
        elif user.onboarding_step == 'preferences':
            return redirect('preferences_step')

        return redirect('home')


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = EditProfileForm
    template_name = 'profiles/edit_profile.html'
    success_url = reverse_lazy('home') #TODO change later to dashboard

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile