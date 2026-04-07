from django.urls import path
from . import views
from properties import views as prop_views
from applications import views as app_views
from messaging import views as msg_views
from accounts import views as acc_views

urlpatterns = [
    path("dashboard/", views.landlord_dashboard, name="landlord_dashboard"),
    path("properties/", prop_views.my_properties, name="my_properties"),
    path("properties/add/", prop_views.add_property, name="add_property"),
    path("applications/", app_views.applications_list, name="applications_list"),
    path("applications/<int:pk>/approve/", app_views.approve_application, name="approve_application"),
    path("applications/<int:pk>/reject/", app_views.reject_application, name="reject_application"),
    path("earnings/", views.landlord_earnings, name="landlord_earnings"),
    path("tenants/", views.landlord_tenants, name="landlord_tenants"),
    path("messages/", msg_views.messages_list, name="landlord_messages"),
    path("settings/", acc_views.landlord_settings, name="landlord_settings"),
]
