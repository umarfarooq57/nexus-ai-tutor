"""
WebSocket routing for real-time features
"""

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/learning/<str:session_id>/', consumers.LearningSessionConsumer.as_asgi()),
    path('ws/ai-assistant/', consumers.AIAssistantConsumer.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]
