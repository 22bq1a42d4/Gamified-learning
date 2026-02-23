import PyPDF2  # Add to top
from django.core.files.storage import FileSystemStorage
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


# ============================reading mode=================
@login_required
@role_required("student")
def reading_mode(request):
    """Render the Scholar Reading Mode page"""
    return render(request, "chatbot/reading_mode.html")

@login_required
@role_required("student")
@require_POST
def upload_scholar_doc(request):
    """API to handle document upload and text extraction"""
    if 'document' not in request.FILES:
        return JsonResponse({"status": "error", "message": "No document uploaded"}, status=400)
    
    doc = request.FILES['document']
    ext = doc.name.split('.')[-1].lower()
    
    # 1. Validation
    if ext not in ['pdf', 'txt']:
        return JsonResponse({
            "status": "error", 
            "message": "Only PDF and TXT files are eligible for AI Reading Mode."
        }, status=400)

    extracted_text = ""
    
    try:
        # 2. Extraction Logic
        if ext == 'pdf':
            pdf_reader = PyPDF2.PdfReader(doc)
            # Limit to first 20 pages to avoid Gemini token limits/latency
            for page_num in range(min(len(pdf_reader.pages), 20)):
                extracted_text += pdf_reader.pages[page_num].extract_text()
        else:
            extracted_text = doc.read().decode('utf-8')

        if not extracted_text.strip():
            return JsonResponse({"status": "error", "message": "Document appears to be empty or an image-based PDF."}, status=400)

        # 3. Store in session (Temporary memory for the bot)
        request.session['scholar_context'] = extracted_text[:10000] # Safe limit
        request.session['scholar_doc_name'] = doc.name

        return JsonResponse({
            "status": "success", 
            "message": f"Successfully synced {doc.name}! Your AI Mentor is ready.",
            "doc_name": doc.name
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Processing failed: {str(e)}"}, status=500)

@login_required
@require_POST
def scholar_chat_api(request):
    """Dedicated API for the Scholar Bot using the uploaded context"""
    user_message = request.POST.get("message", "").strip()
    context = request.session.get('scholar_context', '')
    doc_name = request.session.get('scholar_doc_name', 'the document')

    if not context:
        return JsonResponse({"error": "Please upload a document first."}, status=400)

    # Prompt Engineering for Gemini
    scholar_prompt = f"""
    You are an expert academic tutor. You are helping a student understand a document titled '{doc_name}'.
    Use the following extracted text as your primary knowledge source:
    ---
    {context}
    ---
    Student's Question: {user_message}
    
    Instructions:
    1. If the answer is in the document, explain it clearly.
    2. If the user asks for a summary, provide a bulleted summary.
    3. If the answer isn't in the document, say so but try to help using general knowledge.
    """

    # Reuse your existing service
    from .services import generate_subject_response
    bot_response = generate_subject_response("Academic Scholar", scholar_prompt)

    return JsonResponse({"bot_response": bot_response})