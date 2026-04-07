from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.property_detail, name="property_detail"),
    path("<int:pk>/apply/", views.apply_to_property, name="apply_to_property"),
    path("<int:pk>/review/", views.leave_review, name="leave_review"),
    path("browse/", views.public_homes, name="public_homes"),
    path("browse/<int:pk>/", views.public_property_detail, name="public_property_detail"),
]
