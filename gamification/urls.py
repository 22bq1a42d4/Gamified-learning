from django.urls import path
from .views import student_gamification_dashboard

app_name = "gamification"

urlpatterns = [
    path(
        "student/",
        student_gamification_dashboard,
        name="student_gamification_dashboard"
    ),
]
