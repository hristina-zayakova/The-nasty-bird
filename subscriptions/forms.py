from django import forms
from .models import Subscription

class AddSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'amount', 'frequency', 'next_payment_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'category-form-input',
                'placeholder': 'Enter subscription name'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'category-form-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'frequency': forms.Select(attrs={
                'class': 'category-form-input'
            }),
            'next_payment_date': forms.DateInput(attrs={
                'class': 'category-form-input',
                'type': 'date'
            })
        }
        labels = {
            'name': 'Name',
            'amount': 'Amount',
            'frequency': 'Type',
            'next_payment_date': 'Date'
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0')
        return amount