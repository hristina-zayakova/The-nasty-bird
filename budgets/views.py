from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Budget
from .forms import AddBudgetForm

# Create your views here.
class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user, is_active=True).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from profiles.models import Profile
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['user_currency'] = profile.currency

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.cleaned_data.get('category') == '':
            form.instance.category = None
        messages.success(self.request, 'Budget set successfully!')
        return super().form_valid(form)

class SetBudgetView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = AddBudgetForm
    template_name = 'budgets/set_budget.html'
    success_url = reverse_lazy('budget_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.cleaned_data['category'] == '':
            form.instance.category = None
        messages.success(self.request, 'Budget set successfully!')
        return super().form_valid(form)


class EditBudgetView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = AddBudgetForm
    template_name = 'budgets/edit_budget.html'
    success_url = reverse_lazy('budget_list')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if form.cleaned_data['category'] == '':
            form.instance.category = None
        messages.success(self.request, 'Budget updated successfully!')
        return super().form_valid(form)


def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    name = str(budget)
    budget.delete()
    messages.success(request, f'Budget "{name}" deleted successfully!')
    return redirect('budget_list')
