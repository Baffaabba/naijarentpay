from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [("paid", "Paid"), ("pending", "Pending"), ("failed", "Failed")]
    tenant = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="payments"
    )
    rental_property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="payments"
    )
    lease = models.ForeignKey(
        "leases.Lease", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"₦{self.amount} — {self.tenant} [{self.status}]"
