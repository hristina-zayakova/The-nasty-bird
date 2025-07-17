from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal



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
        help_text="Subscription name (e.g., Netflix, Spotify)"
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
    next_payment_date = models.DateField(
        help_text="Next payment date"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['next_payment_date', 'name']

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.frequency})"