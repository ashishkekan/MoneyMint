from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Budget, Category, Expense, Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class ExpenseForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Expense
        fields = ["amount", "description", "category"]
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Enter description'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Enter amount', 'min': '0.01', 'step': '0.01'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['preferred_currency', 'monthly_budget_limit']
        widgets = {
            'preferred_currency': forms.Select(choices=[('INR', 'INR'), ('USD', 'USD'), ('EUR', 'EUR')]),
            'monthly_budget_limit': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['amount', 'period']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'period': forms.Select(choices=[('monthly', 'Monthly'), ('weekly', 'Weekly')]),
        }