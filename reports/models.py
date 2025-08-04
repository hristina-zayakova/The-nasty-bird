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

        subscription_total = Decimal('0')
        period_subscriptions = Subscription.objects.filter(
            user=self.user,
            created_at__date__lte=self.period_end,
        )

        for sub in period_subscriptions:
            if sub.frequency == 'monthly':
                if sub.created_at.date() <= self.period_end:
                    if self.report_type == 'yearly_overview':
                        sub_start = max(sub.created_at.date().replace(day=1), self.period_start)
                        months_active = ((self.period_end.year - sub_start.year) * 12 +
                                         (self.period_end.month - sub_start.month) + 1)
                        subscription_total += sub.amount * months_active
                    else:
                        subscription_total += sub.amount
            elif sub.frequency == 'yearly':
                if sub.created_at.date() <= self.period_end:
                    subscription_total += sub.amount

        self.total_subscriptions = subscription_total

        budget = Budget.objects.filter(
            user=self.user,
            category=None,
            start_date__lte=self.period_end,
            end_date__gte=self.period_start
        ).order_by('-created_at').first()

        if budget and budget.amount > 0:
            total_used = self.total_expenses + subscription_total
            utilization = (total_used / budget.amount) * 100
            self.budget_utilization = utilization
        else:
            self.budget_utilization = None
