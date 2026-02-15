# games/services.py

from gamification.models import StudentXP, XPLog, StudentBadge, Badge
from django.utils import timezone


def award_xp(student, subject, xp_amount, game_title):
    # Update global XP
    student_xp, _ = StudentXP.objects.get_or_create(student=student)
    student_xp.total_xp += xp_amount
    student_xp.save()

    # Subject XP
    subject_xp = student_xp.subjectxp_set.filter(subject=subject).first()
    if subject_xp:
        subject_xp.xp += xp_amount
        subject_xp.save()

    # Log
    XPLog.objects.create(
        student=student,
        xp_amount=xp_amount,
        reason=f"Completed {game_title}",
        created_at=timezone.now()
    )

    # Check badges
    check_badges(student, student_xp.total_xp)


def check_badges(student, total_xp):
    badges = Badge.objects.filter(xp_threshold__lte=total_xp)

    for badge in badges:
        StudentBadge.objects.get_or_create(student=student, badge=badge)
