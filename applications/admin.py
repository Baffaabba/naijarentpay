from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["tenant", "rental_property", "applied_date", "status", "employment_type"]
    list_filter = ["status", "employment_type"]
