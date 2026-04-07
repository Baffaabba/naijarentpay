from django.urls import path
from . import views

urlpatterns = [
    path("my-lease/", views.my_lease, name="my_lease_direct"),
]
