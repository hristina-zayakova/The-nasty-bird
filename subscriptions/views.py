from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum
from .models import Subscription
from .forms import AddSubscriptionForm

# Create your views here.

class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscriptions/subscription_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('next_payment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from profiles.models import Profile
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['user_currency'] = profile.currency

        subscriptions = self.get_queryset()
        monthly_total = 0
        yearly_total = 0

        for sub in subscriptions:
            if sub.frequency == 'monthly':
                monthly_total += float(sub.amount)
                yearly_total += float(sub.amount) * 12
            elif sub.frequency == 'yearly':
                yearly_total += float(sub.amount)
                monthly_total += float(sub.amount) / 12

        context['monthly_total'] = monthly_total
        context['yearly_total'] = yearly_total

        return context


class AddSubscriptionView(LoginRequiredMixin, CreateView):
    model = Subscription
    form_class = AddSubscriptionForm
    template_name = 'subscriptions/add_subscription.html'
    success_url = reverse_lazy('subscription_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Subscription "{form.instance.name}" added successfully!')
        return super().form_valid(form)


class EditSubscriptionView(LoginRequiredMixin, UpdateView):
    model = Subscription
    form_class = AddSubscriptionForm
    template_name = 'subscriptions/edit_subscription.html'
    success_url = reverse_lazy('subscription_list')

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Subscription "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class DeleteSubscriptionView(LoginRequiredMixin, DeleteView):
    model = Subscription
    success_url = reverse_lazy('subscription_list')

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        # Skip template entirely, just delete and redirect
        obj = self.get_object()
        messages.success(request, f'Subscription "{obj.name}" deleted successfully!')
        obj.delete()
        return HttpResponseRedirect(self.success_url)