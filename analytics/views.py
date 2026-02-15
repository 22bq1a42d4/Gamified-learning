from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.db.models import Count

import csv
from django.http import HttpResponse
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from gamification.models import StudentXP
from accounts.models import User

from institutes.models import Institute

from .models import StudentEngagement
from .utils import (
    get_top_students,
    get_lagging_students,
    get_student_total_engagement,
    get_global_top_students,
    get_institute_statistics
)


# ==========================================================
# STUDENT ANALYTICS
# ==========================================================

@login_required
@role_required("student")
def student_analytics_view(request):

    student_xp = StudentXP.objects.filter(
        student=request.user
    ).select_related("current_level").first()

    engagement_time = get_student_total_engagement(request.user)

    total_games = request.user.studentattempt_set.count()

    context = {
        "student_xp": student_xp,
        "engagement_time": engagement_time,
        "total_games": total_games,
    }

    return render(
        request,
        "analytics/student_analytics.html",
        context
    )


# ==========================================================
# TEACHER ANALYTICS
# ==========================================================

@login_required
@role_required("teacher")
def teacher_analytics_view(request):

    institute = request.user.institute

    students = User.objects.filter(
        role="student",
        institute=institute
    )

    student_xps = StudentXP.objects.filter(student__in=students)

    total_students = students.count()

    average_xp = student_xps.aggregate(
        avg_xp=Avg("total_xp")
    )["avg_xp"] or 0

    # Top performers (Top 5)
    top_students = student_xps.order_by("-total_xp")[:5]

    # Lagging students (< 200 XP threshold)
    lagging_students = student_xps.filter(total_xp__lt=200)

    context = {
        "top_students": top_students,
        "lagging_students": lagging_students,
        "total_students": total_students,
        "average_xp": int(average_xp),
    }

    return render(
        request,
        "analytics/teacher_analytics.html",
        context
    )


@login_required
@role_required("teacher")
def download_intelligence_report(request):

    institute = request.user.institute

    students = StudentXP.objects.filter(
        student__institute=institute
    ).select_related("student")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="intelligence_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Student Email", "Class", "Total XP"])

    for profile in students:
        writer.writerow([
            profile.student.email,
            profile.student.class_studying,
            profile.total_xp,
        ])

    return response
@login_required
@role_required("teacher")
def audit_student_profile(request, student_id):

    institute = request.user.institute

    student = get_object_or_404(
        User,
        id=student_id,
        role="student",
        institute=institute
    )

    xp_profile = StudentXP.objects.filter(student=student).first()

    context = {
        "student": student,
        "xp_profile": xp_profile,
    }

    return render(
        request,
        "analytics/audit_profile.html",
        context
    )


@login_required
@role_required("teacher")
def audit_student_profile(request, student_id):

    institute = request.user.institute

    student = get_object_or_404(
        User,
        id=student_id,
        role="student",
        institute=institute
    )

    xp_profile = StudentXP.objects.filter(student=student).first()

    context = {
        "student": student,
        "xp_profile": xp_profile,
    }

    return render(
        request,
        "analytics/audit_profile.html",
        context
    )

@login_required
@role_required("teacher")
def message_student_view(request, student_id):

    institute = request.user.institute

    student = get_object_or_404(
        User,
        id=student_id,
        role="student",
        institute=institute
    )

    if request.method == "POST":
        message_text = request.POST.get("message")

        # For now just confirmation (can integrate notifications later)
        messages.success(request, f"Message sent to {student.email}")

        return redirect("analytics:teacher")

    return render(
        request,
        "analytics/message_student.html",
        {"student": student}
    )


# ==========================================================
# ADMIN ANALYTICS
# ==========================================================

@login_required
@role_required("admin")
def admin_analytics_view(request):

    total_users = User.objects.count()
    total_students = User.objects.filter(role="student").count()
    total_teachers = User.objects.filter(role="teacher").count()
    total_institutes = Institute.objects.count()

    global_top_students = get_global_top_students()
    institute_stats = get_institute_statistics()

    context = {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_institutes": total_institutes,
        "global_top_students": global_top_students,
        "institute_stats": institute_stats,
    }

    return render(
        request,
        "analytics/admin_analytics.html",
        context
    )
