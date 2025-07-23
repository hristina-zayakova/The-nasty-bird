import json
from datetime import timedelta, datetime
from decimal import Decimal

from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Expense
from .forms import AddExpenseForm


# Create your views here.


class AddExpenseView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = AddExpenseForm
    template_name = 'expenses/add_expense.html'
    success_url = reverse_lazy('categories_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Expense "{form.instance.description}" added successfully!')
        return super().form_valid(form)


class EditExpenseView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = AddExpenseForm
    template_name = 'expenses/edit_expense.html'
    success_url = reverse_lazy('categories_list')

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Expense "{form.instance.description}" updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('category_expenses', kwargs={'category_id': self.object.category.id})


class CategoryExpensesView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/category_expenses.html'
    context_object_name = 'expenses'

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Expense.objects.filter(
            user=self.request.user,
            category_id=category_id
        ).order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['category_id']

        # Get the category for context
        from categories.models import Category
        category = Category.objects.get(id=category_id, user=self.request.user)
        context['category'] = category

        # Get user currency
        from profiles.models import Profile
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['user_currency'] = profile.currency

        # Calculate total amount for this category - fix this part
        from django.db.models import Sum
        expenses_queryset = self.get_queryset()
        total = expenses_queryset.aggregate(total_sum=Sum('amount'))['total_sum']

        # Handle None case and convert to float for proper formatting
        if total is None:
            total = 0

        context['total_amount'] = float(total)

        return context


class ExpensesDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'expenses/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get date range from query parameters
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)

        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                pass

        if date_to:
            try:
                end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Base queryset
        expenses_qs = Expense.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('category')

        # Basic statistics
        stats = expenses_qs.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )

        total_expenses = stats['total'] or Decimal('0')
        expenses_count = stats['count'] or 0
        average_expense = total_expenses / expenses_count if expenses_count > 0 else Decimal('0')

        total_days = (end_date - start_date).days + 1
        daily_average = total_expenses / total_days if total_days > 0 else Decimal('0')

        # Top categories
        top_categories = expenses_qs.values(
            'category__name'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:5]

        # Recent expenses
        recent_expenses = expenses_qs.order_by('-date', '-created_at')[:10]

        # Custom chart data
        monthly_chart_data, y_labels = self._get_monthly_chart_data(expenses_qs)

        context.update({
            # Statistics
            'total_expenses': total_expenses,
            'expenses_count': expenses_count,
            'average_expense': average_expense,
            'daily_average': daily_average,

            # Chart data
            'monthly_chart_data': monthly_chart_data,
            'y_labels': y_labels,
            'user_currency': user.profile.currency,

            # Data for template
            'top_categories': top_categories,
            'recent_expenses': recent_expenses,

            # Date range
            'date_from': date_from or start_date.strftime('%Y-%m-%d'),
            'date_to': date_to or end_date.strftime('%Y-%m-%d'),
        })

        return context

    def _get_monthly_chart_data(self, expenses_qs):
        """Get monthly data formatted for custom bar chart"""
        monthly_data = expenses_qs.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')

        # Format for custom chart
        chart_data = []
        max_amount = 0

        for item in monthly_data:
            amount = float(item['total'])
            if amount > max_amount:
                max_amount = amount

            chart_data.append({
                'month': item['month'].strftime('%b'),
                'amount': amount
            })

        # Create clean Y-axis labels and calculate bar heights
        if max_amount > 0:
            import math
            # Round max_amount up to a nice number (nearest 50)
            nice_max = math.ceil(max_amount / 50) * 50
            y_labels = [nice_max, nice_max * 0.75, nice_max * 0.5, nice_max * 0.25, 0]

            # Calculate bar heights based on nice_max instead of actual max_amount
            for item in chart_data:
                item['bar_height'] = int((item['amount'] / nice_max) * 240)
        else:
            y_labels = [0]
            for item in chart_data:
                item['bar_height'] = 5

        return chart_data, y_labels

def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    category_id = expense.category.id
    name = expense.description
    expense.delete()
    messages.success(request, f'Expense "{name}" deleted successfully!')
    return redirect('category_expenses', category_id=category_id)
