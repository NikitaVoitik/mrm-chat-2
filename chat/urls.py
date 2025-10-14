from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'chats', views.ChatViewSet, basename='chat')
router.register(r'messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('me/', views.current_user, name='current_user'),
    path('users/', views.list_users, name='list_users'),
    path('', include(router.urls)),
]
