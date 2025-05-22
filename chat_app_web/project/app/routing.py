from django.urls import re_path , path
from . import consumers 
from .views import private_chat_view
from channels.routing import ProtocolTypeRouter , URLRouter
from channels.auth import AuthMiddlewareStack


websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
     re_path(r'^ws/privatechat/(?P<user_id>\d+)/$', consumers.PrivateChatConsumer.as_asgi()),
]



application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})