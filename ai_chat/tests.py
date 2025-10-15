import json
from unittest.mock import Mock, patch
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from .models import AIChat, AIMessage
from chat.models import Chat, Message
from .consumers import AIChatConsumer

User = get_user_model()


# =============================================================================
# MODEL TESTS (Unit Tests)
# =============================================================================

class AIChatModelTest(TestCase):
    """Unit tests for AIChat model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.chat = Chat.objects.create(name='Test Chat')
        self.chat.participants.add(self.user)
    
    def test_create_ai_chat_without_related_chat(self):
        """Test creating an AI chat without a related chat"""
        ai_chat = AIChat.objects.create(
            user=self.user,
            title='Test AI Chat',
            system_prompt='You are a helpful assistant.'
        )
        self.assertEqual(ai_chat.user, self.user)
        self.assertEqual(ai_chat.title, 'Test AI Chat')
        self.assertIsNone(ai_chat.related_chat)
        self.assertIsNotNone(ai_chat.created_at)
        self.assertIsNotNone(ai_chat.updated_at)
    
    def test_create_ai_chat_with_related_chat(self):
        """Test creating an AI chat with a related chat"""
        ai_chat = AIChat.objects.create(
            user=self.user,
            title='Test AI Chat',
            system_prompt='You are a helpful assistant.',
            related_chat=self.chat
        )
        self.assertEqual(ai_chat.related_chat, self.chat)
        self.assertIn(ai_chat, self.chat.ai_chats.all())
    
    def test_ai_chat_string_representation(self):
        """Test AIChat __str__ method"""
        ai_chat = AIChat.objects.create(
            user=self.user,
            title='Test AI Chat'
        )
        self.assertEqual(str(ai_chat), f'Test AI Chat - {self.user.username}')
    
    def test_ai_chat_ordering(self):
        """Test that AI chats are ordered by updated_at descending"""
        ai_chat1 = AIChat.objects.create(user=self.user, title='Chat 1')
        ai_chat2 = AIChat.objects.create(user=self.user, title='Chat 2')
        
        chats = AIChat.objects.all()
        self.assertEqual(chats[0], ai_chat2)  # Most recent first
        self.assertEqual(chats[1], ai_chat1)


class AIMessageModelTest(TestCase):
    """Unit tests for AIMessage model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.ai_chat = AIChat.objects.create(
            user=self.user,
            title='Test AI Chat'
        )
    
    def test_create_user_message(self):
        """Test creating a user message"""
        message = AIMessage.objects.create(
            ai_chat=self.ai_chat,
            role='user',
            content='Hello AI!'
        )
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Hello AI!')
        self.assertIsNone(message.prompt_tokens)
    
    def test_create_assistant_message_with_tokens(self):
        """Test creating an assistant message with token tracking"""
        message = AIMessage.objects.create(
            ai_chat=self.ai_chat,
            role='assistant',
            content='Hello! How can I help?',
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        self.assertEqual(message.role, 'assistant')
        self.assertEqual(message.total_tokens, 30)
    
    def test_message_ordering(self):
        """Test that messages are ordered by timestamp"""
        msg1 = AIMessage.objects.create(
            ai_chat=self.ai_chat,
            role='user',
            content='First message'
        )
        msg2 = AIMessage.objects.create(
            ai_chat=self.ai_chat,
            role='assistant',
            content='Second message'
        )
        
        messages = self.ai_chat.messages.all()
        self.assertEqual(messages[0], msg1)
        self.assertEqual(messages[1], msg2)
    
    def test_message_string_representation(self):
        """Test AIMessage __str__ method"""
        message = AIMessage.objects.create(
            ai_chat=self.ai_chat,
            role='user',
            content='Test message'
        )
        expected = f'user in {self.ai_chat.title} at {message.timestamp}'
        self.assertEqual(str(message), expected)


# =============================================================================
# API TESTS (Integration Tests)
# =============================================================================

class AIChatAPITest(APITestCase):
    """Integration tests for AI Chat REST API endpoints"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
        
        # Create a user-to-user chat
        self.chat = Chat.objects.create(name='Test Chat')
        self.chat.participants.add(self.user1, self.user2)
        
        # Create some messages in the chat
        Message.objects.create(
            chat=self.chat,
            sender=self.user1,
            content='Hello from user1'
        )
        Message.objects.create(
            chat=self.chat,
            sender=self.user2,
            content='Hello from user2'
        )
    
    def test_list_ai_chats(self):
        """Test listing AI chats for authenticated user"""
        AIChat.objects.create(user=self.user1, title='Chat 1')
        AIChat.objects.create(user=self.user1, title='Chat 2')
        AIChat.objects.create(user=self.user2, title='Chat 3')  # Different user
        
        response = self.client.get('/api/ai/chats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only user1's chats
    
    def test_create_ai_chat_without_related_chat(self):
        """Test creating an AI chat without related chat"""
        data = {
            'title': 'New AI Chat',
            'system_prompt': 'You are helpful.'
        }
        response = self.client.post('/api/ai/chats/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New AI Chat')
        self.assertIn('id', response.data)
        # Verify the chat was created for the correct user
        ai_chat = AIChat.objects.get(id=response.data['id'])
        self.assertEqual(ai_chat.user, self.user1)
    
    def test_create_ai_chat_with_related_chat(self):
        """Test creating an AI chat with related chat"""
        data = {
            'title': 'AI Chat with Context',
            'system_prompt': 'You help with discussions.',
            'related_chat': self.chat.id
        }
        response = self.client.post('/api/ai/chats/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['related_chat'], self.chat.id)
    
    def test_create_ai_chat_with_invalid_related_chat(self):
        """Test creating AI chat with a chat user doesn't participate in"""
        other_chat = Chat.objects.create(name='Other Chat')
        other_chat.participants.add(self.user2)  # user1 is NOT a participant
        
        data = {
            'title': 'AI Chat',
            'related_chat': other_chat.id
        }
        response = self.client.post('/api/ai/chats/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_ai_chat(self):
        """Test retrieving a specific AI chat"""
        ai_chat = AIChat.objects.create(user=self.user1, title='Test Chat')
        AIMessage.objects.create(
            ai_chat=ai_chat,
            role='user',
            content='Hello'
        )
        
        response = self.client.get(f'/api/ai/chats/{ai_chat.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Chat')
        self.assertEqual(len(response.data['messages']), 1)
    
    def test_cannot_retrieve_other_users_chat(self):
        """Test that users cannot access other users' AI chats"""
        ai_chat = AIChat.objects.create(user=self.user2, title='User2 Chat')
        
        response = self.client.get(f'/api/ai/chats/{ai_chat.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_ai_chat(self):
        """Test deleting an AI chat"""
        ai_chat = AIChat.objects.create(user=self.user1, title='To Delete')
        
        response = self.client.delete(f'/api/ai/chats/{ai_chat.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AIChat.objects.filter(id=ai_chat.id).exists())
    
    def test_get_messages(self):
        """Test getting messages for an AI chat"""
        ai_chat = AIChat.objects.create(user=self.user1, title='Test Chat')
        AIMessage.objects.create(ai_chat=ai_chat, role='user', content='Message 1')
        AIMessage.objects.create(ai_chat=ai_chat, role='assistant', content='Message 2')
        
        response = self.client.get(f'/api/ai/chats/{ai_chat.id}/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_related_chat_context(self):
        """Test getting context from related chat"""
        ai_chat = AIChat.objects.create(
            user=self.user1,
            title='Test Chat',
            related_chat=self.chat
        )
        
        response = self.client.get(f'/api/ai/chats/{ai_chat.id}/related_chat_context/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['chat_name'], 'Test Chat')
        self.assertEqual(response.data['message_count'], 2)
        self.assertEqual(len(response.data['messages']), 2)
    
    def test_get_related_chat_context_without_related_chat(self):
        """Test getting context when no related chat is linked"""
        ai_chat = AIChat.objects.create(user=self.user1, title='Test Chat')
        
        response = self.client.get(f'/api/ai/chats/{ai_chat.id}/related_chat_context/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('ai_chat.views.OpenAI')
    def test_send_message_to_chatgpt(self, mock_openai):
        """Test sending a message to ChatGPT"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='AI response'))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        ai_chat = AIChat.objects.create(user=self.user1, title='Test Chat')
        
        data = {
            'content': 'Hello AI',
            'include_related_chat_context': False
        }
        response = self.client.post(f'/api/ai/chats/{ai_chat.id}/send_message/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'assistant')
        self.assertEqual(response.data['content'], 'AI response')
        self.assertEqual(response.data['total_tokens'], 30)
        
        # Verify messages were created
        self.assertEqual(ai_chat.messages.count(), 2)  # User message + assistant response
    
    @patch('ai_chat.views.OpenAI')
    def test_send_message_with_related_chat_context(self, mock_openai):
        """Test sending a message with related chat context"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='Context-aware response'))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=30, total_tokens=80)
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        ai_chat = AIChat.objects.create(
            user=self.user1,
            title='Test Chat',
            related_chat=self.chat
        )
        
        data = {
            'content': 'Summarize our chat',
            'include_related_chat_context': True,
            'context_message_limit': 10
        }
        response = self.client.post(f'/api/ai/chats/{ai_chat.id}/send_message/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Context-aware response')
        
        # Verify the OpenAI API was called with context
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        # System message should contain context from related chat
        system_message = messages[0]
        self.assertIn('Context from related chat:', system_message['content'])
    
    def test_send_message_empty_content(self):
        """Test sending an empty message"""
        ai_chat = AIChat.objects.create(user=self.user1, title='Test Chat')
        
        data = {'content': ''}
        response = self.client.post(f'/api/ai/chats/{ai_chat.id}/send_message/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access endpoints"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/ai/chats/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AIMessageAPITest(APITestCase):
    """Integration tests for AI Message endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.ai_chat = AIChat.objects.create(user=self.user, title='Test Chat')
    
    def test_list_ai_messages(self):
        """Test listing AI messages"""
        AIMessage.objects.create(ai_chat=self.ai_chat, role='user', content='Msg 1')
        AIMessage.objects.create(ai_chat=self.ai_chat, role='assistant', content='Msg 2')
        
        response = self.client.get('/api/ai/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_ai_message(self):
        """Test retrieving a specific AI message"""
        message = AIMessage.objects.create(
            ai_chat=self.ai_chat,
            role='user',
            content='Test message'
        )
        
        response = self.client.get(f'/api/ai/messages/{message.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test message')


# =============================================================================
# WEBSOCKET TESTS (Integration Tests)
# =============================================================================

class AIChatWebSocketTest(TransactionTestCase):
    """Integration tests for AI Chat WebSocket consumer"""
    
    def setUp(self):
        """Setup for WebSocket tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.ai_chat = AIChat.objects.create(
            user=self.user,
            title='WebSocket Test Chat'
        )
    
    async def test_websocket_connect_authenticated(self):
        """Test WebSocket connection with authenticated user"""
        communicator = WebsocketCommunicator(
            AIChatConsumer.as_asgi(),
            f'/ws/ai-chat/{self.ai_chat.id}/'
        )
        communicator.scope['user'] = self.user
        communicator.scope['url_route'] = {'kwargs': {'ai_chat_id': str(self.ai_chat.id)}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        await communicator.disconnect()
    
    async def test_websocket_connect_unauthenticated(self):
        """Test WebSocket connection without authentication"""
        from django.contrib.auth.models import AnonymousUser
        
        communicator = WebsocketCommunicator(
            AIChatConsumer.as_asgi(),
            f'/ws/ai-chat/{self.ai_chat.id}/'
        )
        communicator.scope['user'] = AnonymousUser()
        communicator.scope['url_route'] = {'kwargs': {'ai_chat_id': str(self.ai_chat.id)}}
        
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
    
    @patch('ai_chat.consumers.OpenAI')
    async def test_websocket_send_message(self, mock_openai):
        """Test sending a message through WebSocket"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='WebSocket AI response'))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        communicator = WebsocketCommunicator(
            AIChatConsumer.as_asgi(),
            f'/ws/ai-chat/{self.ai_chat.id}/'
        )
        communicator.scope['user'] = self.user
        communicator.scope['url_route'] = {'kwargs': {'ai_chat_id': str(self.ai_chat.id)}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send a message
        await communicator.send_json_to({
            'type': 'message',
            'content': 'Hello via WebSocket',
            'include_related_chat_context': False
        })
        
        # Receive user message echo
        response1 = await communicator.receive_json_from()
        self.assertEqual(response1['type'], 'user_message')
        self.assertEqual(response1['message']['content'], 'Hello via WebSocket')
        
        # Receive assistant response
        response2 = await communicator.receive_json_from()
        self.assertEqual(response2['type'], 'assistant_message')
        self.assertEqual(response2['message']['content'], 'WebSocket AI response')
        
        await communicator.disconnect()
    
    async def test_websocket_send_empty_message(self):
        """Test sending an empty message through WebSocket"""
        communicator = WebsocketCommunicator(
            AIChatConsumer.as_asgi(),
            f'/ws/ai-chat/{self.ai_chat.id}/'
        )
        communicator.scope['user'] = self.user
        communicator.scope['url_route'] = {'kwargs': {'ai_chat_id': str(self.ai_chat.id)}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send empty message
        await communicator.send_json_to({
            'type': 'message',
            'content': '',
        })
        
        # Should receive error
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        
        await communicator.disconnect()
    
    async def test_websocket_invalid_json(self):
        """Test sending invalid JSON through WebSocket"""
        communicator = WebsocketCommunicator(
            AIChatConsumer.as_asgi(),
            f'/ws/ai-chat/{self.ai_chat.id}/'
        )
        communicator.scope['user'] = self.user
        communicator.scope['url_route'] = {'kwargs': {'ai_chat_id': str(self.ai_chat.id)}}
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send invalid data
        await communicator.send_to(text_data='invalid json')
        
        # Should receive error
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        
        await communicator.disconnect()
