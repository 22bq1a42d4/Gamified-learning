from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from accounts.decorators import role_required
from academics.models import Subject
from .models import Game, Question, StudentAttempt
from .services import award_xp

from analytics.models import StudentEngagement
from notifications.models import Notification
from gamification.models import StudentXP

# =========================================================
# GAME LIST VIEW (Fixed for Custom User Model)
# =========================================================

@login_required
@role_required("student")
def game_list(request):
    student_grade = request.user.academic_class.grade
    
    games = Game.objects.filter(
        is_active=True,
        min_grade__lte=student_grade,
        max_grade__gte=student_grade
    ).select_related("subject")

    # ADD THIS: If no games match, send a warning toast
    if not games.exists():
        messages.warning(request, f"Scouts are still preparing missions for Class {student_grade}. Check back soon!")
        # Optional: Redirect them back to dashboard so they aren't stuck on an empty page
        return redirect('accounts:student_dashboard')

    context = {
        "games": games,
        "student_grade": student_grade,
    }
    return render(request, "games/game_list.html", context)

# =========================================================
# ADMIN → CREATE GAME
# =========================================================

@login_required
@role_required("admin")
def admin_create_game(request):
    if request.method == "POST":
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        g_type = request.POST.get('game_type')
        
        Game.objects.create(
            title=title,
            subject_id=subject_id,
            game_type=g_type,
            slug=title.lower().replace(' ', '-'),
            min_grade=request.POST.get('min_grade'),
            max_grade=request.POST.get('max_grade'),
            xp_reward=request.POST.get('xp', 100)
        )
        messages.success(request, f"Mission '{title}' deployed to global grid.")
        return redirect('academics:subject_list')

    subjects = Subject.objects.all()
    return render(request, "games/admin_create_game.html", {"subjects": subjects})

# =========================================================
# GAME DETAIL VIEW
# =========================================================

@login_required
@role_required("student")
def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk, is_active=True)
    
    previous_attempt = StudentAttempt.objects.filter(
        student=request.user,
        game=game
    ).order_by("-attempted_at").first()

    context = {
        "game": game,
        "previous_attempt": previous_attempt,
    }
    return render(request, "games/game_detail.html", context)

# =========================================================
# PLAY GAME VIEW (Universal Controller)
# =========================================================

@login_required
@role_required("student")
def play_game(request, pk):
    game = get_object_or_404(Game, pk=pk, is_active=True)

    if request.method == "POST":
        score = 0
        total_questions = 1 
        
        # Logic for Quiz Type
        if game.game_type == 'quiz':
            questions = game.questions.all()
            total_questions = questions.count()
            for q in questions:
                if request.POST.get(str(q.id)) == q.correct_option:
                    score += 1
        
        # Logic for Interactive (Canvas/Sim)
        else:
            score = int(request.POST.get('score', 0))
            total_questions = int(request.POST.get('total_possible', 100))

        # Calculate XP
        performance_ratio = score / total_questions if total_questions > 0 else 0
        xp_earned = int(performance_ratio * game.xp_reward)
        xp_earned = max(0, min(xp_earned, game.xp_reward)) 

        # Save Attempt
        StudentAttempt.objects.create(
            student=request.user,
            game=game,
            score=score,
            total_questions=total_questions,
            xp_earned=xp_earned,
        )

        # Trigger Gamification Service
        result = award_xp(
            student=request.user,
            subject=game.subject,
            xp_amount=xp_earned,
            game_title=game.title 
        )

        # Track Analytics Engagement
        StudentEngagement.objects.create(
            student=request.user,
            subject=game.subject,
            minutes_spent=request.POST.get('time_spent', 5),
            date=timezone.now().date(),
        )

        # Create Notification
        msg = f"You mastered '{game.title}' and gained {xp_earned} XP!"
        if result.get('new_level'):
            msg += f" You reached Level {result['new_level']}! 🚀"

        Notification.objects.create(
            recipient=request.user,
            title="Mission Accomplished! 🏆",
            message=msg,
            notification_type="xp"
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'xp': xp_earned})

        return render(request, "games/game_result.html", {
            "game": game, "score": score, "total": total_questions, "xp_earned": xp_earned
        })

    # Template Routing
    template_map = {
        'quiz': 'games/play_quiz.html',
        'canvas': 'games/play_canvas.html',
        'drag_drop': 'games/play_interactive.html',
        'simulation': 'games/play_simulation.html',
    }
    
    template_name = template_map.get(game.game_type, 'games/play_quiz.html')
    
    context = {
        "game": game,
        "config": game.config,
    }
    
    if game.game_type == 'quiz':
        context["questions"] = game.questions.all()

    return render(request, template_name, context)

# games/views.py
@login_required
@role_required("teacher") # Or "admin"
def subject_missions_view(request, subject_id):
    """Custom Mission Control to replace the Django Admin link."""
    subject = get_object_or_404(Subject, id=subject_id)
    missions = subject.games.all() # Fetches all games/missions for this subject

    return render(request, "games/mission_control.html", {
        "subject": subject,
        "missions": missions
    })