from django import forms
from .models import Profile

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'date_of_birth', 'phone_number', 'profile_picture')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('currency', 'email_notifications', 'budget_alerts', 'weekly_reports')
        widgets = {
            'currency': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'budget_alerts': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'weekly_reports': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'phone_number',
            'profile_picture', 'currency', 'email_notifications',
            'budget_alerts', 'weekly_reports'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'onboarding-input'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'onboarding-input'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'onboarding-input'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'onboarding-input'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'onboarding-input',
                'accept': 'image/*'
            }),
            'currency': forms.Select(attrs={
                'class': 'onboarding-input'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'onboarding-checkbox'
            }),
            'budget_alerts': forms.CheckboxInput(attrs={
                'class': 'onboarding-checkbox'
            }),
            'weekly_reports': forms.CheckboxInput(attrs={
                'class': 'onboarding-checkbox'
            }),
        }