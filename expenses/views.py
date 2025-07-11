import csv
import datetime
import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import BudgetForm, ExpenseForm, ProfileForm, RegisterForm
from .models import Budget, Category, Expense, Profile


def index(request):
    return render(request, "expenses/index.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    return render(request, "expenses/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "expenses/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")


@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    categories = Category.objects.all()
    budget = Budget.objects.filter(user=request.user).first()
    budget_alert = budget and total_expense > budget.amount * Decimal('0.9')

    recent_expenses = expenses.order_by('-date')[:5]
    category_summary = expenses.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    )

    return render(
        request,
        "expenses/dashboard.html",
        {
            "expenses": recent_expenses,
            "total_expense": total_expense,
            "categories": categories,
            "category_summary": category_summary,
            "budget": budget,
            "budget_alert": budget_alert,
        },
    )


@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            try:
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                messages.success(request, "Expense added successfully!")
                return redirect("dashboard")
            except ValidationError as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ExpenseForm()
    return render(request, "expenses/add_expense.html", {"form": form})


@login_required
def view_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        expenses = expenses.filter(category__name=selected_category)
    return render(request, "expenses/view_expenses.html", {"expenses": expenses, "categories": categories})


@login_required
def report(request):
    expenses = Expense.objects.filter(user=request.user)
    today = datetime.date.today()
    time_frames = {
        'weekly': expenses.filter(date__gte=today - datetime.timedelta(days=7)),
        'monthly': expenses.filter(date__month=today.month),
        'yearly': expenses.filter(date__year=today.year),
    }
    category_summary = expenses.values('category__name').annotate(
        total=Sum('amount')
    )
    return render(
        request,
        "expenses/report.html",
        {
            "time_frames": time_frames,
            "category_summary": category_summary,
        },
    )


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "expenses/profile.html", {"form": form})


@login_required
def set_budget(request):
    budget = Budget.objects.filter(user=request.user).first()
    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Budget set successfully!")
            return redirect("dashboard")
    else:
        form = BudgetForm(instance=budget)
    return render(request, "expenses/set_budget.html", {"form": form})


@login_required
def export_json(request):
    expenses = Expense.objects.filter(user=request.user)
    data = [
        {
            "amount": str(exp.amount),
            "description": exp.description,
            "date": str(exp.date),
            "category": exp.category.name if exp.category else "Uncategorized",
        }
        for exp in expenses
    ]
    return JsonResponse(data, safe=False)


@login_required
def export_csv(request):
    expenses = Expense.objects.filter(user=request.user)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(["Amount", "Description", "Date", "Category"])
    for exp in expenses:
        writer.writerow([exp.amount, exp.description, exp.date, exp.category.name if exp.category else "Uncategorized"])
    return response