# academics/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import AcademicClass, Stream, Subject
from institutes.models import Institute
from gamification.models import SubjectXP, Level


# =====================================================
# ADMIN → SUBJECT LIST
# =====================================================
@login_required
@role_required("admin")
def subject_list_view(request):

    subjects = Subject.objects.select_related(
        "academic_class",
        "stream",
        "institute"
    )

    return render(request, "academics/subject_list.html", {
        "subjects": subjects
    })


# =====================================================
# ADMIN → CREATE SUBJECT
# =====================================================
@login_required
@role_required("admin")
def subject_create_view(request):

    classes = AcademicClass.objects.all()
    streams = Stream.objects.all()
    institutes = Institute.objects.all()

    if request.method == "POST":

        name = request.POST.get("name")
        class_id = request.POST.get("academic_class")
        stream_id = request.POST.get("stream")
        institute_id = request.POST.get("institute")

        academic_class = get_object_or_404(AcademicClass, id=class_id)
        stream = Stream.objects.filter(id=stream_id).first()
        institute = get_object_or_404(Institute, id=institute_id)

        # Stream validation for 11 & 12
        if academic_class.grade in [11, 12] and not stream:
            messages.error(request, "Stream required for Class 11 and 12.")
            return redirect("academics:subject_create")

        Subject.objects.create(
            name=name,
            academic_class=academic_class,
            stream=stream,
            institute=institute,
        )

        messages.success(request, "Subject created successfully.")
        return redirect("academics:subject_list")

    return render(request, "academics/subject_create.html", {
        "classes": classes,
        "streams": streams,
        "institutes": institutes
    })


# =====================================================
# STUDENT → SUBJECT LIST
# =====================================================
@login_required
@role_required("student")
def student_subjects_view(request):

    user = request.user

    subjects = Subject.objects.filter(
        academic_class=user.academic_class,
        institute=user.institute,
        is_active=True
    )

    # Stream filtering only for 11 & 12
    if user.stream:
        subjects = subjects.filter(stream=user.stream)

    return render(request, "academics/student_subjects.html", {
        "subjects": subjects
    })


# =====================================================
# STUDENT → SUBJECT DETAIL PAGE
# =====================================================
@login_required
@role_required("student")
def subject_detail_view(request, pk):

    # --------------------------------------
    # GET SUBJECT (Institute-secured)
    # --------------------------------------
    subject = get_object_or_404(
        Subject,
        pk=pk,
        institute=request.user.institute,
        is_active=True
    )

    # --------------------------------------
    # GET ACTIVE GAMES
    # --------------------------------------
    games = subject.games.filter(is_active=True)

    # --------------------------------------
    # GET SUBJECT XP RECORD
    # --------------------------------------
    subject_xp_obj, created = SubjectXP.objects.get_or_create(
        student=request.user,
        subject=subject,
        defaults={"xp": 0}
    )

    subject_xp = subject_xp_obj.xp

    # --------------------------------------
    # LEVEL CALCULATION
    # --------------------------------------
    levels = Level.objects.order_by("xp_required")

    current_level = None
    next_level = None

    for level in levels:
        if subject_xp >= level.xp_required:
            current_level = level
        elif subject_xp < level.xp_required:
            next_level = level
            break

    # If student exceeded highest level
    if not next_level:
        next_level = current_level

    subject_level = current_level.level_number if current_level else 1

    # --------------------------------------
    # XP PROGRESS PERCENTAGE
    # --------------------------------------
    if current_level and next_level and current_level != next_level:
        xp_in_current_level = subject_xp - current_level.xp_required
        xp_range = next_level.xp_required - current_level.xp_required
        xp_percentage = int((xp_in_current_level / xp_range) * 100)
    else:
        xp_percentage = 100

    # Safety cap
    if xp_percentage > 100:
        xp_percentage = 100
    if xp_percentage < 0:
        xp_percentage = 0

    # --------------------------------------
    # RENDER
    # --------------------------------------
    return render(request, "academics/subject_detail.html", {
        "subject": subject,
        "games": games,
        "subject_xp": subject_xp,
        "subject_level": subject_level,
        "next_level": next_level.level_number if next_level else subject_level,
        "xp_percentage": xp_percentage,
    })

# =====================================================
# TEACHER → SUBJECT LIST
# =====================================================
@login_required
@role_required("teacher")
def teacher_subjects_view(request):

    subjects = Subject.objects.filter(
        institute=request.user.institute,
        is_active=True
    )

    return render(request, "academics/teacher_subjects.html", {
        "subjects": subjects
    })
