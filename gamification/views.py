from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import StudentXP, SubjectXP, StudentBadge


@login_required
@role_required("student")
def student_gamification_dashboard(request):

    xp_profile, _ = StudentXP.objects.get_or_create(
        student=request.user
    )

    subject_xp = SubjectXP.objects.filter(
        student=request.user
    )

    badges = StudentBadge.objects.filter(
        student=request.user
    )

    context = {
        "xp_profile": xp_profile,
        "subject_xp": subject_xp,
        "badges": badges,
    }

    return render(
        request,
        "gamification/student_dashboard_gamification.html",
        context
    )
