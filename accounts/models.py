from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [("tenant", "Tenant"), ("landlord", "Landlord")]
    TIER_CHOICES = [
        ("free", "Free"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="tenant")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    id_document = models.FileField(upload_to="id_docs/", blank=True, null=True)
    is_kyc_verified = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def initials(self):
        parts = self.get_full_name().split()
        return "".join(p[0].upper() for p in parts[:2]) if parts else "U"

    @property
    def is_landlord(self):
        return self.role == "landlord"

    @property
    def is_tenant(self):
        return self.role == "tenant"

    @property
    def membership_tier(self):
        """Compute tier based on KYC status — no subscription needed."""
        if self.is_kyc_verified and self.id_document:
            return "premium"
        if self.phone and self.email:
            return "standard"
        return "free"

    @property
    def tier_label(self):
        return {"free": "Free", "standard": "Standard", "premium": "Premium"}.get(self.membership_tier, "Free")

    @property
    def tier_color(self):
        return {
            "free": "bg-gray-100 text-gray-600",
            "standard": "bg-blue-100 text-blue-700",
            "premium": "bg-amber-100 text-amber-700",
        }.get(self.membership_tier, "bg-gray-100 text-gray-600")

    @property
    def tier_badge_emoji(self):
        return {"free": "⬜", "standard": "🔵", "premium": "⭐"}.get(self.membership_tier, "⬜")
