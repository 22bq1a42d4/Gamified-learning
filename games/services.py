# games/services.py

from gamification.models import StudentXP, XPLog, StudentBadge, Badge, SubjectXP
from django.utils import timezone
from django.db import transaction

def award_xp(student, subject, xp_amount, source="Game Completion"):
    """
    Core service to update student XP across global and subject-specific levels.
    Wrapped in a transaction to ensure data integrity.
    """
    with transaction.atomic():
        # 1. Update Global XP and Level
        student_xp, _ = StudentXP.objects.get_or_create(student=student)
        student_xp.total_xp += xp_amount
        
        # Simple Level Logic: 1 level per 500 XP
        new_level = (student_xp.total_xp // 500) + 1
        student_xp.current_level = new_level
        student_xp.save()

        # 2. Update Subject-Specific XP
        # Uses get_or_create to ensure the subject record exists
        subject_xp, _ = SubjectXP.objects.get_or_create(
            student=student, 
            subject=subject,
            defaults={'xp': 0, 'level': 1}
        )
        subject_xp.xp += xp_amount
        
        # Calculate subject-specific level (e.g., 1 level per 200 XP)
        subject_xp.level = (subject_xp.xp // 200) + 1
        subject_xp.save()

        # 3. Log the transaction for Analytics
        XPLog.objects.create(
            student=student,
            xp_amount=xp_amount,
            reason=source,
            created_at=timezone.now()
        )

        # 4. Trigger Badge Check
        new_badges = check_badges(student, student_xp.total_xp, subject)
        
        return {
            "xp_earned": xp_amount,
            "new_level": student_xp.current_level,
            "new_badges": new_badges
        }

def check_badges(student, total_xp, subject=None):
    """
    Checks if the student has met thresholds for new badges.
    """
    # Get all badges where threshold is met but student doesn't own them yet
    eligible_badges = Badge.objects.filter(xp_threshold__lte=total_xp).exclude(
        id__in=StudentBadge.objects.filter(student=student).values_list('badge_id', flat=True)
    )

    unlocked_badges = []
    for badge in eligible_badges:
        sb, created = StudentBadge.objects.get_or_create(student=student, badge=badge)
        if created:
            unlocked_badges.append(badge.name)
            
    return unlocked_badges