from django.core.mail import send_mail
from django.conf import settings


# Notification types that warrant an email
EMAIL_TYPES = {
    "application_received",
    "application_approved",
    "application_rejected",
    "payment_confirmed",
    "lease_created",
    "rent_due",
}


def send_notification_email(user, notification):
    if notification.notification_type not in EMAIL_TYPES:
        return
    if not user.email:
        return
    subject = notification.title
    body = notification.body or notification.title
    if notification.link:
        base_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        body += f"\n\nView: {base_url}{notification.link}"
    send_mail(
        subject=f"[9jaRentPay] {subject}",
        message=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@9jarentpay.com"),
        recipient_list=[user.email],
        fail_silently=True,
    )
