from django.db import models
from django.conf import settings
from academics.models import Subject


class StudentEngagement(models.Model):
    """
    Tracks daily engagement time of student per subject
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="engagement_records"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    minutes_spent = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Student Engagement"
        verbose_name_plural = "Student Engagement Records"

    def __str__(self):
        return f"{self.student.email} - {self.minutes_spent} mins on {self.date}"


class PerformanceSnapshot(models.Model):
    """
    Cached performance data for fast analytics rendering
    """

    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="performance_snapshot"
    )

    total_xp = models.PositiveIntegerField(default=0)
    total_games_played = models.PositiveIntegerField(default=0)
    total_minutes_spent = models.PositiveIntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Performance Snapshot"
        verbose_name_plural = "Performance Snapshots"

    def __str__(self):
        return f"{self.student.email} - Snapshot"
