from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from .models import Property
from .forms import AddPropertyForm, ReviewForm
from applications.models import Application


def _filter_properties(request):
    """Common filter logic for both public and logged-in home search."""
    q = request.GET.get("q", "").strip()
    prop_type = request.GET.get("type", "").strip()
    city = request.GET.get("city", "").strip()
    state = request.GET.get("state", "").strip()
    bedrooms = request.GET.get("bedrooms", "").strip()
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")

    properties = Property.objects.filter(is_available=True)
    if q:
        from django.db.models import Q
        properties = properties.filter(
            Q(location__icontains=q) | Q(title__icontains=q) | Q(city__icontains=q)
        )
    if prop_type:
        properties = properties.filter(property_type=prop_type)
    if city:
        properties = properties.filter(city__icontains=city)
    if state:
        properties = properties.filter(state__icontains=state)
    if bedrooms:
        try:
            properties = properties.filter(bedrooms=int(bedrooms))
        except ValueError:
            pass
    if min_price:
        try:
            properties = properties.filter(price_per_year__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            properties = properties.filter(price_per_year__lte=float(max_price))
        except ValueError:
            pass
    return properties.distinct().order_by("-created_at"), {
        "q": q, "selected_type": prop_type, "city": city, "state": state,
        "bedrooms": bedrooms, "min_price": min_price, "max_price": max_price,
    }


def _properties_map_json(properties):
    pins = []
    for p in properties:
        if p.latitude and p.longitude:
            pins.append({
                "pk": p.pk,
                "title": p.title,
                "lat": float(p.latitude),
                "lng": float(p.longitude),
                "price": int(p.price_per_year),
                "city": p.city,
                "image": p.display_image,
            })
    return json.dumps(pins)


def find_homes(request):
    properties, filters = _filter_properties(request)
    if request.htmx:
        return render(request, "partials/search_results.html", {"properties": properties})
    return render(request, "properties/listing.html", {
        "properties": properties,
        "type_choices": Property.TYPE_CHOICES,
        "properties_json": _properties_map_json(properties),
        **filters,
    })


def public_homes(request):
    properties, filters = _filter_properties(request)
    if request.htmx:
        return render(request, "partials/public_search_results.html", {"properties": properties})
    return render(request, "properties/homes.html", {
        "properties": properties,
        "type_choices": Property.TYPE_CHOICES,
        "properties_json": _properties_map_json(properties),
        **filters,
    })


def public_property_detail(request, pk):
    from .models import PropertyReview
    prop = get_object_or_404(Property, pk=pk)
    amenities = prop.amenities.select_related("amenity").all()
    reviews = prop.reviews.select_related("reviewer").all()
    return render(request, "properties/public_detail.html", {
        "property": prop,
        "amenities": amenities,
        "reviews": reviews,
    })



def property_detail(request, pk):
    from messaging.models import Conversation
    from leases.models import Lease
    from .models import PropertyReview
    prop = get_object_or_404(Property, pk=pk)
    is_owner = request.user.is_authenticated and (prop.landlord == request.user)
    applied = False
    has_lease = False
    conversation = None
    can_review = False
    has_reviewed = False
    if request.user.is_authenticated and request.user.is_tenant:
        applied = Application.objects.filter(tenant=request.user, rental_property=prop).exists()
        conversation = Conversation.objects.filter(tenant=request.user, rental_property=prop).first()
        has_lease = Lease.objects.filter(tenant=request.user, rental_property=prop).exists()
        if has_lease:
            has_reviewed = PropertyReview.objects.filter(property=prop, reviewer=request.user).exists()
            can_review = not has_reviewed
    amenities = prop.amenities.select_related("amenity").all()
    reviews = prop.reviews.select_related("reviewer").all()
    review_form = ReviewForm()
    return render(request, "properties/detail.html", {
        "property": prop,
        "applied": applied,
        "has_lease": has_lease,
        "is_owner": is_owner,
        "amenities": amenities,
        "conversation": conversation,
        "reviews": reviews,
        "can_review": can_review,
        "has_reviewed": has_reviewed,
        "review_form": review_form,
    })


@login_required
def apply_to_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        message = request.POST.get("message", "")
        employment_type = request.POST.get("employment_type", "")
        monthly_income = request.POST.get("monthly_income") or None
        Application.objects.get_or_create(
            tenant=request.user,
            rental_property=prop,
            defaults={
                "message": message,
                "employment_type": employment_type,
                "monthly_income": monthly_income,
            },
        )
        if request.htmx:
            return render(request, "partials/apply_button.html", {"property": prop, "applied": True, "available": prop.is_available})
        return redirect("property_detail", pk=pk)
    return redirect("property_detail", pk=pk)


@login_required
def my_properties(request):
    properties = request.user.properties.prefetch_related("applications").order_by("-created_at")
    return render(request, "properties/my_properties.html", {"properties": properties})


@login_required
def add_property(request):
    from .models import PropertyImage
    form = AddPropertyForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        prop = form.save(commit=False)
        prop.landlord = request.user
        prop.save()
        extra_images = request.FILES.getlist("extra_images")
        for index, img_file in enumerate(extra_images):
            PropertyImage.objects.create(
                property=prop,
                image=img_file,
                is_primary=(index == 0),
                order=index,
            )
        return redirect("my_properties")
    return render(request, "properties/add_property.html", {"form": form})


@login_required
def leave_review(request, pk):
    from .models import PropertyReview
    from leases.models import Lease
    from django.db.models import Avg
    prop = get_object_or_404(Property, pk=pk)
    if not request.user.is_tenant:
        return redirect("property_detail", pk=pk)
    has_lease = Lease.objects.filter(tenant=request.user, rental_property=prop).exists()
    if not has_lease:
        return redirect("property_detail", pk=pk)
    if PropertyReview.objects.filter(property=prop, reviewer=request.user).exists():
        return redirect("property_detail", pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            PropertyReview.objects.create(
                property=prop,
                reviewer=request.user,
                rating=int(form.cleaned_data["rating"]),
                comment=form.cleaned_data["comment"],
            )
            avg = prop.reviews.aggregate(avg=Avg("rating"))["avg"] or 0
            prop.rating = round(avg, 1)
            prop.save(update_fields=["rating"])
    return redirect("property_detail", pk=pk)
