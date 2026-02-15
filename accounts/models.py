from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from institutes.models import Institute
from academics.models import AcademicClass, Stream



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", User.ADMIN)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    # Remove username
    username = None

    # Role Constants
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    GUARDIAN = "guardian"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (TEACHER, "Teacher"),
        (STUDENT, "Student"),
        (GUARDIAN, "Guardian"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # ==============================
    # ADD MENTOR FIELD HERE
    # ==============================
    mentor = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_students",
        limit_choices_to={"role": TEACHER}
    )

    # Student-specific
    class_studying = models.IntegerField(null=True, blank=True)

    # Common fields
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    login_count = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    institute = models.ForeignKey(
        Institute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    academic_class = models.ForeignKey(
        AcademicClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    stream = models.ForeignKey(
        Stream,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    guardian = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        limit_choices_to={"role": "guardian"}
    )


    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"


class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
