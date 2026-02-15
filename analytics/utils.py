from django.db.models import Sum, Count, Q
from accounts.models import User
from gamification.models import StudentXP
from .models import StudentEngagement, PerformanceSnapshot
from institutes.models import Institute


# ==========================================================
# STUDENT TOTAL ENGAGEMENT
# ==========================================================

def get_student_total_engagement(student):
    result = StudentEngagement.objects.filter(
        student=student
    ).aggregate(
        total_minutes=Sum("minutes_spent")
    )

    return result["total_minutes"] or 0


# ==========================================================
# TEACHER → TOP STUDENTS (INSTITUTE FILTERED)
# ==========================================================

def get_top_students(institute, limit=5):
    return (
        StudentXP.objects
        .select_related("student")
        .filter(student__institute=institute)
        .order_by("-total_xp")[:limit]
    )


# ==========================================================
# TEACHER → LAGGING STUDENTS
# ==========================================================

def get_lagging_students(institute, threshold=200):
    return (
        StudentXP.objects
        .select_related("student")
        .filter(
            student__institute=institute,
            total_xp__lt=threshold
        )
        .order_by("total_xp")
    )


# ==========================================================
# ADMIN → GLOBAL TOP STUDENTS
# ==========================================================

def get_global_top_students(limit=10):
    return (
        StudentXP.objects
        .select_related("student")
        .order_by("-total_xp")[:limit]
    )


# ==========================================================
# ADMIN → INSTITUTE STATISTICS
# ==========================================================

def get_institute_statistics():
    return Institute.objects.annotate(
        total_students=Count(
            "user",
            filter=Q(user__role="student")
        ),
        total_teachers=Count(
            "user",
            filter=Q(user__role="teacher")
        )
    )
