import PyPDF2
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from django.utils import timezone
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
    """
    Renders the AI Mentor interface with subjects filtered by the student's grade.
    """
    subjects = Subject.objects.filter(
        academic_class=request.user.academic_class,
        is_active=True
    ).order_by('name')

    subject_id = request.GET.get("subject")
    active_session = None
    messages_list = []

    if subject_id:
        subject = get_object_or_404(Subject, id=subject_id)

        active_session, _ = ChatSession.objects.get_or_create(
            student=request.user,
            subject=subject,
            is_active=True
        )

        messages_list = active_session.messages.all().order_by('timestamp')

    return render(request, "chatbot/chat_page.html", {
        "subjects": subjects,
        "active_session": active_session,
        "messages": messages_list,
    })


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

    # FIXED: removed institute filter
    subject = get_object_or_404(Subject, id=subject_id)

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

    # Engagement tracking
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

    subject = get_object_or_404(Subject, id=subject_id)

    ChatSession.objects.filter(
        student=request.user,
        subject=subject
    ).delete()

    return redirect("chatbot:chat_page")


# ==========================================
# READING MODE
# ==========================================

@login_required
@role_required("student")
def reading_mode(request):
    return render(request, "chatbot/reading_mode.html")


@login_required
@role_required("student")
@require_POST
def upload_scholar_doc(request):

    if 'document' not in request.FILES:
        return JsonResponse(
            {"status": "error", "message": "No document uploaded"},
            status=400
        )

    doc = request.FILES['document']
    ext = doc.name.split('.')[-1].lower()

    if ext not in ['pdf', 'txt']:
        return JsonResponse(
            {
                "status": "error",
                "message": "Only PDF and TXT files are eligible for AI Reading Mode."
            },
            status=400
        )

    extracted_text = ""

    try:

        if ext == 'pdf':
            pdf_reader = PyPDF2.PdfReader(doc)

            for page_num in range(min(len(pdf_reader.pages), 20)):
                extracted_text += pdf_reader.pages[page_num].extract_text()

        else:
            extracted_text = doc.read().decode('utf-8')

        if not extracted_text.strip():
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Document appears to be empty or image-based."
                },
                status=400
            )

        request.session['scholar_context'] = extracted_text[:10000]
        request.session['scholar_doc_name'] = doc.name

        return JsonResponse({
            "status": "success",
            "message": f"Successfully synced {doc.name}! Your AI Mentor is ready.",
            "doc_name": doc.name
        })

    except Exception as e:

        return JsonResponse(
            {"status": "error", "message": f"Processing failed: {str(e)}"},
            status=500
        )


@login_required
@require_POST
def scholar_chat_api(request):

    user_message = request.POST.get("message", "").strip()

    context = request.session.get('scholar_context', '')
    doc_name = request.session.get('scholar_doc_name', 'the document')

    if not context:
        return JsonResponse(
            {"error": "Please upload a document first."},
            status=400
        )

    scholar_prompt = f"""
You are an expert academic tutor helping a student understand a document called "{doc_name}".

DOCUMENT CONTENT
----------------
{context}

Student Question:
{user_message}

Instructions:
1. Use the document as the main source.
2. If asked for summary, provide bullet points.
3. If answer is not inside document, say it clearly then explain using general knowledge.
"""

    bot_response = generate_subject_response("Academic Scholar", scholar_prompt)

    return JsonResponse({
        "bot_response": bot_response
    })