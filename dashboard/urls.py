from django.urls import path
from . import views

# NOTE: This file is included TWICE in root urls.py:
#   path("tenant/", include("dashboard.urls"))
#   path("landlord/", include("dashboard.urls"))
# Django allows this but names collide — use app_name namespacing avoids that.
# Instead we define both sets of names here; the view itself guards by role.

urlpatterns = [
    # tenant routes (mounted under /tenant/)
    path("dashboard/", views.tenant_dashboard, name="tenant_dashboard"),
    path("find-homes/", views.find_homes_redirect, name="find_homes"),
    path("my-lease/", views.my_lease_redirect, name="my_lease"),
    path("savings/", views.savings_redirect, name="savings_wallet"),
    path("messages/", views.messages_redirect, name="tenant_messages"),
    path("applications/", views.tenant_applications_redirect, name="my_applications"),
    path("settings/", views.tenant_settings_redirect, name="tenant_settings_dash"),
    # landlord routes (mounted under /landlord/)
    path("dashboard/", views.landlord_dashboard, name="landlord_dashboard"),
    path("properties/", views.my_properties_redirect, name="my_properties"),
    path("properties/add/", views.add_property_redirect, name="add_property"),
    path("applications/", views.landlord_applications_redirect, name="applications_list"),
    path("earnings/", views.landlord_earnings, name="landlord_earnings"),
    path("tenants/", views.landlord_tenants, name="landlord_tenants"),
    path("messages/", views.messages_redirect, name="landlord_messages"),
    path("settings/", views.landlord_settings_redirect, name="landlord_settings_dash"),
]
