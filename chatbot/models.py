from django.db import models
from django.conf import settings
from academics.models import Subject


# ==========================================
# CHAT SESSION
# ==========================================

class ChatSession(models.Model):

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ("student", "subject", "is_active")

    def __str__(self):
        return f"{self.student.email} - {self.subject.name}"


# ==========================================
# CHAT MESSAGE
# ==========================================

class ChatMessage(models.Model):

    ROLE_CHOICES = (
        ("user", "User"),
        ("bot", "Bot"),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    content = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["session", "timestamp"])
        ]

    def __str__(self):
        return f"{self.role} - {self.session.student.email}"
