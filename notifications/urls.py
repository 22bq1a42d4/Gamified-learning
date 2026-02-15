from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="notification_list"),
    path("read/<int:pk>/", views.mark_as_read, name="read"),
    path("read-all/", views.mark_all_as_read, name="read_all"),
]
