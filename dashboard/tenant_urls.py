from django.urls import path
from . import views
from properties import views as prop_views
from leases import views as lease_views
from wallet import views as wallet_views
from messaging import views as msg_views
from applications import views as app_views
from accounts import views as acc_views

urlpatterns = [
    path("dashboard/", views.tenant_dashboard, name="tenant_dashboard"),
    path("find-homes/", prop_views.find_homes, name="find_homes"),
    path("my-lease/", lease_views.my_lease, name="my_lease"),
    path("savings/", wallet_views.savings_wallet, name="savings_wallet"),
    path("messages/", msg_views.messages_list, name="tenant_messages"),
    path("applications/", app_views.my_applications, name="my_applications"),
    path("settings/", acc_views.tenant_settings, name="tenant_settings"),
]
