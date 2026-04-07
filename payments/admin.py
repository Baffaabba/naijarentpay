from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["tenant", "rental_property", "amount", "date", "status"]
    list_filter = ["status"]
