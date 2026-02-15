from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from accounts.decorators import role_required
from .models import Game, Question, StudentAttempt
from .services import award_xp

from analytics.models import StudentEngagement
from notifications.models import Notification
from gamification.models import StudentXP


# =========================================================
# GAME LIST VIEW
# =========================================================

@login_required
@role_required("student")
def game_list(request):
    """
    Displays all active games available to the student
    """

    games = Game.objects.filter(is_active=True).select_related("subject")

    context = {
        "games": games,
    }

    return render(request, "games/game_list.html", context)


# =========================================================
# GAME DETAIL VIEW
# =========================================================

@login_required
@role_required("student")
def game_detail(request, pk):
    """
    Shows game description before starting
    """

    game = get_object_or_404(Game, pk=pk, is_active=True)

    # Check if student already attempted
    previous_attempt = StudentAttempt.objects.filter(
        student=request.user,
        game=game
    ).order_by("-created_at").first()

    context = {
        "game": game,
        "previous_attempt": previous_attempt,
    }

    return render(request, "games/game_detail.html", context)


# =========================================================
# PLAY GAME VIEW
# =========================================================

@login_required
@role_required("student")
def play_game(request, pk):
    """
    Handles quiz logic and XP awarding
    """

    game = get_object_or_404(Game, pk=pk, is_active=True)
    questions = game.questions.all()

    if questions.count() == 0:
        messages.error(request, "This game has no questions configured.")
        return redirect("games:game_detail", pk=game.pk)

    # -----------------------------------------------------
    # GAME SUBMISSION
    # -----------------------------------------------------
    if request.method == "POST":

        score = 0
        total_questions = questions.count()

        for question in questions:
            selected_option = request.POST.get(str(question.id))

            if selected_option and selected_option == question.correct_option:
                score += 1

        # Secure XP Calculation
        xp_earned = int((score / total_questions) * game.xp_reward)

        # Prevent negative or invalid XP
        xp_earned = max(0, xp_earned)

        # -------------------------------------------------
        # SAVE ATTEMPT
        # -------------------------------------------------
        StudentAttempt.objects.create(
            student=request.user,
            game=game,
            score=score,
            total_questions=total_questions,
            xp_earned=xp_earned,
        )

        # -------------------------------------------------
        # AWARD XP
        # -------------------------------------------------
        award_xp(
            student=request.user,
            subject=game.subject,
            xp_amount=xp_earned,
            source=f"Game: {game.title}",
        )

        # -------------------------------------------------
        # TRACK ENGAGEMENT
        # -------------------------------------------------
        StudentEngagement.objects.create(
            student=request.user,
            subject=game.subject,
            minutes_spent=5,  # Replace with dynamic timer if implemented
            date=timezone.now().date(),
        )

        # -------------------------------------------------
        # CREATE NOTIFICATION
        # -------------------------------------------------
        Notification.objects.create(
            recipient=request.user,
            title="Game Completed",
            message=f"You earned {xp_earned} XP from '{game.title}'.",
            notification_type="xp"
        )

        # -------------------------------------------------
        # FETCH UPDATED XP DATA
        # -------------------------------------------------
        student_xp = StudentXP.objects.filter(
            student=request.user
        ).first()

        context = {
            "game": game,
            "score": score,
            "total": total_questions,
            "xp_earned": xp_earned,
            "student_xp": student_xp,
        }

        return render(request, "games/game_result.html", context)

    # -----------------------------------------------------
    # INITIAL GAME LOAD
    # -----------------------------------------------------
    context = {
        "game": game,
        "questions": questions,
    }

    return render(request, "games/play_game.html", context)
