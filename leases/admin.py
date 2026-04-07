from django.contrib import admin
from .models import Lease


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ["tenant", "rental_property", "start_date", "end_date", "status", "rent_amount"]
    list_filter = ["status"]
