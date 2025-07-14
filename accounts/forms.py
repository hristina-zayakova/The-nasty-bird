from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label = 'Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
        }))
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        }))


class EmailSignUpForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
        )
        user.username = self.cleaned_data['email']
        user.save()
        return user