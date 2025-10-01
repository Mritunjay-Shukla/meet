from django.urls import path
from meetapp import views

app_name="meetapp"

urlpatterns = [
    path("call/create/", views.create_room, name="create_room"),
    path("call/room/<str:room_id>/", views.call_room, name="call_room"),
]
