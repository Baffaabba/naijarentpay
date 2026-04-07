from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Lease


@login_required
def my_lease(request):
    lease = Lease.objects.filter(
        tenant=request.user, status="active"
    ).select_related("rental_property", "rental_property__landlord").first()
    return render(request, "leases/my_lease.html", {"lease": lease})
