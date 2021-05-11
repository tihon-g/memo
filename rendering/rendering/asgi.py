import os

import django
from channels.routing import get_default_application

# from channels.sessions import SessionMiddlewareStack
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# from chat.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rendering.settings")
django.setup()
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

application = get_default_application()

# application = ProtocolTypeRouter({
#   "http": get_asgi_application(),
#   "websocket": AuthMiddlewareStack(
#         AllowedHostsOriginValidator(
#             # SessionMiddlewareStack(
#             URLRouter(
#                 websocket_urlpatterns
#             )
#         )
#       # )
#     ),
# })
