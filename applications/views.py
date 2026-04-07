from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Application


@login_required
def applications_list(request):
    status_filter = request.GET.get("status", "")
    apps = Application.objects.filter(
        rental_property__landlord=request.user
    ).select_related("tenant", "rental_property").order_by("-applied_date")
    if status_filter:
        apps = apps.filter(status=status_filter)
    pending_count = Application.objects.filter(
        rental_property__landlord=request.user, status="pending"
    ).count()
    return render(request, "applications/applications.html", {
        "applications": apps,
        "pending_count": pending_count,
    })


@login_required
def approve_application(request, pk):
    app = get_object_or_404(Application, pk=pk, rental_property__landlord=request.user)
    if request.method == "POST":
        app.status = "approved"
        app.save()
        if request.htmx:
            return render(request, "partials/application_card.html", {"app": app})
        return redirect("applications_list")
    return redirect("applications_list")


@login_required
def reject_application(request, pk):
    app = get_object_or_404(Application, pk=pk, rental_property__landlord=request.user)
    if request.method == "POST":
        app.status = "rejected"
        app.save()
        if request.htmx:
            return render(request, "partials/application_card.html", {"app": app})
        return redirect("applications_list")
    return redirect("applications_list")


@login_required
def my_applications(request):
    apps = Application.objects.filter(
        tenant=request.user
    ).select_related("rental_property", "rental_property__landlord").order_by("-applied_date")
    return render(request, "applications/my_applications.html", {"applications": apps})
