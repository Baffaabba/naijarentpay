from django.db.models.signals import post_save
from django.dispatch import receiver


def _create(user, ntype, title, body="", link=""):
    from .models import Notification
    from .email import send_notification_email
    n = Notification.objects.create(
        user=user,
        notification_type=ntype,
        title=title,
        body=body,
        link=link,
    )
    try:
        send_notification_email(user, n)
    except Exception:
        pass


# ─── Applications ────────────────────────────────────────────────────────────

@receiver(post_save, sender="applications.Application")
def on_application_save(sender, instance, created, **kwargs):
    if created:
        # Notify landlord
        _create(
            user=instance.rental_property.landlord,
            ntype="application_received",
            title=f"New application for {instance.rental_property.title}",
            body=f"{instance.tenant.get_full_name()} applied for your property.",
            link=f"/applications/",
        )
    else:
        # Notify tenant on status change
        if instance.status == "approved":
            _create(
                user=instance.tenant,
                ntype="application_approved",
                title=f"Application approved — {instance.rental_property.title}",
                body="Congratulations! Your rental application has been approved.",
                link=f"/applications/my/",
            )
        elif instance.status == "rejected":
            _create(
                user=instance.tenant,
                ntype="application_rejected",
                title=f"Application update — {instance.rental_property.title}",
                body="Unfortunately your application was not successful this time.",
                link=f"/applications/my/",
            )


# ─── Messages ────────────────────────────────────────────────────────────────

@receiver(post_save, sender="messaging.Message")
def on_message_save(sender, instance, created, **kwargs):
    if not created:
        return
    conv = instance.conversation
    recipient = conv.landlord if instance.sender == conv.tenant else conv.tenant
    _create(
        user=recipient,
        ntype="message_received",
        title=f"New message from {instance.sender.get_full_name()}",
        body=instance.content[:120],
        link=f"/messages/?conv={conv.pk}",
    )


# ─── Leases ──────────────────────────────────────────────────────────────────

@receiver(post_save, sender="leases.Lease")
def on_lease_save(sender, instance, created, **kwargs):
    if created:
        _create(
            user=instance.tenant,
            ntype="lease_created",
            title=f"Your lease is ready — {instance.rental_property.title}",
            body="Your lease agreement has been created. Review it in My Lease.",
            link="/leases/my/",
        )


# ─── Payments ────────────────────────────────────────────────────────────────

@receiver(post_save, sender="payments.Payment")
def on_payment_save(sender, instance, created, **kwargs):
    if instance.status == "paid":
        _create(
            user=instance.tenant,
            ntype="payment_confirmed",
            title=f"Payment confirmed — ₦{instance.amount:,.0f}",
            body=f"Your rent payment for {instance.rental_property.title} was successful.",
            link="/payments/history/",
        )
        _create(
            user=instance.rental_property.landlord,
            ntype="payment_confirmed",
            title=f"Rent received — ₦{instance.amount:,.0f}",
            body=f"{instance.tenant.get_full_name()} paid rent for {instance.rental_property.title}.",
            link="/landlord/earnings/",
        )
