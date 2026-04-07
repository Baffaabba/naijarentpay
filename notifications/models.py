from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ("application_received", "New Application"),
        ("application_approved", "Application Approved"),
        ("application_rejected", "Application Rejected"),
        ("message_received", "New Message"),
        ("payment_confirmed", "Payment Confirmed"),
        ("lease_created", "Lease Created"),
        ("rent_due", "Rent Due"),
        ("system", "System"),
    ]
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="system")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.user}"
