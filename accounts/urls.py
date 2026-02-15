# accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = "accounts"

urlpatterns = [

    # ==========================
    # PUBLIC ROUTES
    # ==========================
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),

    # ==========================
    # DASHBOARDS (Role Based)
    # ==========================
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("dashboard/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/guardian/", views.guardian_dashboard, name="guardian_dashboard"),

    # ==========================
    # PASSWORD RESET FLOW
    # ==========================

    # Step 1: Enter Email
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),

    # Step 2: Email Sent Page
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    # Step 3: Link from Email
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),

    # Step 4: Success Page
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("profile/", views.profile_view, name="profile"),
]
