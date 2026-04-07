from django.db import models


class Conversation(models.Model):
    tenant = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="tenant_conversations"
    )
    landlord = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="landlord_conversations"
    )
    rental_property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("tenant", "landlord", "rental_property")]

    def __str__(self):
        return f"Convo: {self.tenant} ↔ {self.landlord} re {self.rental_property}"

    @property
    def last_message(self):
        return self.messages.order_by("-sent_at").first()

    @property
    def unread_count(self):
        return self.messages.filter(is_read=False).count()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}"
