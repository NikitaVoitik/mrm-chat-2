from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIChatViewSet, AIMessageViewSet

router = DefaultRouter()
router.register(r'chats', AIChatViewSet, basename='ai-chat')
router.register(r'messages', AIMessageViewSet, basename='ai-message')

urlpatterns = [
    path('', include(router.urls)),
]
