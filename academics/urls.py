# academics/urls.py
from django.urls import path
from .views import (
    subject_list_view,
    subject_create_view,
    subject_detail_view,
    student_subjects_view,
    teacher_subjects_view,
    subject_missions_view, # Add this
)

app_name = "academics"

urlpatterns = [
    # ADMIN
    path("admin/subjects/", subject_list_view, name="subject_list"),
    path("admin/subjects/create/", subject_create_view, name="subject_create"),

    # STUDENT
    path("student/subjects/", student_subjects_view, name="student_subjects"),
    path("student/subjects/<int:pk>/", subject_detail_view, name="subject_detail"),

    # TEACHER / CURRICULUM MANAGEMENT
    path("teacher/subjects/", teacher_subjects_view, name="teacher_subjects"),
    path("subjects/<int:subject_id>/missions/", subject_missions_view, name="subject_missions"),
]