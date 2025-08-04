from django.contrib import messages
from django.shortcuts import render, redirect, reverse
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

    def get_default_context(self, user):
        """Return default dashboard context"""
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

        budget_data = self.get_budget_data(user, month_start, month_end, None)

        subscription_total = Subscription.objects.filter(
            user=user
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        return {
            'monthly_expenses': monthly_expenses,
            'recent_expenses': recent_expenses,
            'subscription_total': subscription_total,
            'user_currency': user.profile.currency,
            'current_month': now.month,
            'current_year': now.year,
            **budget_data
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Check if we should display a specific report
        report_id = self.request.GET.get('report_id')

        if report_id:
            try:
                from .models import Report  # Import Report model
                report = Report.objects.get(id=report_id, user=user)
                context.update(self.get_report_context(report))
            except Report.DoesNotExist:
                # If report doesn't exist, show default dashboard
                context.update(self.get_default_context(user))
        else:
            # No report_id, show default dashboard
            context.update(self.get_default_context(user))

        return context

    def get_budget_data(self, user, period_start, period_end, report_type=None):

        if report_type == 'yearly_overview':

            budgets = Budget.objects.filter(
                user=user,
                category=None,
                start_date__lte=period_end,
                end_date__gte=period_start
            ).order_by('start_date', '-created_at')

            monthly_budgets = {}
            total_budget = Decimal('0')

            for budget in budgets:
                month_key = f"{budget.start_date.year}-{budget.start_date.month:02d}"

                if month_key not in monthly_budgets or budget.created_at > monthly_budgets[month_key].created_at:
                    monthly_budgets[month_key] = budget

            for budget in monthly_budgets.values():
                total_budget += budget.amount

            if total_budget > 0:

                from .models import Report
                current_report = Report.objects.filter(
                    user=user,
                    period_start=period_start,
                    period_end=period_end
                ).order_by('-created_at').first()

                if current_report:
                    total_used = current_report.total_expenses + current_report.total_subscriptions
                    remaining = total_budget - total_used
                    percentage_used = (total_used / total_budget) * 100
                    is_over = total_used > total_budget

                    # Add over_degrees calculation
                    if percentage_used > 100:
                        over_percentage_display = percentage_used - 100
                        over_degrees = float(min(percentage_used - 100, 50)) * 3.6
                    else:
                        over_percentage_display = 0
                        over_degrees = 0

                    return {
                        'budget_amount': total_budget,
                        'budget_remaining': remaining,
                        'budget_percentage': percentage_used,
                        'is_over_budget': is_over,
                        'over_degrees': over_degrees,
                        'over_percentage_display': over_percentage_display,
                    }


            return {
                'budget_amount': None,
                'budget_remaining': None,
                'budget_percentage': None,
                'is_over_budget': False,
                'over_degrees': 0,
                'over_percentage_display': 0,
            }

        else:

            budget = Budget.objects.filter(
                user=user,
                category=None,
                start_date__lte=period_end,
                end_date__gte=period_start
            ).order_by('-created_at').first()

            if budget:
                remaining = budget.get_remaining_budget()
                percentage_used = budget.get_budget_percentage_used()
                is_over = budget.is_over_budget()

                # Add over_degrees calculation
                if percentage_used > 100:
                    over_percentage_display = percentage_used - 100
                    over_degrees = float(min(percentage_used - 100, 50)) * 3.6
                else:
                    over_percentage_display = 0
                    over_degrees = 0

                return {
                    'budget_amount': budget.amount,
                    'budget_remaining': remaining,
                    'budget_percentage': percentage_used,
                    'is_over_budget': is_over,
                    'over_degrees': over_degrees,
                    'over_percentage_display': over_percentage_display,
                }

            return {
                'budget_amount': None,
                'budget_remaining': None,
                'budget_percentage': None,
                'is_over_budget': False,
                'over_degrees': 0,
                'over_percentage_display': 0,
            }

    def get_report_context(self, report):

        from expenses.models import Expense

        base_context = {
            'monthly_expenses': report.total_expenses,
            'subscription_total': report.total_subscriptions,
            'budget_utilization': report.budget_utilization,
            'report_type': report.report_type,
            'period_start': report.period_start,
            'period_end': report.period_end,
            'user_currency': report.user.profile.currency,
            'current_month': report.period_start.month,
            'current_year': report.period_start.year,
        }

        budget_data = self.get_budget_data(report.user, report.period_start, report.period_end, report.report_type)
        base_context.update(budget_data)

        if report.report_type == 'monthly_summary':
            recent_expenses = Expense.objects.filter(
                user=report.user,
                date__gte=report.period_start,
                date__lte=report.period_end
            ).select_related('category').order_by('-date', '-created_at')[:10]

            base_context.update({
                'recent_expenses': recent_expenses,
                'show_monthly_summary': True,
            })

        elif report.report_type == 'yearly_overview':
            recent_expenses = Expense.objects.filter(
                user=report.user,
                date__gte=report.period_start,
                date__lte=report.period_end
            ).select_related('category').order_by('-date', '-created_at')[:10]

            base_context.update({
                'recent_expenses': recent_expenses,
                'show_yearly_overview': True,
                'card_period_text': 'this year',
            })

        return base_context


def generate_report_view(request):
    period_start = None
    period_end = None
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        selected_month = int(request.POST.get('month'))
        selected_year = int(request.POST.get('year'))
        user = request.user

        # Calculate period based on report type and user selection
        if report_type == 'monthly_summary':
            period_start = datetime(selected_year, selected_month, 1).date()
            if selected_month == 12:
                period_end = datetime(selected_year + 1, 1, 1).date() - timedelta(days=1)
            else:
                period_end = datetime(selected_year, selected_month + 1, 1).date() - timedelta(days=1)

        elif report_type == 'yearly_overview':
            period_start = datetime(selected_year, 1, 1).date()
            period_end = datetime(selected_year, 12, 31).date()

        else:
            # Fallback to current month if invalid report type
            now = timezone.now().date()
            period_start = now.replace(day=1)
            period_end = (period_start.replace(month=period_start.month + 1) - timedelta(
                days=1)) if period_start.month < 12 else period_start.replace(year=period_start.year + 1,
                                                                              month=1) - timedelta(days=1)

        try:
            # Create the report
            report = Report.objects.create(
                user=user,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end
            )

            # Add success message
            messages.success(request, f'Generated {dict(Report.REPORT_TYPES)[report_type]} successfully!')

            # Redirect to dashboard showing this report
            return redirect(f"{reverse('main_dashboard')}?report_id={report.id}")

        except Exception as e:
            # Handle any errors during report creation
            messages.error(request, f'Error generating report: {str(e)}')
            return redirect('main_dashboard')

    return redirect('main_dashboard')