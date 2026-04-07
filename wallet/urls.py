from django.urls import path
from . import views

urlpatterns = [
    path("savings/", views.savings_wallet, name="savings_wallet_direct"),
    path("fund/", views.fund_step1, name="fund_step1"),
    path("fund/step2/", views.fund_step2, name="fund_step2"),
    path("fund/step3/", views.fund_step3, name="fund_step3"),
    path("fund/confirm/", views.fund_confirm, name="fund_confirm"),
    path("quick-add/", views.quick_add_savings, name="quick_add_savings"),
    path("autosave/<int:goal_id>/", views.toggle_autosave, name="toggle_autosave"),
    # Payment gateway callbacks
    path("paystack/verify/", views.paystack_verify, name="paystack_verify"),
    path("flutterwave/verify/", views.flutterwave_verify, name="flutterwave_verify"),
    # Webhooks (csrf_exempt, login_not_required — registered at top level in main urls.py)
    path("paystack/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path("flutterwave/webhook/", views.flutterwave_webhook, name="flutterwave_webhook"),
    # Saved cards
    path("card/save/", views.save_card, name="save_card"),
    path("card/<int:pk>/delete/", views.delete_card, name="delete_card"),
]
