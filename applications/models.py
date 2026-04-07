from django.db import models


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    EMPLOYMENT_CHOICES = [
        ("employed", "Employed"),
        ("self_employed", "Self-Employed"),
        ("business_owner", "Business Owner"),
        ("student", "Student"),
        ("other", "Other"),
    ]
    tenant = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="applications"
    )
    rental_property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="applications"
    )
    applied_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_CHOICES, blank=True
    )
    monthly_income = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tenant} → {self.rental_property} [{self.status}]"
