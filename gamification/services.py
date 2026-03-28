# gamification/services.py
from .models import StudentXP, SubjectXP, XPLog, Badge, StudentBadge, Level
from notifications.models import Notification
from django.db import transaction
from django.utils import timezone

@transaction.atomic
def award_xp_to_student(student, subject, xp_amount, source="Game Completion"):
    """
    Master service to update student progress across all modules.
    """
    # 1. Get or Create Global XP Profile
    xp_profile, _ = StudentXP.objects.get_or_create(student=student)
    
    # 2. Get or Create Subject-Specific XP
    subject_xp, _ = SubjectXP.objects.get_or_create(
        student=student,
        subject=subject
    )

    # 3. Add XP and check for Global Level Up
    # Uses the add_xp method defined in your StudentXP model
    level_up, new_level = xp_profile.add_xp(xp_amount)

    # 4. Update Subject XP
    subject_xp.xp += xp_amount
    subject_xp.save()

    # 5. Log the Transaction
    XPLog.objects.create(
        student=student,
        subject=subject,
        xp_earned=xp_amount,
        source=source,
        timestamp=timezone.now()
    )

    # 6. Level Up Notification
    if level_up and new_level:
        Notification.objects.create(
            recipient=student,
            title="Level Up! 🚀",
            message=f"Fantastic! You've reached {new_level.level_number}. Keep it up!",
            notification_type="system"
        )

    # 7. Check and Unlock Badges
    unlocked = unlock_badges_logic(student, xp_profile.total_xp)

    return {
        "status": "success",
        "xp_profile": xp_profile,
        "level_up": level_up,
        "new_level": new_level.level_number if new_level else None,
        "unlocked_badges": unlocked
    }

def unlock_badges_logic(student, total_xp):
    """
    Checks thresholds and grants new badges.
    """
    eligible_badges = Badge.objects.filter(xp_threshold__lte=total_xp)
    newly_unlocked = []

    for badge in eligible_badges:
        # get_or_create returns (object, created_bool)
        obj, created = StudentBadge.objects.get_or_create(
            student=student,
            badge=badge
        )

        if created:
            newly_unlocked.append(badge.name)
            Notification.objects.create(
                recipient=student,
                title="New Achievement! 🏆",
                message=f"You've earned the '{badge.name}' badge!",
                notification_type="xp"
            )
            
    return newly_unlocked