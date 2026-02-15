from django.db import models
from django.conf import settings


class Institute(models.Model):
    """
    Core academic entity.
    Every Student and Teacher must belong to one Institute.
    Admin can manage Institutes.
    """

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    # --------------------------
    # Dynamic Counters
    # --------------------------
    def total_students(self):
        return settings.AUTH_USER_MODEL.objects.filter(
            institute=self,
            role="student"
        ).count()

    def total_teachers(self):
        return settings.AUTH_USER_MODEL.objects.filter(
            institute=self,
            role="teacher"
        ).count()
