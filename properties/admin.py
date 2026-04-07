from django.contrib import admin
from .models import Property, Amenity, PropertyAmenity


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["title", "property_type", "location", "price_per_year", "is_available", "is_verified"]
    list_filter = ["property_type", "is_available", "is_verified", "state"]
    search_fields = ["title", "location", "city"]


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ["name", "icon"]


@admin.register(PropertyAmenity)
class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = ["property", "amenity"]
