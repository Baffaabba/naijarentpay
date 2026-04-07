from django.urls import path
from . import views

urlpatterns = [
    path("", views.notifications_list, name="notifications_list"),
    path("unread-count/", views.unread_count, name="notifications_unread_count"),
    path("mark-all-read/", views.mark_all_read, name="notifications_mark_all_read"),
    path("<int:pk>/read/", views.mark_read, name="notification_mark_read"),
    path("dropdown/", views.notification_dropdown, name="notification_dropdown"),
]
