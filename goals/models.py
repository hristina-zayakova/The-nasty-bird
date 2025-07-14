from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

# Create your models here.
class Goal(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    name = models.CharField(
        max_length=255,
        help_text="Goal name (e.g., Summer Vacation, New Laptop, Wedding Fund)"
    )
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Target amount to save"
    )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Current amount saved"
    )
    target_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target date to reach goal (optional)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or notes about this goal"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this goal is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def clean(self):
        super().clean()

        if self.current_amount > self.target_amount:
            raise ValidationError({'current_amount': 'Current amount cannot exceed target amount'})

        if self.target_date:
            today = timezone.now().date()
            if self.target_date < today:
                raise ValidationError({'target_date': 'Target date cannot be in the past'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.currency}{self.current_amount}/{self.user.currency}{self.target_amount}"

    def get_progress_percentage(self):
        if self.target_amount <= 0:
            return 0
        return min((self.current_amount / self.target_amount) * 100, 100)

    def get_remaining_amount(self):
        return max(self.target_amount - self.current_amount, Decimal('0.00'))

    def is_completed(self):
        return self.current_amount >= self.target_amount

    def days_to_target(self):
        if not self.target_date:
            return None

        today = timezone.now().date()
        if self.target_date > today:
            return (self.target_date - today).days
        return 0

    def add_progress(self, amount):
        self.current_amount += Decimal(str(amount))
        if self.current_amount > self.target_amount:
            self.current_amount = self.target_amount
        self.save()
