# games/models.py

from django.db import models
from django.conf import settings
from academics.models import Subject
from django.utils import timezone


class Game(models.Model):
    DIFFICULTY_CHOICES = (
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    )

    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="games")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    xp_reward = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"


class Question(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_option = models.CharField(max_length=1)  # A / B / C / D

    def __str__(self):
        return self.question_text[:50]


class StudentAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    xp_earned = models.IntegerField()
    attempted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.email} - {self.game.title}"
