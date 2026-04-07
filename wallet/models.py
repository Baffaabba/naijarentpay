from django.db import models
from django.utils import timezone


class Wallet(models.Model):
    tenant = models.OneToOneField(
        "accounts.User", on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Wallet: {self.tenant} — ₦{self.balance}"


class SavingsGoal(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="goals")
    goal_name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    auto_save = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.goal_name

    @property
    def percentage_saved(self):
        if self.target_amount == 0:
            return 0
        return round((self.saved_amount / self.target_amount) * 100, 1)

    @property
    def days_remaining(self):
        delta = self.due_date - timezone.now().date()
        return max(delta.days, 0)

    @property
    def amount_remaining(self):
        return max(self.target_amount - self.saved_amount, 0)


class WalletTransaction(models.Model):
    TYPE_CHOICES = [("credit", "Credit"), ("debit", "Debit")]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.transaction_type == "credit" else "-"
        return f"{sign}₦{self.amount} — {self.description}"


class FundingRequest(models.Model):
    METHOD_CHOICES = [
        ("bank_transfer", "Bank Transfer"),
        ("card", "Card"),
        ("ussd", "USSD"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("expired", "Expired"),
    ]
    GATEWAY_CHOICES = [
        ("paystack", "Paystack"),
        ("flutterwave", "Flutterwave"),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="funding_requests")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=15, choices=METHOD_CHOICES, default="bank_transfer")
    gateway = models.CharField(max_length=15, choices=GATEWAY_CHOICES, blank=True, default="paystack")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    reference = models.CharField(max_length=100, blank=True, null=True, unique=True)
    bank_ref = models.CharField(max_length=20, blank=True)
    # Extra JSON data returned by gateway (USSD code, virtual account, etc.)
    gateway_data = models.JSONField(default=dict, blank=True)
    countdown_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FundingRequest ₦{self.amount} [{self.status}]"


class SavedCard(models.Model):
    CARD_TYPE_CHOICES = [
        ("visa", "Visa"),
        ("mastercard", "Mastercard"),
        ("verve", "Verve"),
        ("unknown", "Unknown"),
    ]
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="saved_cards")
    card_type = models.CharField(max_length=12, choices=CARD_TYPE_CHOICES, default="unknown")
    last4 = models.CharField(max_length=4)
    exp_month = models.CharField(max_length=2)
    exp_year = models.CharField(max_length=4)
    auth_code = models.CharField(max_length=200)  # Paystack authorization_code
    bank = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.get_card_type_display()} •••• {self.last4} ({self.user})"


class SavedCard(models.Model):
    CARD_TYPE_CHOICES = [
        ("visa", "Visa"),
        ("mastercard", "Mastercard"),
        ("verve", "Verve"),
        ("unknown", "Unknown"),
    ]
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="saved_cards"
    )
    card_type = models.CharField(max_length=12, choices=CARD_TYPE_CHOICES, default="unknown")
    last4 = models.CharField(max_length=4)
    exp_month = models.CharField(max_length=2)
    exp_year = models.CharField(max_length=4)
    auth_code = models.CharField(max_length=200)
    bank = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.get_card_type_display()} •••• {self.last4}"
