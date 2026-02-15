from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from django.utils import timezone
from django.db.models import Count

from academics.models import Subject
from analytics.models import StudentEngagement
from .models import ChatSession, ChatMessage
from .services import generate_subject_response


# ==========================================
# RATE LIMIT CONFIG
# ==========================================

MAX_MESSAGES_PER_MINUTE = 15


# ==========================================
# CHAT PAGE
# ==========================================

@login_required
@role_required("student")
def chat_page(request):

    subjects = Subject.objects.filter(
        institute=request.user.institute,
        is_active=True
    )

    subject_id = request.GET.get("subject")

    active_session = None
    messages = []

    if subject_id:
        subject = get_object_or_404(
            Subject,
            id=subject_id,
            institute=request.user.institute
        )

        active_session, _ = ChatSession.objects.get_or_create(
            student=request.user,
            subject=subject,
            is_active=True
        )

        messages = active_session.messages.all()

    return render(
        request,
        "chatbot/chat_page.html",
        {
            "subjects": subjects,
            "active_session": active_session,
            "messages": messages,
        }
    )


# ==========================================
# CHAT API (AJAX)
# ==========================================

@login_required
@role_required("student")
@require_POST
def chat_api(request):

    subject_id = request.POST.get("subject_id")
    message = request.POST.get("message", "").strip()

    if not subject_id or not message:
        return JsonResponse({"error": "Invalid request"}, status=400)

    # -------------------------------
    # RATE LIMIT CHECK
    # -------------------------------
    one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)

    recent_messages_count = ChatMessage.objects.filter(
        session__student=request.user,
        timestamp__gte=one_minute_ago,
        role="user"
    ).count()

    if recent_messages_count >= MAX_MESSAGES_PER_MINUTE:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please slow down."},
            status=429
        )

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        institute=request.user.institute
    )

    session, _ = ChatSession.objects.get_or_create(
        student=request.user,
        subject=subject,
        is_active=True
    )

    # Save user message
    ChatMessage.objects.create(
        session=session,
        role="user",
        content=message
    )

    # Generate bot response
    bot_response = generate_subject_response(subject.name, message)

    ChatMessage.objects.create(
        session=session,
        role="bot",
        content=bot_response
    )

    # Engagement tracking (FIXED)
    StudentEngagement.objects.create(
        student=request.user,
        subject=subject,
        minutes_spent=1
    )

    return JsonResponse({
        "bot_response": bot_response
    })


# ==========================================
# CLEAR CHAT
# ==========================================

@login_required
@role_required("student")
def clear_chat(request, subject_id):

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        institute=request.user.institute
    )

    ChatSession.objects.filter(
        student=request.user,
        subject=subject
    ).delete()

    return redirect("chatbot:chat_page")
