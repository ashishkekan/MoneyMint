from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.category or 'Uncategorized'}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    period = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('weekly', 'Weekly')])

    def __str__(self):
        return f"{self.user.username} - {self.period} Budget: {self.amount}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_currency = models.CharField(max_length=3, default='INR')
    monthly_budget_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"