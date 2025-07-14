from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.

user = get_user_model()

class Profile(models.Model):

    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('BGN', 'Bulgarian Lev'),
        ('GBP', 'British Pound'),
    ]

    user = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )

    first_name = models.CharField(
        max_length=30,
        blank=True,
    )

    last_name = models.CharField(
        max_length=30,
        blank=True,
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='BGN',
        help_text="User's preferred currency"
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
        )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number (optional)"
    )

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        help_text="Profile picture (max 5MB)"
    )

    email_notifications = models.BooleanField(default=True)

    budget_alerts = models.BooleanField(default=True)

    weekly_reports = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def clean(self):
        super().clean()

        if self.date_of_birth:
            from django.utils import timezone
            today = timezone.now().date()

            if self.date_of_birth > today:
                raise ValidationError({'date_of_birth': 'Date of birth cannot be in the future'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile for {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_total_expenses_this_month(self):
        from expenses.models import Expense
        now = timezone.now()
        return Expense.objects.filter(
            user=self.user,
            date__year=now.year,
            date__month=now.month
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def get_current_monthly_budget(self):
        from budgets.models import Budget

        today = timezone.now().date()
        return Budget.objects.filter(
            user=self.user,
            category=None,
            period='monthly',
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).first()

    def get_remaining_budget(self):
        budget = self.get_current_monthly_budget()
        if budget:
            return budget.get_remaining_budget()
        return None

    def is_over_budget(self):
        budget = self.get_current_monthly_budget()
        if budget:
            return budget.is_over_budget()
        return False
