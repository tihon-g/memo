from django.conf.urls import url, re_path
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from chat.consumers import ChatConsumer, TaskConsumer
from render.consumers import RenderConsumer, ServerConsumer

application = ProtocolTypeRouter({
    # Websocket chat handler
    'websocket':
        AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(r"^messages/(?P<username>[\w.@+-]+)$", ChatConsumer(), name='chat'),
                        re_path(r"^api/render/$", RenderConsumer(), name='render'),
                        re_path(r"^server_info$", ServerConsumer(), name='server')
                    ]
                )
            ),
        ),
    'channel': ChannelNameRouter({
        'task': TaskConsumer
    })
})