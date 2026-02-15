from .models import StudentXP, SubjectXP, XPLog, Badge, StudentBadge
from notifications.models import Notification
from django.db import transaction


@transaction.atomic
def award_xp(student, subject, xp_amount, source="Game Completion"):

    xp_profile, _ = StudentXP.objects.get_or_create(student=student)
    subject_xp, _ = SubjectXP.objects.get_or_create(
        student=student,
        subject=subject
    )

    # Add XP
    level_up, new_level = xp_profile.add_xp(xp_amount)

    subject_xp.xp += xp_amount
    subject_xp.save()

    # Log XP
    XPLog.objects.create(
        student=student,
        subject=subject,
        xp_earned=xp_amount,
        source=source
    )

    # Level Up Notification
    if level_up:
        Notification.objects.create(
            recipient=student,
            title="Level Up!",
            message=f"You reached Level {new_level.level_number}"
        )

    # Badge Check
    unlock_badges(student)

    return xp_profile


def unlock_badges(student):

    xp_profile = student.xp_profile

    eligible_badges = Badge.objects.filter(
        xp_threshold__lte=xp_profile.total_xp
    )

    for badge in eligible_badges:
        created = StudentBadge.objects.get_or_create(
            student=student,
            badge=badge
        )[1]

        if created:
            Notification.objects.create(
                recipient=student,
                title="New Badge Unlocked!",
                message=f"You unlocked {badge.name}"
            )
