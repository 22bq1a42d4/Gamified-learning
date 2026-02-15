# academics/models.py

from django.db import models
from institutes.models import Institute


# =====================================================
# ACADEMIC CLASS (Grades 6–12)
# =====================================================
class AcademicClass(models.Model):
    """
    Represents school grade levels (6 to 12)
    """

    CLASS_CHOICES = [
        (6, "Class 6"),
        (7, "Class 7"),
        (8, "Class 8"),
        (9, "Class 9"),
        (10, "Class 10"),
        (11, "Class 11"),
        (12, "Class 12"),
    ]

    grade = models.IntegerField(choices=CLASS_CHOICES, unique=True)

    def __str__(self):
        return f"Class {self.grade}"

    class Meta:
        ordering = ["grade"]


# =====================================================
# STREAM (Only for 11 & 12)
# =====================================================
class Stream(models.Model):
    """
    MPC / BIPC for higher secondary
    """

    STREAM_CHOICES = [
        ("MPC", "MPC"),
        ("BIPC", "BIPC"),
    ]

    name = models.CharField(max_length=10, choices=STREAM_CHOICES, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


# =====================================================
# SUBJECT MODEL
# =====================================================
class Subject(models.Model):
    """
    Core subject mapping system
    """

    name = models.CharField(max_length=120)

    academic_class = models.ForeignKey(
        AcademicClass,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    # Only required for class 11 & 12
    stream = models.ForeignKey(
        Stream,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subjects"
    )

    institute = models.ForeignKey(
        Institute,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.stream:
            return f"{self.name} - Class {self.academic_class.grade} ({self.stream.name})"
        return f"{self.name} - Class {self.academic_class.grade}"

    class Meta:
        ordering = ["academic_class__grade", "name"]
        unique_together = ("name", "academic_class", "stream", "institute")
