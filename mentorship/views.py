# mentorship/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from django.contrib.auth import get_user_model

from .models import MentorRequest, StudentMentor
from notifications.models import Notification

User = get_user_model()


# -----------------------------
# STUDENT: Search Teachers
# -----------------------------
@login_required
@role_required("student")
def mentor_search(request):
    teachers = User.objects.filter(role="teacher")

    return render(request, "mentorship/mentor_search.html", {
        "teachers": teachers
    })


# -----------------------------
# STUDENT: Send Request
# -----------------------------
@login_required
@role_required("student")
def send_mentor_request(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")

    MentorRequest.objects.get_or_create(
        student=request.user,
        teacher=teacher
    )

    Notification.objects.create(
        recipient=teacher,
        message=f"{request.user.email} requested you as a mentor."
    )

    messages.success(request, "Mentor request sent.")
    return redirect("mentorship:mentor_search")


# -----------------------------
# TEACHER: View Requests
# -----------------------------
@login_required
@role_required("teacher")
def mentor_requests_list(request):
    requests = MentorRequest.objects.filter(teacher=request.user, status="pending")

    return render(request, "mentorship/mentor_requests.html", {
        "requests": requests
    })


# -----------------------------
# TEACHER: Approve Request
# -----------------------------
@login_required
@role_required("teacher")
def approve_request(request, request_id):
    mentor_request = get_object_or_404(MentorRequest, id=request_id)

    mentor_request.status = "approved"
    mentor_request.save()

    StudentMentor.objects.update_or_create(
        student=mentor_request.student,
        defaults={"mentor": request.user}
    )

    Notification.objects.create(
        recipient=mentor_request.student,
        message=f"{request.user.email} approved your mentor request."
    )

    messages.success(request, "Mentor request approved.")
    return redirect("mentorship:mentor_requests")


# -----------------------------
# TEACHER: Reject Request
# -----------------------------
@login_required
@role_required("teacher")
def reject_request(request, request_id):
    mentor_request = get_object_or_404(MentorRequest, id=request_id)

    mentor_request.status = "rejected"
    mentor_request.save()

    Notification.objects.create(
        recipient=mentor_request.student,
        message=f"{request.user.email} rejected your mentor request."
    )

    messages.info(request, "Mentor request rejected.")
    return redirect("mentorship:mentor_requests")
