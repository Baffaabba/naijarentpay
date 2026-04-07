from django.contrib import admin
from .models import Wallet, SavingsGoal, WalletTransaction, FundingRequest


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["tenant", "balance"]


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ["goal_name", "wallet", "saved_amount", "target_amount", "due_date", "auto_save"]


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ["wallet", "description", "amount", "transaction_type", "created_at"]
    list_filter = ["transaction_type"]


@admin.register(FundingRequest)
class FundingRequestAdmin(admin.ModelAdmin):
    list_display = ["wallet", "amount", "method", "status", "created_at"]
    list_filter = ["status", "method"]
