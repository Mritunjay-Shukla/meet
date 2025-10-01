from django.urls import re_path, path
from meetapp import consumers

websocket_urlpatterns = [
    path('ws/call/<str:room_id>/', consumers.CallConsumer.as_asgi()),
]
