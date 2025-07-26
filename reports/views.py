from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from reports.models import Report
from expenses.models import Expense
from subscriptions.models import Subscription
from budgets.models import Budget

# Create your views here.

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/main_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        now = timezone.now()
        month_start = now.replace(day=1).date()
        month_end = (month_start.replace(month=month_start.month + 1) - timedelta(
            days=1)) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1) - timedelta(
            days=1)

        monthly_expenses = Expense.objects.filter(
            user=user,
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        recent_expenses = Expense.objects.filter(
            user=user
        ).select_related('category').order_by('-date', '-created_at')[:10]

        budget_data = self.get_budget_data(user, month_start, month_end)


        subscription_total = Decimal('300')

        context.update({
            'monthly_expenses': monthly_expenses,
            'recent_expenses': recent_expenses,
            'subscription_total': subscription_total,
            'user_currency': user.profile.currency,
            **budget_data
        })

        return context

    def get_budget_data(self, user, month_start, month_end):
        budget = Budget.objects.filter(
            user=user,
            category=None,
            start_date__lte=month_end,
            end_date__gte=month_start,
            is_active=True
        ).first()

        if budget:
            remaining = budget.get_remaining_budget()
            percentage_used = budget.get_budget_percentage_used()
            is_over = budget.is_over_budget()

            return {
                'budget_amount': budget.amount,
                'budget_remaining': remaining,
                'budget_percentage': percentage_used,
                'is_over_budget': is_over,
            }

        return {
            'budget_amount': None,
            'budget_remaining': None,
            'budget_percentage': None,
            'is_over_budget': False,
        }


def generate_report_view(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')

        from django.contrib import messages
        messages.success(request, f'Generating {report_type} report...')

        return redirect('main_dashboard')

    return redirect('main_dashboard')
