import os
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     # "http": AsgiHandler(),
#     # Just HTTP for now. (We can add other protocols later.)
# })
# application = AuthMiddlewareStack(application)
