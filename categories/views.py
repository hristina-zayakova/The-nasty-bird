from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Category
from .forms import AddCategoryForm
from django.db.models import Sum, Count
from profiles.models import Profile


# Create your views here.

class AddCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = AddCategoryForm
    template_name = 'categories/add_category.html'
    success_url = reverse_lazy('categories_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class EditCategoryView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = AddCategoryForm
    template_name = 'categories/edit_category.html'
    success_url = reverse_lazy('categories_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(
            user=self.request.user,
            is_active=True
        ).annotate(
            total_expenses=Sum('expenses__amount'),
            expense_count=Count('expenses')
        ).order_by('sort_order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get user's currency
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        user_currency = profile.currency
        context['user_currency'] = user_currency

        # Calculate max amount and chart scale
        categories = self.get_queryset()
        max_amount = 0
        for category in categories:
            if category.total_expenses:
                max_amount = max(max_amount, float(category.total_expenses))

        # Create dynamic Y-axis labels
        if max_amount > 0:
            # Round up to nice numbers
            import math
            scale = 10 ** (len(str(int(max_amount))) - 1)  # 10, 100, 1000, etc.
            chart_max = math.ceil(max_amount / scale) * scale

            # Create 4 Y-axis labels
            y_labels = [
                chart_max,
                chart_max * 0.75,
                chart_max * 0.5,
                chart_max * 0.25,
                0
            ]
        else:
            y_labels = [1000, 750, 500, 250, 0]  # Default when no expenses
            chart_max = 1000

        context['y_labels'] = y_labels
        context['chart_max'] = chart_max

        # Add bar height to each category
        categories_with_height = []
        for category in categories:
            amount = float(category.total_expenses or 0)
            # Scale height between 5px (min) and 200px (max)
            if chart_max > 0:
                height = max(5, int((amount / chart_max) * 200))
            else:
                height = 5

            categories_with_height.append({
                'category': category,
                'bar_height': height,
                'amount': amount
            })

        context['categories_with_data'] = categories_with_height
        return context
