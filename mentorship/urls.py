# mentorship/urls.py

from django.urls import path
from . import views

app_name = "mentorship"

urlpatterns = [

    # Student
    path("search/", views.mentor_search, name="mentor_search"),
    path("request/<int:teacher_id>/", views.send_mentor_request, name="send_request"),

    # Teacher
    path("requests/", views.mentor_requests_list, name="mentor_requests"),
    path("approve/<int:request_id>/", views.approve_request, name="approve_request"),
    path("reject/<int:request_id>/", views.reject_request, name="reject_request"),
]
