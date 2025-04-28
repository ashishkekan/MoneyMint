import csv
import datetime
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import ExpenseForm, RegisterForm
from .models import Expense


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    total_expense = sum(exp.amount for exp in expenses)
    return render(
        request,
        "dashboard.html",
        {"expenses": expenses, "total_expense": total_expense},
    )


@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect("dashboard")
    else:
        form = ExpenseForm()
    return render(request, "add_expense.html", {"form": form})


@login_required
def view_expenses(request):
    expenses = Expense.objects.filter(user=request.user)
    return render(request, "view_expenses.html", {"expenses": expenses})


@login_required
def report(request):
    expenses = Expense.objects.filter(user=request.user)
    today = datetime.date.today()
    weekly_expenses = expenses.filter(date__gte=today - datetime.timedelta(days=7))
    monthly_expenses = expenses.filter(date__month=today.month)
    return render(
        request,
        "report.html",
        {
            "weekly_expenses": weekly_expenses,
            "monthly_expenses": monthly_expenses,
        },
    )


@login_required
def export_json(request):
    expenses = Expense.objects.filter(user=request.user)
    data = [
        {
            "amount": str(exp.amount),
            "description": exp.description,
            "date": str(exp.date),
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
    writer.writerow(["Amount", "Description", "Date"])
    for exp in expenses:
        writer.writerow([exp.amount, exp.description, exp.date])
    return response
