from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from .consumers import AppointmentConsumer  # Ensure the correct path for your consumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/appointments/", AppointmentConsumer.as_asgi()),  # Adjust the URL path as needed
        ])
    ),
})
