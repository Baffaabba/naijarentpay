from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "get_full_name", "role", "is_kyc_verified"]
    list_filter = ["role", "is_kyc_verified"]
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("role", "phone", "avatar", "id_document", "is_kyc_verified", "address")}),
    )
