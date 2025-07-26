from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, Count

# Create your models here.
user = get_user_model()


class Report(models.Model):
    REPORT_TYPES = [
        ('monthly_summary', 'Monthly Financial Summary'),
        ('category_breakdown', 'Category Analysis Report'),
        ('budget_performance', 'Budget vs Actual Report'),
        ('subscription_analysis', 'Subscription Cost Analysis'),
        ('yearly_overview', 'Annual Financial Overview'),
    ]

    user = models.ForeignKey(
        user,
        on_delete=models.CASCADE
    )
    report_type = models.CharField(
        max_length=120,
        choices=REPORT_TYPES
    )

    period_start = models.DateField()
    period_end = models.DateField()

    total_expenses = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    total_subscriptions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    budget_utilization = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    categories_analyzed = models.IntegerField(
        default=0
    )
    transactions_count = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Financial Report'
        verbose_name_plural = 'Financial Reports'


    def save(self, *args, **kwargs):
        self.calculate_report_data()
        super().save(*args, **kwargs)

    def calculate_report_data(self):
        from expenses.models import Expense
        from subscriptions.models import Subscription
        from budgets.models import Budget

        expenses_qs = Expense.objects.filter(
            user=self.user,
            date__gte=self.period_start,
            date__lte=self.period_end
        )

        expense_stats = expenses_qs.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )

        self.total_expenses = expense_stats['total'] or Decimal('0')
        self.transactions_count = expense_stats['count'] or 0
        self.categories_analyzed = expenses_qs.values('category').distinct().count()

        if hasattr(self.user, 'subscriptions'):
            subscription_stats = Subscription.objects.filter(
                user=self.user,
            ).aggregate(total=Sum('amount'))

            self.total_subscriptions = subscription_stats['total'] or Decimal('0')

        budget = Budget.objects.filter(
            user=self.user,
            start_date__lte=self.period_end,
            end_date__gte=self.period_start,
            is_active=True
        ).first()

        if budget and budget.amount > 0:
            utilization = (self.total_expenses / budget.amount) * 100
            self.budget_utilization = min(utilization, Decimal('999.99'))
        else:
            self.budget_utilization = None
