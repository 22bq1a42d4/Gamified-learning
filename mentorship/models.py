# mentorship/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class MentorRequest(models.Model):
    """
    Student requests a Teacher as mentor.
    Teacher can approve or reject.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor_requests_sent",
        limit_choices_to={"role": "student"},
    )

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor_requests_received",
        limit_choices_to={"role": "teacher"},
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("student", "teacher")

    def __str__(self):
        return f"{self.student.email} → {self.teacher.email} ({self.status})"


class StudentMentor(models.Model):
    """
    Approved mentor relationship.
    """

    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_mentor",
        limit_choices_to={"role": "student"},
    )

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentees",
    )

    assigned_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.email} mentored by {self.mentor.email}"
