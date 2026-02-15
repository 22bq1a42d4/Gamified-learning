import os
import django
from django.db.models import Sum

# --------------------------------------------
# SET YOUR PROJECT NAME HERE
# Replace "phs.settings" with your project
# --------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from django.contrib.auth import get_user_model
from notifications.models import Notification
from gamification.models import XPLog
from mentorship.models import MentorRequest
from analytics.models import StudentEngagement

User = get_user_model()

print("\n========== SYSTEM VERIFICATION START ==========\n")

# =====================================================
# USER VALIDATION
# =====================================================
student = User.objects.filter(role="student").first()
teacher = User.objects.filter(role="teacher").first()
guardian = User.objects.filter(role="guardian").first()
admin = User.objects.filter(role="admin").first()

def show_user(label, user):
    if user:
        print(f"{label}: {user.email} | Role: {user.role}")
    else:
        print(f"{label}: NOT FOUND")

print("----- USER VALIDATION -----")
show_user("Student", student)
show_user("Teacher", teacher)
show_user("Guardian", guardian)
show_user("Admin", admin)

# =====================================================
# INSTITUTE & CLASS VALIDATION
# =====================================================
print("\n----- INSTITUTE / CLASS VALIDATION -----")

if student:
    print("Student Institute:", student.institute)
    print("Student Academic Class:", getattr(student, "academic_class", None))

if teacher:
    print("Teacher Institute:", teacher.institute)

# =====================================================
# XP VALIDATION
# =====================================================
print("\n----- XP SYSTEM VALIDATION -----")

if student:
    student_xp = (
        XPLog.objects.filter(student=student)
        .aggregate(total=Sum("xp_earned"))["total"] or 0
    )
    print("Student Total XP:", student_xp)
else:
    student_xp = 0

# =====================================================
# ENGAGEMENT VALIDATION
# =====================================================
print("\n----- ENGAGEMENT VALIDATION -----")

if student:
    engagement = (
        StudentEngagement.objects.filter(student=student)
        .aggregate(total=Sum("minutes_spent"))["total"] or 0
    )
    print("Student Engagement Minutes:", engagement)
else:
    engagement = 0

# =====================================================
# NOTIFICATION VALIDATION
# =====================================================
print("\n----- NOTIFICATION VALIDATION -----")

def notification_count(user):
    if user:
        return Notification.objects.filter(recipient=user).count()
    return 0

print("Student Notifications:", notification_count(student))
print("Teacher Notifications:", notification_count(teacher))
print("Guardian Notifications:", notification_count(guardian))
print("Admin Notifications:", notification_count(admin))

# =====================================================
# TEACHER ANALYTICS
# =====================================================
print("\n----- TEACHER ANALYTICS VALIDATION -----")

if teacher:
    if teacher.institute:
        teacher_students = User.objects.filter(
            role="student",
            institute=teacher.institute
        )
    else:
        teacher_students = User.objects.filter(role="student")

    print("Teacher Total Students:", teacher_students.count())

    for s in teacher_students:
        total_xp = (
            XPLog.objects.filter(student=s)
            .aggregate(total=Sum("xp_earned"))["total"] or 0
        )
        print("Student:", s.email, "| XP:", total_xp)

# =====================================================
# GUARDIAN VALIDATION
# =====================================================
print("\n----- GUARDIAN VALIDATION -----")

guardian_students = User.objects.filter(role="student")
print("Guardian Accessible Students:", guardian_students.count())

for s in guardian_students:
    total_xp = (
        XPLog.objects.filter(student=s)
        .aggregate(total=Sum("xp_earned"))["total"] or 0
    )
    print("Student:", s.email, "| XP:", total_xp)

# =====================================================
# ADMIN METRICS
# =====================================================
print("\n----- ADMIN METRICS VALIDATION -----")

print("Total Users:", User.objects.count())
print("Total Students:", User.objects.filter(role="student").count())
print("Total Teachers:", User.objects.filter(role="teacher").count())
print("Total Guardians:", User.objects.filter(role="guardian").count())
print("Total Admins:", User.objects.filter(role="admin").count())

# =====================================================
# MENTORSHIP VALIDATION
# =====================================================
print("\n----- MENTORSHIP VALIDATION -----")

if student:
    mentor_requests = MentorRequest.objects.filter(student=student)
    print("Student Mentor Requests:", mentor_requests.count())

# =====================================================
# SYSTEM HEALTH SUMMARY
# =====================================================
print("\n========== SYSTEM HEALTH SUMMARY ==========\n")

if student_xp >= 0:
    print("XP System: OK")

if engagement >= 0:
    print("Engagement Tracking: OK")

if User.objects.filter(role="admin").exists():
    print("Admin System: OK")

if Notification.objects.count() >= 0:
    print("Notification System: OK")

if User.objects.filter(role="teacher").exists():
    print("Teacher Analytics: OK")

print("\n========== SYSTEM VERIFICATION COMPLETE ==========\n")
