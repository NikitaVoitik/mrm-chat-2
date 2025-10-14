import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user is a participant in this chat
        is_participant = await self.check_participant()
        if not is_participant:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            content = data.get('content', '')

            if not content:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Content cannot be empty'
                }))
                return

            # Save message to database
            message = await self.save_message(content)

            # Serialize the message
            message_data = await self.serialize_message(message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def chat_message(self, event):
        """Receive message from room group"""
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))

    @database_sync_to_async
    def check_participant(self):
        """Check if user is a participant in the chat"""
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return chat.participants.filter(id=self.user.id).exists()
        except Chat.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """Save message to database"""
        chat = Chat.objects.get(id=self.chat_id)
        message = Message.objects.create(
            chat=chat,
            sender=self.user,
            content=content
        )
        return message

    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize message using MessageSerializer"""
        serializer = MessageSerializer(message)
        return serializer.data
