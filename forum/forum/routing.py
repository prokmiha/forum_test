from django.urls import re_path
from shared.services.realtime.consumers import CommentConsumer


websocket_urlpatterns = [
    re_path(r'ws/comments/$', CommentConsumer.as_asgi()),
]