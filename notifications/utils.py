from .models import Notification
from accounts.models import User


def broadcast_notification(title, message, role=None):

    users = User.objects.all()

    if role:
        users = users.filter(role=role)

    notifications = [
        Notification(
            recipient=user,
            title=title,
            message=message,
            notification_type="system"
        )
        for user in users
    ]

    Notification.objects.bulk_create(notifications)
