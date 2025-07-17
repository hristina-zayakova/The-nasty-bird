from django import forms
from .models import Budget
from categories.models import Category


class AddBudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period', 'start_date', 'end_date']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'category-form-input'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'category-form-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'period': forms.Select(attrs={
                'class': 'category-form-input'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'category-form-input',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'category-form-input',
                'type': 'date'
            })
        }
        labels = {
            'category': 'Category',
            'amount': 'Amount',
            'period': 'Type',
            'start_date': 'Start Date',
            'end_date': 'End Date'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            choices = [('', 'Overall Budget')]
            categories = Category.objects.filter(user=user, is_active=True)
            choices.extend([(str(cat.id), cat.name) for cat in categories])
            self.fields['category'].choices = choices
            self.fields['category'].required = False

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0')
        return amount