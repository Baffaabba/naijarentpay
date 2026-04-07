from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()[:50]
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications/list.html", {"notifications": notifications})


@login_required
def unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({"count": count})


@login_required
@require_POST
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({"count": count})


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    if request.htmx:
        notifications = request.user.notifications.all()[:10]
        return render(request, "partials/notification_dropdown.html", {
            "notifications": notifications,
            "unread_count": 0,
        })
    return JsonResponse({"status": "ok"})


@login_required
def notification_dropdown(request):
    """HTMX partial: last 8 notifications for bell dropdown."""
    notifications = request.user.notifications.all()[:8]
    unread = request.user.notifications.filter(is_read=False).count()
    return render(request, "partials/notification_dropdown.html", {
        "notifications": notifications,
        "unread_count": unread,
    })
