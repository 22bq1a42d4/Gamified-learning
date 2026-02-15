# games/urls.py

from django.urls import path
from . import views

app_name = "games"

urlpatterns = [
    path("", views.game_list, name="game_list"),
    path("<int:pk>/", views.game_detail, name="game_detail"),
    path("<int:pk>/play/", views.play_game, name="play_game"),
]
