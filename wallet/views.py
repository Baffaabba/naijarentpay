import uuid
import json
import hmac
import hashlib
import urllib.request
import urllib.parse
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db import transaction as db_transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Wallet, SavingsGoal, WalletTransaction, FundingRequest, SavedCard
from .forms import QuickSaveForm, FundWalletStep1Form, FundWalletStep2Form


# ── Gateway helpers ────────────────────────────────────────────────────────────

def _paystack_post(path, payload, secret_key):
    """POST to Paystack API. Returns parsed JSON dict."""
    url = f"https://api.paystack.co{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return {"status": False, "message": "Gateway error"}


def _paystack_get(path, secret_key):
    """GET from Paystack API. Returns parsed JSON dict."""
    url = f"https://api.paystack.co{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {secret_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return {"status": False, "message": "Gateway error"}


def _flutterwave_post(path, payload, secret_key):
    """POST to Flutterwave API. Returns parsed JSON dict."""
    url = f"https://api.flutterwave.com/v3{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return {"status": "error", "message": "Gateway error"}


def _flutterwave_get(path, secret_key):
    """GET from Flutterwave API. Returns parsed JSON dict."""
    url = f"https://api.flutterwave.com/v3{path}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {secret_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return {"status": "error", "message": "Gateway error"}


def _credit_wallet(wallet, amount, funding, description):
    """Atomically credit wallet and mark FundingRequest confirmed."""
    with db_transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        wallet.balance += Decimal(str(amount))
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet,
            description=description,
            amount=Decimal(str(amount)),
            transaction_type="credit",
        )
        FundingRequest.objects.filter(pk=funding.pk).update(status="confirmed")


def _get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(tenant=user)
    return wallet


@login_required
def savings_wallet(request):
    wallet = _get_or_create_wallet(request.user)
    goals = wallet.goals.filter(is_active=True)
    transactions = wallet.transactions.order_by("-created_at")[:10]
    total_in = sum(t.amount for t in wallet.transactions.filter(transaction_type="credit"))
    total_out = sum(t.amount for t in wallet.transactions.filter(transaction_type="debit"))
    return render(request, "wallet/savings.html", {
        "wallet": wallet,
        "goals": goals,
        "transactions": transactions,
        "total_in": total_in,
        "total_out": total_out,
        "quick_amounts": [500, 1000, 2000, 5000, 10000, 20000],
    })


@login_required
def fund_step1(request):
    form = FundWalletStep1Form()
    return render(request, "wallet/partials/fund_step1.html", {
        "form": form,
        "quick_amounts": [500, 1000, 2000, 5000, 10000, 20000],
    })


