from django.db import models
from django.conf import settings
from django.utils import timezone
from academics.models import Subject


# ==============================================
# LEVEL MODEL
# ==============================================
class Level(models.Model):
    level_number = models.PositiveIntegerField(unique=True)
    xp_required = models.PositiveIntegerField()

    class Meta:
        ordering = ["level_number"]

    def __str__(self):
        return f"Level {self.level_number}"
    

# ==============================================
# BADGE MODEL
# ==============================================
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=100, blank=True)
    xp_threshold = models.PositiveIntegerField()

    def __str__(self):
        return self.name


# ==============================================
# STUDENT XP PROFILE (GLOBAL)
# ==============================================
class StudentXP(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="xp_profile"
    )

    total_xp = models.PositiveIntegerField(default=0)
    current_level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.email} - XP Profile"

    # -------------------------
    # XP ADDITION
    # -------------------------
    def add_xp(self, amount):
        previous_level = self.current_level
        self.total_xp += amount

        new_level = self.calculate_level()

        level_up = False
        if previous_level != new_level:
            level_up = True
            self.current_level = new_level

        self.update_streak()
        self.save()

        return level_up, new_level

    # -------------------------
    # LEVEL CALCULATION
    # -------------------------
    def calculate_level(self):
        return Level.objects.filter(
            xp_required__lte=self.total_xp
        ).order_by("-level_number").first()

    # -------------------------
    # STREAK LOGIC
    # -------------------------
    def update_streak(self):
        today = timezone.now().date()

        if self.last_activity_date:
            delta = (today - self.last_activity_date).days

            if delta == 1:
                self.streak_days += 1
            elif delta > 1:
                self.streak_days = 1
        else:
            self.streak_days = 1

        self.last_activity_date = today


# ==============================================
# SUBJECT XP
# ==============================================
class SubjectXP(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="xp_records"
    )

    xp = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("student", "subject")

    def __str__(self):
        return f"{self.student.email} - {self.subject.name}"


# ==============================================
# XP LOG
# ==============================================
class XPLog(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    xp_earned = models.PositiveIntegerField()
    source = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} earned {self.xp_earned} XP"


# ==============================================
# STUDENT BADGE
# ==============================================
class StudentBadge(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "badge")

    def __str__(self):
        return f"{self.student.email} - {self.badge.name}"
