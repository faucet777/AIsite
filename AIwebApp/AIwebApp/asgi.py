"""
ASGI config for AIwebApp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from AIsite.consumers import ChatConsumer
from channels.auth import AuthMiddlewareStack
from django.urls import path, include
from AIsite import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AIwebApp.settings')

# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(routing.websocket_urlpatterns)
    ),
    # Add other protocol types and applications if needed
})
