import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import LoginForm, RegisterStep1Form, RegisterStep2Form, ProfileForm, SecurityForm
from .models import User
from wallet.models import SavedCard


def landing_page(request):
    if request.user.is_authenticated:
        return redirect("tenant_dashboard" if request.user.is_tenant else "landlord_dashboard")
    return render(request, "landing.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("tenant_dashboard" if request.user.is_tenant else "landlord_dashboard")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.is_landlord:
            return redirect("landlord_dashboard")
        return redirect("tenant_dashboard")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method in ("POST", "GET"):
        logout(request)
    return redirect("landing")


def register_step1(request):
    if request.user.is_authenticated:
        return redirect("landing")
    form = RegisterStep1Form(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        otp = str(random.randint(100000, 999999))
        print(f"\n{'='*40}\nOTP for {form.cleaned_data['email']}: {otp}\n{'='*40}\n")
        request.session["reg_step1"] = {
            "role": form.cleaned_data["role"],
            "first_name": form.cleaned_data["first_name"],
            "last_name": form.cleaned_data["last_name"],
            "email": form.cleaned_data["email"],
            "password": form.cleaned_data["password"],
            "otp": otp,
        }
        return redirect("register_step2")
    return render(request, "accounts/register_step1.html", {"form": form})


def register_step2(request):
    step1 = request.session.get("reg_step1")
    if not step1:
        return redirect("register_step1")
    form = RegisterStep2Form(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["otp"] != step1.get("otp"):
            error = "Invalid verification code."
        else:
            from django.db import IntegrityError
            username = step1["email"].split("@")[0]
            base = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1
            try:
                user = User.objects.create_user(
                    username=username,
                    email=step1["email"],
                    password=step1["password"],
                    first_name=step1["first_name"],
                    last_name=step1["last_name"],
                    role=step1["role"],
                    phone=form.cleaned_data.get("phone", ""),
                    address=form.cleaned_data.get("address", ""),
                )
            except IntegrityError:
                error = "An account with this email already exists. Please go back and use a different email."
                return render(request, "accounts/register_step2.html", {"form": form, "error": error, "email": step1["email"]})
            del request.session["reg_step1"]
            login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
            if user.is_landlord:
                return redirect("landlord_dashboard")
            return redirect("tenant_dashboard")
    return render(request, "accounts/register_step2.html", {"form": form, "error": error, "email": step1["email"]})


@login_required
def tenant_settings(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    security_form = SecurityForm()
    active_tab = request.GET.get("tab", "profile")

    if request.method == "POST":
        tab = request.POST.get("tab", "profile")
        form_type = request.POST.get("form_type", tab)
        active_tab = form_type if form_type in ("profile", "security", "kyc") else tab
        if form_type == "profile":
            profile_form = ProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated.")
        elif form_type == "security":
            security_form = SecurityForm(request.POST)
            if security_form.is_valid():
                cd = security_form.cleaned_data
                auth_user = authenticate(request, username=user.username, password=cd["current_password"])
                if auth_user:
                    user.set_password(cd["new_password"])
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Password changed.")
                else:
                    messages.error(request, "Current password is incorrect.")
        elif form_type == "kyc":
            if "id_document" in request.FILES:
                user.id_document = request.FILES["id_document"]
                user.save()
                messages.success(request, "ID document uploaded. KYC verification is pending.")

    return render(request, "accounts/settings.html", {
        "profile_form": profile_form,
        "security_form": security_form,
        "active_tab": active_tab,
        "saved_cards": SavedCard.objects.filter(user=user),
        "PAYSTACK_PUBLIC_KEY": settings.PAYSTACK_PUBLIC_KEY,
        "notification_labels": [
            "Rent reminders", "Lease updates", "New messages",
            "Payment confirmations", "Application status", "Platform announcements",
        ],
    })
@login_required
def landlord_settings(request):
    return tenant_settings(request)
