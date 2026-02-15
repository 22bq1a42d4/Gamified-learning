from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Notification


# ==========================================
# LIST VIEW
# ==========================================

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    )

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications
        }
    )


# ==========================================
# MARK SINGLE AS READ
# ==========================================

@login_required
@require_POST
def mark_as_read(request, pk):
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    notification.is_read = True
    notification.save(update_fields=["is_read"])

    return redirect("notifications:list")


# ==========================================
# MARK ALL AS READ
# ==========================================

@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect("notifications:list")
