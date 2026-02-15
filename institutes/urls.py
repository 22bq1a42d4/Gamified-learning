from django.urls import path
from .views import (
    institute_list_view,
    institute_create_view,
    institute_toggle_status,
    institute_detail_view,
)

app_name = "institutes"

urlpatterns = [
    path("", institute_list_view, name="institute_list"),
    path("create/", institute_create_view, name="institute_create"),
    path("<int:pk>/", institute_detail_view, name="institute_detail"),
    path("<int:pk>/toggle/", institute_toggle_status, name="institute_toggle"),
]
