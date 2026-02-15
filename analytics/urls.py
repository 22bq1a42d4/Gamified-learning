from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path("student/", views.student_analytics_view, name="student"),
    path("teacher/", views.teacher_analytics_view, name="teacher"),
    path("admin/", views.admin_analytics_view, name="admin"),

    # NEW ROUTES
    path("teacher/report/", views.download_intelligence_report, name="download_report"),
    path("teacher/audit/<int:student_id>/", views.audit_student_profile, name="audit_profile"),
    path("teacher/message/<int:student_id>/", views.message_student_view, name="message_student"),
]
