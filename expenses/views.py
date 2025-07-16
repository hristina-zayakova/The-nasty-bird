from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView
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

