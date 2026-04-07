from django.urls import path
from . import views

urlpatterns = [
    path("", views.applications_list, name="applications_list_direct"),
    path("<int:pk>/approve/", views.approve_application, name="approve_application_direct"),
    path("<int:pk>/reject/", views.reject_application, name="reject_application_direct"),
]
