from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import role_required
from .models import AcademicClass, Stream, Subject
from gamification.models import SubjectXP, Level

# =====================================================
# ADMIN → SUBJECT LIST (FIXED: Full Visibility)
# =====================================================
@login_required
@role_required("admin")
def subject_list_view(request):
    """
    Finalized Registry View: Fetches ALL subjects.
    Sorting changed to newest first to verify your 'Social' module immediately.
    """
    subjects = Subject.objects.select_related(
        "academic_class",
        "stream",
        "institute"
    ).order_by('-id') # This puts Ref ID #EDU25 (Social) at the top

    return render(request, "academics/subject_list.html", {
        "subjects": subjects
    })

# =====================================================
# ADMIN → CREATE SUBJECT (FIXED: IntegrityError Shield)
# =====================================================
@login_required
@role_required("admin")
def subject_create_view(request):
    """
    Controller: Safeguards against NULL institutes and validates 11-12 streams.
    """
    classes = AcademicClass.objects.all().order_by('grade')
    streams = Stream.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        class_id = request.POST.get("academic_class")
        stream_id = request.POST.get("stream")
        
        # FIX: Ensure admin has an institute before saving
        institute = request.user.institute 
        if not institute:
            messages.error(request, "🛡️ Profile Error: Your Admin account must be linked to an Institute in Django Admin.")
            return redirect("academics:subject_list")

        academic_class = get_object_or_404(AcademicClass, id=class_id)
        stream = Stream.objects.filter(id=stream_id).first()

        # Validation for Classes 11 and 12
        if academic_class.grade in [11, 12] and not stream:
            messages.error(request, "Error: A Stream (MPC/BIPC) is required for Class 11 and 12.")
            return render(request, "academics/subject_create.html", {"classes": classes, "streams": streams})

        if academic_class.grade < 11:
            stream = None

        try:
            Subject.objects.create(
                name=name,
                academic_class=academic_class,
                stream=stream,
                institute=institute,
            )
            messages.success(request, f"Operational: '{name}' mapped to Class {academic_class.grade}.")
            return redirect("academics:subject_list")
        except Exception as e:
            messages.error(request, f"Database Error: {str(e)}")
            return redirect("academics:subject_create")

    return render(request, "academics/subject_create.html", {"classes": classes, "streams": streams})

# =====================================================
# STUDENT → SUBJECT LIST (FIXED: Sync Visibility)
# =====================================================
@login_required
@role_required("student")
def student_subjects_view(request):
    """
    Dynamic Student View: Shows subjects matching the student's Grade
    and their Institute (including Global Base modules).
    """
    user = request.user
    
    # FIX: Show subjects belonging to student's institute OR global subjects (null institute)
    subjects = Subject.objects.filter(
        academic_class=user.academic_class,
        is_active=True
    ).filter(
        Q(institute=user.institute) | Q(institute__isnull=True)
    )

    if user.stream:
        subjects = subjects.filter(stream=user.stream)

    return render(request, "academics/student_subjects.html", {"subjects": subjects})

# =====================================================
# STUDENT → SUBJECT DETAIL (FIXED: Permission Logic)
# =====================================================
@login_required
@role_required("student")
def subject_detail_view(request, pk):
    """
    Secure Detail View: Calculates levels and XP progress for the student.
    """
    # FIX: Allow access if subject is global or student's institute
    subject = get_object_or_404(
        Subject,
        Q(pk=pk, is_active=True),
        Q(institute=request.user.institute) | Q(institute__isnull=True)
    )

    games = subject.games.filter(is_active=True)
    subject_xp_obj, _ = SubjectXP.objects.get_or_create(
        student=request.user, subject=subject, defaults={"xp": 0}
    )

    subject_xp = subject_xp_obj.xp
    levels = Level.objects.order_by("xp_required")

    current_level = levels.filter(xp_required__lte=subject_xp).last() or levels.first()
    next_level = levels.filter(xp_required__gt=subject_xp).first() or current_level

    # XP Progress Logic
    xp_range = next_level.xp_required - current_level.xp_required
    if xp_range > 0:
        xp_percentage = min(int(((subject_xp - current_level.xp_required) / xp_range) * 100), 100)
    else:
        xp_percentage = 100

    return render(request, "academics/subject_detail.html", {
        "subject": subject,
        "games": games,
        "subject_xp": subject_xp,
        "subject_level": current_level.level_number,
        "next_level": next_level.level_number,
        "xp_percentage": max(xp_percentage, 0),
    })

# =====================================================
# TEACHER → SUBJECT LIST
# =====================================================
@login_required
@role_required("teacher")
def teacher_subjects_view(request):
    """
    Teacher Curriculum Portal: Dynamic listing of STEM modules 
    authorized for the teacher's specific institute.
    """
    # Filter subjects by the teacher's institute and ensure they are active
    subjects = Subject.objects.filter(
        institute=request.user.institute,
        is_active=True
    ).select_related('academic_class', 'stream').order_by('academic_class__grade')

    return render(request, "academics/teacher_subjects.html", {
        "subjects": subjects
    })

# academics/views.py

# academics/views.py

@login_required
@role_required("teacher") # Or "admin"
def subject_missions_view(request, subject_id):
    """
    Mission Control: Displays quick-access cards for all STEM games 
    linked to a specific subject.
    """
    subject = get_object_or_404(Subject, id=subject_id)
    # Fetch all games associated with this subject
    missions = subject.games.all() 

    return render(request, "academics/mission_control.html", {
        "subject": subject,
        "missions": missions
    })

@login_required
@role_required("teacher")
def teacher_subjects_view(request):
    """Teacher view limited to their sector."""
    subjects = Subject.objects.filter(
        institute=request.user.institute,
        is_active=True
    ).select_related('academic_class', 'stream').order_by('academic_class__grade')

    return render(request, "academics/teacher_subjects.html", {"subjects": subjects})

