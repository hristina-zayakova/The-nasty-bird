from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

# Create your models here.
class Budget(models.Model):

    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='budgets',
        help_text="Category for this budget (leave empty for overall budget)"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Budget amount"
    )
    period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        default='monthly',
        help_text="Budget period (monthly, weekly, yearly)"
    )
    start_date = models.DateField(
        help_text="When this budget starts"
    )
    end_date = models.DateField(
        help_text="When this budget ends"
    )
    is_active = models.BooleanField(
        default=True,
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about this budget (e.g., 'Saving for vacation')"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        ordering = ['-start_date', 'category__name']
        unique_together = ['user', 'category', 'start_date', 'period']

    def clean(self):
        super().clean()

        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError({'end_date': 'End date must be after start date'})

        if self.category and self.category.user != self.user:
            raise ValidationError({'category': 'Category must belong to the same user'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.category:
            return f"{self.category.name} - ${self.amount} ({self.period})"
        return f"Overall Budget - ${self.amount} ({self.period})"

    def get_total_expenses(self):
        from expenses.models import Expense

        if self.category:
            expenses = Expense.objects.filter(
                user=self.user,
                category=self.category,
                date__gte=self.start_date,
                date__lte=self.end_date
            )
        else:
            expenses = Expense.objects.filter(
                user=self.user,
                date__gte=self.start_date,
                date__lte=self.end_date
            )

        return expenses.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def get_remaining_budget(self):
        return self.amount - self.get_total_expenses()

    def get_budget_percentage_used(self):
        spent = self.get_total_expenses()
        return min((spent / self.amount) * 100, 100)

    def is_over_budget(self):
       return self.get_remaining_budget() < 0

    def days_remaining(self):
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days

    def is_current_period(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date