from django import forms
from .models import Expense
from categories.models import Category


class AddExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'category', 'date']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'category-form-input',
                'placeholder': 'Enter expense description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'category-form-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={
                'class': 'category-form-input'
            }),
            'date': forms.DateInput(attrs={
                'class': 'category-form-input',
                'type': 'date'
            })
        }
        labels = {
            'description': 'Name',
            'amount': 'Amount',
            'category': 'Category',
            'date': 'Date'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                is_active=True
            )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0')
        return amount