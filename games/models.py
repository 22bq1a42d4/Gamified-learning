from django.db import models
from django.conf import settings
from academics.models import Subject
from django.utils import timezone

class Game(models.Model):
    GAME_TYPES = (
        ("quiz", "Animated Quiz"),
        ("canvas", "Canvas Action Game"),
        ("drag_drop", "Interactive Sorting"),
        ("simulation", "Scientific Simulation"),
    )
    
    DIFFICULTY_CHOICES = (
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="Used for the URL (e.g., equation-archer)")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="games")
    game_type = models.CharField(max_length=20, choices=GAME_TYPES, default="quiz")
    
    # Grade logic
    min_grade = models.PositiveIntegerField(default=6)
    max_grade = models.PositiveIntegerField(default=12)
    
    # Visuals & Gamification
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="game_thumbs/", blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    xp_reward = models.PositiveIntegerField(default=50)
    
    # Advanced: Dynamic Config (Requires passing as JSON to frontend)
    # Allows Admin to change game speed, gravity, or time limits per game
    config = models.JSONField(default=dict, blank=True, help_text="Game-specific settings in JSON format")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - Grade {self.min_grade}-{self.max_grade}"

class Question(models.Model):
    """Used specifically when game_type is 'quiz'"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    image = models.ImageField(upload_to="question_imgs/", blank=True, null=True) # For Bio/Physics diagrams
    
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    
    correct_option = models.CharField(max_length=1, choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')])

    def __str__(self):
        return f"Q for {self.game.title}: {self.question_text[:30]}"

class StudentAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField(default=1) # 1 for non-quiz games
    xp_earned = models.IntegerField()
    time_spent = models.DurationField(null=True, blank=True) # For analytics tracking
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} played {self.game.title}"