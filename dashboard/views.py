import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum


def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if request.user.role != role:
                return redirect("landing")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def tenant_dashboard(request):
    from wallet.models import Wallet
    from leases.models import Lease
    from properties.models import Property

    try:
        wallet = request.user.wallet
    except Exception:
        wallet = None

    active_lease = Lease.objects.filter(tenant=request.user, status="active").select_related("rental_property").first()
    recommended = Property.objects.filter(is_available=True).order_by("-created_at")[:3]

    savings_goal = None
    transactions = []
    if wallet:
        savings_goal = wallet.goals.filter(is_active=True).first()
        transactions = wallet.transactions.order_by("-created_at")[:5]

    return render(request, "dashboard/tenant_dashboard.html", {
        "wallet": wallet,
        "active_lease": active_lease,
        "savings_goal": savings_goal,
        "transactions": transactions,
        "recommended": recommended,
    })


@login_required
def landlord_dashboard(request):
    from payments.models import Payment
    from applications.models import Application
    from leases.models import Lease

    properties = request.user.properties.all()
    total_properties = properties.count()
    active_tenants = Lease.objects.filter(
        rental_property__landlord=request.user, status="active"
    ).count()
    pending_applications = Application.objects.filter(
        rental_property__landlord=request.user, status="pending"
    ).count()

    paid_payments = Payment.objects.filter(rental_property__landlord=request.user, status="paid")
    total_earnings = paid_payments.aggregate(total=Sum("amount"))["total"] or 0

    recent_payments = Payment.objects.filter(
        rental_property__landlord=request.user
    ).select_related("tenant", "rental_property").order_by("-date")[:5]

    upcoming_leases = Lease.objects.filter(
        rental_property__landlord=request.user, status="active"
    ).select_related("tenant", "rental_property").order_by("next_rent_due")[:5]

    monthly_earnings = [
        {"month": "Jan", "amount": 1200000},
        {"month": "Feb", "amount": 1800000},
        {"month": "Mar", "amount": 2350000},
        {"month": "Apr", "amount": 2100000},
        {"month": "May", "amount": 2600000},
        {"month": "Jun", "amount": 2350000},
    ]

    pending_apps = Application.objects.filter(
        rental_property__landlord=request.user, status="pending"
    ).select_related("tenant", "rental_property").order_by("-applied_date")[:5]

    tenants = Lease.objects.filter(
        rental_property__landlord=request.user, status="active"
    ).select_related("tenant", "rental_property").order_by("-start_date")[:10]

    return render(request, "dashboard/landlord_dashboard.html", {
        "total_properties": total_properties,
        "active_tenants": active_tenants,
        "pending_applications": pending_applications,
        "pending_apps": pending_apps,
        "tenants": tenants,
        "total_earnings": total_earnings,
        "recent_payments": recent_payments,
        "upcoming_rents": upcoming_leases,
        "monthly_earnings_json": json.dumps(monthly_earnings),
    })


@login_required
def landlord_earnings(request):
    from payments.models import Payment
    payments = Payment.objects.filter(
        rental_property__landlord=request.user, status="paid"
    ).order_by("-date")
    total_earnings = payments.aggregate(total=Sum("amount"))["total"] or 0
    paid_count = payments.count()
    return render(request, "dashboard/earnings.html", {
        "payments": payments,
        "total_earnings": total_earnings,
        "paid_count": paid_count,
    })


@login_required
def landlord_tenants(request):
    from leases.models import Lease
    leases = Lease.objects.filter(
        rental_property__landlord=request.user, status="active"
    ).select_related("tenant", "rental_property")
    return render(request, "dashboard/tenants.html", {"leases": leases})
