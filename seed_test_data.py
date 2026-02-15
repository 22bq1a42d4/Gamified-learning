import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from institutes.models import Institute
from academics.models import AcademicClass, Subject
from gamification.models import (
    Level,
    Badge,
    StudentXP,
    SubjectXP,
    XPLog,
    StudentBadge,
)
from analytics.models import StudentEngagement
from notifications.models import Notification
from mentorship.models import MentorRequest

User = get_user_model()

print("\n========== PRODUCTION USER DATA SEED START ==========\n")

# =====================================================
# SAFE USER FETCH
# =====================================================
student = User.objects.get(role="student", email="harisaiparasa@gmail.com")
teacher = User.objects.get(role="teacher", email="harisaiparsa.ai@gmail.com")
guardian = User.objects.get(role="guardian", email="parasaharisai@gmail.com")
admin = User.objects.filter(role="admin").first()

if not admin:
    raise Exception("Admin user not found.")

print("Users Loaded")

# =====================================================
# LEVELS (IDEMPOTENT)
# =====================================================
levels_data = [(1, 0), (2, 100), (3, 250), (4, 500)]

for number, xp in levels_data:
    Level.objects.get_or_create(
        level_number=number,
        defaults={"xp_required": xp}
    )

print("Levels Ready")

# =====================================================
# BADGE
# =====================================================
badge, _ = Badge.objects.get_or_create(
    name="XP Starter",
    defaults={
        "description": "Earn 100 XP",
        "xp_threshold": 100,
        "icon": "star"
    }
)

print("Badge Ready")

# =====================================================
# INSTITUTE (UNIQUE CODE SAFE)
# =====================================================
institute, _ = Institute.objects.get_or_create(
    code="PHS001",
    defaults={"name": "PHS Rural Institute"}
)

# Assign institute safely
if student.institute != institute:
    student.institute = institute
    student.save()

if teacher.institute != institute:
    teacher.institute = institute
    teacher.save()

print("Institute Ready & Assigned")

# =====================================================
# ACADEMIC CLASS (GRADE UNIQUE FIXED)
# =====================================================
academic_class = AcademicClass.objects.filter(grade=10).first()

if not academic_class:
    academic_class = AcademicClass.objects.create(grade=10)

# If model has user field
if hasattr(academic_class, "user"):
    academic_class.user = student
    academic_class.save()

print("Academic Class Ready")

# =====================================================
# SUBJECT (WITH REQUIRED FKs)
# =====================================================
subject, _ = Subject.objects.get_or_create(
    name="Mathematics",
    academic_class=academic_class,
    institute=institute
)

print("Subject Ready")

# =====================================================
# STUDENT XP PROFILE
# =====================================================
xp_profile, _ = StudentXP.objects.get_or_create(student=student)

print("StudentXP Profile Ready")

# =====================================================
# ADD XP LOGS (SAFE MULTIPLE RUN)
# =====================================================
total_xp_added = 0

for i in range(5):
    xp_amount = random.randint(40, 80)

    XPLog.objects.create(
        student=student,
        subject=subject,
        xp_earned=xp_amount,
        source="Game Completion"
    )

    xp_profile.add_xp(xp_amount)
    total_xp_added += xp_amount

print("XP Logs Added:", total_xp_added)

# =====================================================
# SUBJECT XP UPDATE
# =====================================================
subject_xp, _ = SubjectXP.objects.get_or_create(
    student=student,
    subject=subject
)

subject_xp.xp += total_xp_added
subject_xp.save()

print("SubjectXP Updated")

# =====================================================
# BADGE UNLOCK CHECK
# =====================================================
if xp_profile.total_xp >= badge.xp_threshold:
    StudentBadge.objects.get_or_create(
        student=student,
        badge=badge
    )
    print("Badge Unlocked")

# =====================================================
# ENGAGEMENT DATA
# =====================================================
for _ in range(5):
    StudentEngagement.objects.create(
        student=student,
        minutes_spent=random.randint(30, 120)
    )

print("Engagement Data Added")

# =====================================================
# NOTIFICATIONS (SAFE ADD)
# =====================================================
Notification.objects.create(
    recipient=student,
    message="You earned XP from Mathematics!"
)

Notification.objects.create(
    recipient=teacher,
    message="Student Harisai gained XP."
)

Notification.objects.create(
    recipient=guardian,
    message="Your child made progress in Mathematics."
)

Notification.objects.create(
    recipient=admin,
    message="System activity recorded."
)

print("Notifications Created")

# =====================================================
# MENTOR RELATIONSHIP
# =====================================================
MentorRequest.objects.get_or_create(
    student=student,
    teacher=teacher,
    defaults={"status": "approved"}
)

print("Mentor Relationship Ready")

# =====================================================
# SUMMARY
# =====================================================
final_total_xp = (
    XPLog.objects.filter(student=student)
    .aggregate(total=Sum("xp_earned"))["total"] or 0
)

print("\nFinal Student Total XP:", final_total_xp)
print("Current Level:", xp_profile.current_level)
print("Streak Days:", xp_profile.streak_days)

print("\n========== PRODUCTION USER DATA SEED COMPLETE ==========\n")
