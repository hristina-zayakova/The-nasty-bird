from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta


class Subscription(models.Model):

    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    name = models.CharField(
        max_length=255,
        help_text="Subscription name (e.g., Netflix, Spotify, Gym Membership)"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount charged per billing cycle"
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='monthly',
        help_text="How often you are charged"
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='subscriptions',
        help_text="Category for this subscription"
    )

    start_date = models.DateField(
        help_text="When this subscription started"
    )
    next_payment_date = models.DateField(
        help_text="Next scheduled payment date"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="When subscription ends (leave empty for ongoing)"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this subscription is currently active"
    )
    auto_add_expense = models.BooleanField(
        default=False,
        help_text="Automatically create expense entries when payments are due"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about this subscription"
    )
    website_url = models.URLField(
        blank=True,
        null=True,
        help_text="Subscription service website (optional)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['next_payment_date', 'name']
        unique_together = ['user', 'name']

    def clean(self):
        super().clean()

        if self.start_date and self.next_payment_date:
            if self.next_payment_date < self.start_date:
                raise ValidationError({'next_payment_date': 'Next payment date cannot be before start date'})

        if self.end_date and self.start_date:
            if self.end_date <= self.start_date:
                raise ValidationError({'end_date': 'End date must be after start date'})

        if self.category and self.category.user != self.user:
            raise ValidationError({'category': 'Category must belong to the same user'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.currency}{self.amount} ({self.frequency})"

    def calculate_next_payment_date(self):
        if not self.next_payment_date:
            return None

        if self.frequency == 'monthly':
            return self.next_payment_date + relativedelta(months=1)
        elif self.frequency == 'yearly':
            return self.next_payment_date + relativedelta(years=1)

        return self.next_payment_date

    def update_next_payment_date(self):
        self.next_payment_date = self.calculate_next_payment_date()
        self.save(update_fields=['next_payment_date', 'updated_at'])

    def is_overdue(self):

        if not self.is_active:
            return False

        today = timezone.now().date()
        return self.next_payment_date < today

    def days_until_payment(self):

        today = timezone.now().date()
        return (self.next_payment_date - today).days

    def create_expense_entry(self):
        from expenses.models import Expense

        return Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=self.amount,
            description=f"{self.name} - {self.frequency} subscription",
            date=self.next_payment_date,
            notes=f"Auto-generated from subscription: {self.name}"
        )