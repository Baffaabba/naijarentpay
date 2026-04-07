from django.urls import path
from . import views

urlpatterns = [
    path("", views.messages_list, name="messages_list"),
    path("<int:conv_id>/send/", views.send_message, name="send_message"),
    path("initiate/<int:property_pk>/", views.initiate_conversation, name="initiate_conversation"),
]