@login_required
def fund_step2(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = Decimal(str(amount))
        except Exception:
            amount = Decimal("0")
        request.session["fund_amount"] = str(amount)
        form = FundWalletStep2Form()
        return render(request, "wallet/partials/fund_step2.html", {
            "form": form,
            "amount": amount,
            "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
            "flutterwave_public_key": settings.FLUTTERWAVE_PUBLIC_KEY,
        })
    return redirect("savings_wallet")


@login_required
def fund_step3(request):
    """Receive method+gateway selection, call gateway API, render payment step."""
    if request.method != "POST":
        return redirect("savings_wallet")

    amount = Decimal(request.session.get("fund_amount", "0"))
    method = request.POST.get("method", "card")       # card | bank_transfer | ussd
    gateway = request.POST.get("gateway", "paystack")  # paystack | flutterwave
    ussd_bank = request.POST.get("ussd_bank", "057")   # default: Zenith

    wallet = _get_or_create_wallet(request.user)
    reference = f"NRP-{uuid.uuid4().hex[:12].upper()}"
    expires_at = timezone.now() + timezone.timedelta(minutes=30)

    sk = settings.PAYSTACK_SECRET_KEY
    fw_sk = settings.FLUTTERWAVE_SECRET_KEY

    context = {
        "amount": amount,
        "method": method,
        "gateway": gateway,
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
        "flutterwave_public_key": settings.FLUTTERWAVE_PUBLIC_KEY,
        "user_email": request.user.email,
    }

    # ── Paystack card (inline popup) ──────────────────────────────────────────
    if gateway == "paystack" and method == "card":
        funding = FundingRequest.objects.create(
            wallet=wallet, amount=amount, method="card",
            gateway="paystack", reference=reference,
            countdown_expires_at=expires_at,
        )
        context.update({
            "funding": funding,
            "reference": reference,
            "amount_kobo": int(amount * 100),
        })
        return render(request, "wallet/partials/fund_paystack_card.html", context)

    # ── Paystack bank transfer (virtual account) ──────────────────────────────
    if gateway == "paystack" and method == "bank_transfer":
        payload = {
            "email": request.user.email,
            "amount": int(amount * 100),
        }
        result = _paystack_post("/charge", payload, sk)
        gateway_data = result.get("data", {})
        funding = FundingRequest.objects.create(
            wallet=wallet, amount=amount, method="bank_transfer",
            gateway="paystack", reference=reference,
            gateway_data=gateway_data,
            countdown_expires_at=expires_at,
        )
        context.update({
            "funding": funding,
            "gateway_data": gateway_data,
            "bank_name": gateway_data.get("bank", {}).get("name", "Your Bank"),
            "account_number": gateway_data.get("bank", {}).get("account_number", "—"),
            "account_name": gateway_data.get("bank", {}).get("account_name", "9jaRentPay Escrow"),
            "expires_seconds": int((expires_at - timezone.now()).total_seconds()),
            "reference": reference,
        })
        return render(request, "wallet/partials/fund_bank_transfer.html", context)

    # ── Paystack USSD ─────────────────────────────────────────────────────────
    if gateway == "paystack" and method == "ussd":
        payload = {
            "email": request.user.email,
            "amount": int(amount * 100),
            "type": "ussd",
            "ussd": {"type": ussd_bank},
        }
        result = _paystack_post("/charge", payload, sk)
        gateway_data = result.get("data", {})
        ussd_code = gateway_data.get("ussd_code", "")
        funding = FundingRequest.objects.create(
            wallet=wallet, amount=amount, method="ussd",
            gateway="paystack", reference=reference,
            gateway_data=gateway_data,
            countdown_expires_at=expires_at,
        )
        context.update({
            "funding": funding,
            "ussd_code": ussd_code,
            "reference": reference,
            "gateway_data": gateway_data,
            "expires_seconds": int((expires_at - timezone.now()).total_seconds()),
        })
        return render(request, "wallet/partials/fund_ussd.html", context)

    # ── Flutterwave card (inline popup) ───────────────────────────────────────
    if gateway == "flutterwave" and method == "card":
        funding = FundingRequest.objects.create(
            wallet=wallet, amount=amount, method="card",
            gateway="flutterwave", reference=reference,
            countdown_expires_at=expires_at,
        )
        context.update({
            "funding": funding,
            "reference": reference,
            "user_name": request.user.get_full_name() or request.user.username,
            "user_phone": getattr(request.user, "phone", ""),
        })
        return render(request, "wallet/partials/fund_flutterwave_card.html", context)

    # Fallback
    return redirect("savings_wallet")


# ── Paystack: verify card payment (called via fetch from JS popup callback) ───

@login_required
@require_POST
def paystack_verify(request):
    """Client POSTs the reference after Paystack popup success; server verifies and credits."""
    reference = request.POST.get("reference", "")
    if not reference:
        return JsonResponse({"ok": False, "error": "No reference"}, status=400)

    try:
        funding = FundingRequest.objects.get(reference=reference)
    except FundingRequest.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Unknown reference"}, status=400)

    if funding.wallet.tenant != request.user:
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    if funding.status == "confirmed":
        wallet = _get_or_create_wallet(request.user)
        return JsonResponse({"ok": True, "balance": str(wallet.balance)})

    result = _paystack_get(f"/transaction/verify/{reference}", settings.PAYSTACK_SECRET_KEY)
    if result.get("status") and result.get("data", {}).get("status") == "success":
        wallet = funding.wallet
        _credit_wallet(wallet, funding.amount, funding,
                       f"Wallet funded via Card (Paystack)")
        wallet.refresh_from_db()
        return JsonResponse({"ok": True, "balance": str(wallet.balance)})
    return JsonResponse({"ok": False, "error": result.get("message", "Verification failed")}, status=400)


# ── Flutterwave: verify card payment ─────────────────────────────────────────

@login_required
@require_POST
def flutterwave_verify(request):
    """Client POSTs the transaction_id after Flutterwave success; server verifies and credits."""
    tx_id = request.POST.get("transaction_id", "")
    reference = request.POST.get("reference", "")
    if not tx_id or not reference:
        return JsonResponse({"ok": False, "error": "Missing data"}, status=400)

    try:
        funding = FundingRequest.objects.get(reference=reference)
    except FundingRequest.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Unknown reference"}, status=400)

    if funding.wallet.tenant != request.user:
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    if funding.status == "confirmed":
        wallet = _get_or_create_wallet(request.user)
        return JsonResponse({"ok": True, "balance": str(wallet.balance)})

    result = _flutterwave_get(f"/transactions/{tx_id}/verify", settings.FLUTTERWAVE_SECRET_KEY)
    data = result.get("data", {})
    if result.get("status") == "success" and data.get("status") == "successful":
        wallet = funding.wallet
        _credit_wallet(wallet, funding.amount, funding,
                       "Wallet funded via Card (Flutterwave)")
        wallet.refresh_from_db()
        return JsonResponse({"ok": True, "balance": str(wallet.balance)})
    return JsonResponse({"ok": False, "error": "Verification failed"}, status=400)


# ── Legacy confirm (manual "I've sent the money" for bank transfer fallback) ──

@login_required
def fund_confirm(request):
    if request.method == "POST":
        ref = request.POST.get("ref")
        wallet = _get_or_create_wallet(request.user)
        try:
            funding = FundingRequest.objects.get(reference=ref, wallet=wallet, status="pending")
        except FundingRequest.DoesNotExist:
            # Try legacy bank_ref field
            try:
                funding = FundingRequest.objects.get(bank_ref=ref, wallet=wallet, status="pending")
            except FundingRequest.DoesNotExist:
                return HttpResponse("Invalid reference.", status=400)

        _credit_wallet(wallet, funding.amount, funding,
                       f"Wallet funded via {funding.get_method_display()}")
        wallet.refresh_from_db()
        return render(request, "wallet/partials/fund_success.html", {
            "wallet": wallet,
            "amount": funding.amount,
        })
    return redirect("savings_wallet")


# ── Paystack Webhook ──────────────────────────────────────────────────────────

@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook events (bank transfer, USSD completion, etc.)."""
    if request.method != "POST":
        return HttpResponse(status=405)

    sig = request.headers.get("X-Paystack-Signature", "")
    sk = settings.PAYSTACK_SECRET_KEY
    expected = hmac.new(sk.encode(), request.body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return HttpResponse(status=400)

    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponse(status=400)

    event = payload.get("event", "")
    data = payload.get("data", {})

    if event == "charge.success":
        reference = data.get("reference", "")
        amount_kobo = data.get("amount", 0)
        amount = Decimal(str(amount_kobo)) / 100
        try:
            funding = FundingRequest.objects.get(reference=reference, status="pending")
        except FundingRequest.DoesNotExist:
            return HttpResponse(status=200)
        _credit_wallet(funding.wallet, amount, funding,
                       f"Wallet funded via {funding.get_method_display()} (Paystack)")

    return HttpResponse(status=200)


# ── Flutterwave Webhook ───────────────────────────────────────────────────────

@csrf_exempt
def flutterwave_webhook(request):
    """Handle Flutterwave webhook events."""
    if request.method != "POST":
        return HttpResponse(status=405)

    verif_hash = request.headers.get("Verif-Hash", "")
    if verif_hash != settings.FLUTTERWAVE_WEBHOOK_HASH:
        return HttpResponse(status=400)

    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponse(status=400)

    if payload.get("event") == "charge.completed":
        data = payload.get("data", {})
        tx_ref = data.get("tx_ref", "")
        status = data.get("status", "")
        amount = Decimal(str(data.get("amount", 0)))
        if status == "successful" and tx_ref:
            try:
                funding = FundingRequest.objects.get(reference=tx_ref, status="pending")
            except FundingRequest.DoesNotExist:
                return HttpResponse(status=200)
            _credit_wallet(funding.wallet, amount, funding,
                           "Wallet funded via Card (Flutterwave)")

    return HttpResponse(status=200)


# ── Savings helpers ───────────────────────────────────────────────────────────

@login_required
def quick_add_savings(request):
    if request.method == "POST":
        wallet = _get_or_create_wallet(request.user)
        try:
            amount = Decimal(str(request.POST.get("amount", "0")))
        except Exception:
            amount = Decimal("0")
        goal_id = request.POST.get("goal_id")
        if goal_id:
            goal = get_object_or_404(SavingsGoal, pk=goal_id, wallet=wallet)
        else:
            goal = wallet.goals.filter(is_active=True).first()

        if goal and amount > 0 and wallet.balance >= amount:
            goal.saved_amount += amount
            goal.save()
            wallet.balance -= amount
            wallet.save()
            WalletTransaction.objects.create(
                wallet=wallet,
                description=f"Added to {goal.goal_name}",
                amount=amount,
                transaction_type="debit",
            )

        goals = wallet.goals.filter(is_active=True)
        return render(request, "wallet/partials/savings_summary.html", {
            "wallet": wallet,
            "goals": goals,
        })
    return redirect("savings_wallet")


@login_required
def toggle_autosave(request, goal_id):
    wallet = _get_or_create_wallet(request.user)
    goal = get_object_or_404(SavingsGoal, pk=goal_id, wallet=wallet)
    if request.method == "POST":
        goal.auto_save = not goal.auto_save
        goal.save()
        if request.htmx:
            return render(request, "wallet/partials/autosave_badge.html", {"goal": goal})
    return redirect("savings_wallet")


# ── Saved Cards ───────────────────────────────────────────────────────────────

@login_required
@require_POST
def save_card(request):
    """Verify a Paystack charge and store the card authorisation."""
    reference = request.POST.get("reference", "")
    if not reference:
        return JsonResponse({"ok": False, "error": "Missing reference"}, status=400)

    result = _paystack_get(f"/transaction/verify/{reference}", settings.PAYSTACK_SECRET_KEY)
    if result.get("status") and result.get("data", {}).get("status") == "success":
        auth = result["data"].get("authorization", {})
        auth_code = auth.get("authorization_code", "")
        # Map Paystack card_type string to our choices
        raw_type = auth.get("card_type", "unknown").lower()
        card_type = "visa" if "visa" in raw_type else \
                    "mastercard" if "master" in raw_type else \
                    "verve" if "verve" in raw_type else "unknown"

        SavedCard.objects.update_or_create(
            user=request.user,
            auth_code=auth_code,
            defaults={
                "card_type": card_type,
                "last4": auth.get("last4", ""),
                "exp_month": auth.get("exp_month", ""),
                "exp_year": auth.get("exp_year", ""),
                "bank": auth.get("bank", ""),
                "is_default": not SavedCard.objects.filter(user=request.user).exists(),
            },
        )
        cards = SavedCard.objects.filter(user=request.user)
        return render(request, "wallet/partials/saved_cards.html", {"cards": cards})

    return JsonResponse({"ok": False, "error": "Verification failed"}, status=400)


@login_required
@require_POST
def delete_card(request, pk):
    card = get_object_or_404(SavedCard, pk=pk, user=request.user)
    card.delete()
    cards = SavedCard.objects.filter(user=request.user)
    return render(request, "wallet/partials/saved_cards.html", {"cards": cards})
