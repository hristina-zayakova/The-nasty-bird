from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import os

# Create your models here.

def expense_receipt_path(instance, filename):
    # Format: receipts/user_id/year/month/filename
    return f'receipts/{instance.user.id}/{instance.date.year}/{instance.date.month}/{filename}'


class Expense(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('digital_wallet', 'Digital Wallet (PayPal, etc.)'),
        ('other', 'Other'),
    ]

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

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or details (optional)"
    )

    date = models.DateField(
        default=timezone.now,
        help_text="Date when the expense occurred"
    )

    receipt_image = models.ImageField(
        upload_to=expense_receipt_path,
        null=True,
        blank=True,
        help_text="Upload receipt image (optional)"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Where the expense occurred (optional)"
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

    def delete(self, *args, **kwargs):
        if self.receipt_image:
            if os.path.isfile(self.receipt_image.path):
                os.remove(self.receipt_image.path)
        super().delete(*args, **kwargs)

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