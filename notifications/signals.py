from django.db.models.signals import post_save
from django.dispatch import receiver
from gamification.models import XPLog, StudentBadge
from .models import Notification


# ===============================
# XP Notification
# ===============================

@receiver(post_save, sender=XPLog)
def create_xp_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.student,
            notification_type="xp",
            title="XP Earned",
            message=f"You earned {instance.xp_earned} XP in {instance.subject.name}.",
        )


# ===============================
# Badge Notification
# ===============================

@receiver(post_save, sender=StudentBadge)
def create_badge_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.student,
            notification_type="badge",
            title="Badge Unlocked!",
            message=f"You unlocked the '{instance.badge.name}' badge.",
        )
