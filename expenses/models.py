from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import os

# Create your models here.

class Expense(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,  # Prevent category deletion if expenses exist
        related_name='expenses'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Expense amount"
    )

    description = models.CharField(
        max_length=255,
        help_text="Brief description of the expense"
    )

    date = models.DateField(
        default=timezone.now,
        help_text="Date when the expense occurred"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date', '-created_at']

    def clean(self):
        super().clean()

        if self.date:
            today = timezone.now().date()
            if self.date > today:
                raise ValidationError({'date': 'Expense date cannot be in the future'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - ${self.amount} ({self.date})"

    def get_previous_expense(self):
        return Expense.objects.filter(
            user=self.user,
            created_at__lt=self.created_at
        ).first()

    def get_next_expense(self):
        return Expense.objects.filter(
            user=self.user,
            created_at__gt=self.created_at
        ).last()