from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from django.db import models

from accounts.managers import CustomUserManager


# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):

    ONBOARDING_STEPS = [
        ('signup', 'Initial Signup'),
        ('personal_info', 'Personal Information'),
        ('preferences', 'Preferences & Settings'),
        ('complete', 'Complete'),
    ]

    email = models.EmailField(
        unique=True,
        error_messages={'unique': 'A user with this email already exists.'}
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_staff = models.BooleanField(
         default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    onboarding_step = models.CharField(
        max_length=20,
        choices=ONBOARDING_STEPS,
        default='signup',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] #TODO: Look if that is TRUE

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_next_onboarding_step(self):
        steps = [step[0] for step in self.ONBOARDING_STEPS]
        try:
            current_index = steps.index(self.onboarding_step)
            if current_index < len(steps) - 1:
                return steps[current_index + 1]
        except ValueError:
            pass
        return None

    @property
    def is_onboarding_complete(self):
        return self.onboarding_step == 'complete'
