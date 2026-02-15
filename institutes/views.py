from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Institute
from django.contrib.auth import get_user_model

User = get_user_model()


# ------------------------------------
# ADMIN → Institute List View
# ------------------------------------
@login_required
@role_required("admin")
def institute_list_view(request):
    institutes = Institute.objects.all()

    context = {
        "institutes": institutes,
        "total_institutes": institutes.count(),
        "active_count": institutes.filter(is_active=True).count(),
        "inactive_count": institutes.filter(is_active=False).count(),
    }

    return render(request, "institutes/institute_list.html", context)


# ------------------------------------
# ADMIN → Create Institute
# ------------------------------------
@login_required
@role_required("admin")
def institute_create_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        city = request.POST.get("city")
        state = request.POST.get("state")
        address = request.POST.get("address")

        if Institute.objects.filter(code=code).exists():
            messages.error(request, "Institute code already exists.")
            return redirect("institutes:institute_create")

        Institute.objects.create(
            name=name,
            code=code,
            city=city,
            state=state,
            address=address,
        )

        messages.success(request, "Institute created successfully.")
        return redirect("institutes:institute_list")

    return render(request, "institutes/institute_create.html")


# ------------------------------------
# ADMIN → Toggle Active / Inactive
# ------------------------------------
@login_required
@role_required("admin")
def institute_toggle_status(request, pk):
    institute = get_object_or_404(Institute, pk=pk)

    institute.is_active = not institute.is_active
    institute.save()

    messages.success(request, "Institute status updated.")
    return redirect("institutes:institute_list")


# ------------------------------------
# ADMIN → Institute Detail
# ------------------------------------
@login_required
@role_required("admin")
def institute_detail_view(request, pk):
    institute = get_object_or_404(Institute, pk=pk)

    students = User.objects.filter(institute=institute, role="student")
    teachers = User.objects.filter(institute=institute, role="teacher")

    context = {
        "institute": institute,
        "students": students,
        "teachers": teachers,
        "student_count": students.count(),
        "teacher_count": teachers.count(),
    }

    return render(request, "institutes/institute_detail.html", context)
