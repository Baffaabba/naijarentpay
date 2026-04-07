from django.db import models


class Lease(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("terminated", "Terminated"),
    ]
    tenant = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="leases"
    )
    rental_property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="leases"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2)
    next_rent_due = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lease: {self.tenant} → {self.rental_property}"

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def duration_months(self):
        delta = self.end_date - self.start_date
        return round(delta.days / 30)
