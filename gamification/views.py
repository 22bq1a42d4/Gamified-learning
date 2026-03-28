from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import StudentXP, SubjectXP, StudentBadge
from .models import StudentXP, Badge, StudentBadge, Level
from django.db.models import F

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



@login_required
def leaderboard_view(request):
    # Only show top 10 from the same institute
    institute = request.user.student_profile.institute
    leaderboard = StudentXP.objects.filter(
        student__student_profile__institute=institute
    ).order_by('-total_xp')[:10]
    
    return render(request, "gamification/leaderboard.html", {"leaderboard": leaderboard})

@login_required
def badge_gallery_view(request):
    all_badges = Badge.objects.all().order_by('xp_threshold')
    unlocked_badges = [sb.badge for sb in StudentBadge.objects.filter(student=request.user)]
    
    return render(request, "gamification/badge_gallery.html", {
        "all_badges": all_badges,
        "unlocked_badges": unlocked_badges
    })
