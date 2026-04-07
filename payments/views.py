from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Payment


@login_required
def payment_history(request):
    payments = Payment.objects.filter(
        tenant=request.user
    ).select_related("rental_property").order_by("-date")
    return render(request, "payments/history.html", {"payments": payments})
