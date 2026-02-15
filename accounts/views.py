# =====================================================
# IMPORTS
# =====================================================

import random
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django import forms
from accounts.models import User  # Safe import of custom user model
from games.models import StudentAttempt
from analytics.models import StudentEngagement

from .decorators import role_required
from .models import EmailOTP

# Gamification imports
from gamification.models import (
    StudentXP,
    Level,
    StudentBadge,
    XPLog,
    SubjectXP,
)

# Safe Custom User Model
User = apps.get_model(settings.AUTH_USER_MODEL)


# =====================================================
# LANDING PAGE
# =====================================================

def home_view(request):
    return render(request, "landing.html")


# =====================================================
# SIGNUP
# =====================================================

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")
        class_studying = request.POST.get("class_studying")
        stream = request.POST.get("stream")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("accounts:signup")

        if User.objects.filter(email=email).exists():
            messages.info(request, "User already exists.")
            return redirect("accounts:login")

        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            class_studying=class_studying if role == "student" else None,
            stream=stream if role == "student" else None,
            is_active=False,
        )

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(student=user, defaults={"otp": otp})

        send_mail(
            subject="Verify your Gamified Learning account",
            message=f"Your OTP is {otp}. It expires in 10 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        request.session["verify_user"] = user.id
        return redirect("accounts:verify_otp")

    return render(request, "accounts/signup.html")


# =====================================================
# OTP VERIFY
# =====================================================

def verify_otp_view(request):
    user_id = request.session.get("verify_user")

    if not user_id:
        return redirect("accounts:signup")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        otp_obj = EmailOTP.objects.filter(student=user).first()

        if otp_obj and not otp_obj.is_expired() and entered_otp == otp_obj.otp:
            user.is_active = True
            user.is_verified = True
            user.save()

            otp_obj.delete()
            del request.session["verify_user"]

            messages.success(request, "Email verified successfully.")
            return redirect("accounts:login")

        messages.error(request, "Invalid or expired OTP.")

    return render(request, "accounts/verify_otp.html")


# =====================================================
# LOGIN
# =====================================================

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=email, password=password)

        if user:
            if not user.is_verified:
                messages.error(request, "Please verify your email first.")
                return redirect("accounts:login")

            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)

            user.login_count += 1
            user.save()

            return redirect_dashboard(user)

        messages.error(request, "Invalid credentials.")

    return render(request, "accounts/login.html")


# =====================================================
# STUDENT DASHBOARD
# =====================================================

@login_required
@role_required("student")
def student_dashboard(request):
    user = request.user

    student_xp, _ = StudentXP.objects.get_or_create(student=user)
    total_xp = student_xp.total_xp

    levels = Level.objects.order_by("level_number")

    current_level = None
    next_level = None

    for level in levels:
        if total_xp >= level.xp_required:
            current_level = level
        elif not next_level:
            next_level = level
            break

    if not current_level:
        current_level = levels.first()

    if not next_level:
        next_level = levels.last()

    xp_needed = next_level.xp_required if next_level else 1
    xp_percentage = min((total_xp / xp_needed) * 100, 100)

    subject_progress = SubjectXP.objects.filter(student=user)
    for subject in subject_progress:
        subject.progress_percent = min((subject.xp / 500) * 100, 100)

    earned_badges = StudentBadge.objects.filter(student=user).select_related("badge")
    recent_logs = XPLog.objects.filter(student=user).order_by("-timestamp")[:5]

    context = {
        "student_xp": student_xp,
        "current_level": current_level,
        "next_level_xp": next_level.xp_required if next_level else 0,
        "xp_percentage": xp_percentage,
        "subject_progress": subject_progress,
        "earned_badges": earned_badges,
        "recent_logs": recent_logs,
        "streak_count": student_xp.streak_days,
    }

    return render(request, "accounts/student_dashboard.html", context)


# =====================================================
# TEACHER DASHBOARD (PRODUCTION VERSION)
# =====================================================

@login_required
@role_required("teacher")
def teacher_dashboard(request):

    teacher = request.user

    # Assigned students (mentor relationship required in User model)
    students = User.objects.filter(role="student", mentor=teacher)

    total_students = students.count()

    student_xps = StudentXP.objects.filter(student__in=students)

    # Total XP & Average
    total_xp = sum([xp.total_xp for xp in student_xps])
    avg_xp = int(total_xp / total_students) if total_students > 0 else 0

    # Lagging students (below 300 XP threshold)
    lagging_students = student_xps.filter(total_xp__lt=300)
    lagging_count = lagging_students.count()

    # Top 5 students
    top_students = student_xps.order_by("-total_xp")[:5]

    # Total engagement time (if analytics app exists)
    try:
        from analytics.models import StudentEngagement
        engagement_data = StudentEngagement.objects.filter(student__in=students)
        total_engagement_time = sum([e.total_time_minutes for e in engagement_data])
    except:
        total_engagement_time = 0

    context = {
        "total_students": total_students,
        "avg_xp": avg_xp,
        "lagging_count": lagging_count,
        "top_students": top_students,
        "total_engagement_time": total_engagement_time,
    }

    return render(request, "accounts/teacher_dashboard.html", context)


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@login_required
@role_required("admin")
def admin_dashboard(request):

    total_users = User.objects.count()
    total_students = User.objects.filter(role="student").count()
    total_teachers = User.objects.filter(role="teacher").count()
    total_guardians = User.objects.filter(role="guardian").count()

    context = {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_guardians": total_guardians,
    }

    return render(request, "accounts/admin_dashboard.html", context)


# =====================================================
# GUARDIAN DASHBOARD
# =====================================================

@login_required
@role_required("guardian")
def guardian_dashboard(request):
    guardian = request.user

    # Get students assigned to this guardian
    students = User.objects.filter(
        role=User.STUDENT,
        guardian=guardian  # Make sure you have this FK in User model
    ).select_related("academic_class", "institute")

    student_data = []

    for student in students:
        attempts = StudentAttempt.objects.filter(student=student)

        total_xp = sum(attempt.xp_earned for attempt in attempts)
        total_games = attempts.count()

        engagement = StudentEngagement.objects.filter(student=student).first()
        engagement_minutes = engagement.total_minutes if engagement else 0

        student_data.append({
            "student": student,
            "total_xp": total_xp,
            "total_games": total_games,
            "engagement_minutes": engagement_minutes,
        })

    context = {
        "guardian": guardian,
        "student_data": student_data,
    }

    return render(request, "accounts/guardian_dashboard.html", context)


# =====================================================
# ROLE REDIRECTION
# =====================================================

def redirect_dashboard(user):
    if user.role == "admin":
        return redirect("accounts:admin_dashboard")
    if user.role == "teacher":
        return redirect("accounts:teacher_dashboard")
    if user.role == "student":
        return redirect("accounts:student_dashboard")
    if user.role == "guardian":
        return redirect("accounts:guardian_dashboard")
    return redirect("accounts:login")


# =====================================================
# LOGOUT
# =====================================================

@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# =====================================================
# PROFILE UPDATE FORM
# =====================================================

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]  # Extend if needed


# =====================================================
# PROFILE VIEW
# =====================================================

@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {
        "form": form,
    }

    return render(request, "accounts/profile.html", context)
