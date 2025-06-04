from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add/", views.add_expense, name="add_expense"),
    path("view/", views.view_expenses, name="view_expenses"),
    path("report/", views.report, name="report"),
    path("export/json/", views.export_json, name="export_json"),
    path("export/csv/", views.export_csv, name="export_csv"),
]
