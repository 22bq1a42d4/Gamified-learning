from django.urls import path
from .views import leaderboard_view, student_gamification_dashboard, badge_gallery_view

app_name = "gamification"

urlpatterns = [
    path(
        "student/",
        student_gamification_dashboard,
        name="student_gamification_dashboard"
    ),
    path("leaderboard/", leaderboard_view, name="leaderboard"),
    path("badges/", badge_gallery_view, name="badge_gallery"),
]
