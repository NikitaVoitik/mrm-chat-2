import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from openai import OpenAI

from .models import AIChat, AIMessage
from chat.models import Message


class AIChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time AI chat with ChatGPT.
    Handles user messages and streams responses from ChatGPT.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.ai_chat_id = self.scope['url_route']['kwargs']['ai_chat_id']
        self.room_group_name = f'ai_chat_{self.ai_chat_id}'
        self.user = self.scope['user']
        
        # Check authentication
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user owns this AI chat
        if not await self.check_ownership():
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_user_message(data)
            elif message_type == 'typing':
                # Optionally handle typing indicators
                pass
                
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
    
    async def handle_user_message(self, data):
        """Process user message and get ChatGPT response"""
        content = data.get('content', '').strip()
        include_context = data.get('include_related_chat_context', False)
        context_limit = data.get('context_message_limit', 20)
        
        if not content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content cannot be empty'
            }))
            return
        
        # Save user message
        user_message = await self.save_message('user', content)
        
        # Send user message to client
        await self.send(text_data=json.dumps({
            'type': 'user_message',
            'message': {
                'id': user_message.id,
                'role': 'user',
                'content': content,
                'timestamp': user_message.timestamp.isoformat()
            }
        }))
        
        # Get ChatGPT response
        try:
            assistant_content, usage = await self.get_chatgpt_response(
                include_context,
                context_limit
            )
            
            # Save assistant message
            assistant_message = await self.save_message(
                'assistant',
                assistant_content,
                prompt_tokens=usage.get('prompt_tokens'),
                completion_tokens=usage.get('completion_tokens'),
                total_tokens=usage.get('total_tokens')
            )
            
            # Send assistant message to client
            await self.send(text_data=json.dumps({
                'type': 'assistant_message',
                'message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': assistant_content,
                    'timestamp': assistant_message.timestamp.isoformat(),
                    'usage': usage
                }
            }))
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to get ChatGPT response: {str(e)}'
            }))
    
    async def get_chatgpt_response(self, include_context, context_limit):
        """Call OpenAI API and get response"""
        # Prepare messages
        messages = await self.prepare_messages(include_context, context_limit)
        
        # Call OpenAI API (sync operation in thread pool)
        def call_openai():
            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model=os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=messages
            )
            return response
        
        # Run in thread pool to avoid blocking
        from asgiref.sync import sync_to_async
        response = await sync_to_async(call_openai)()
        
        content = response.choices[0].message.content
        usage = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
        
        return content, usage
    
    @database_sync_to_async
    def check_ownership(self):
        """Check if the user owns this AI chat"""
        try:
            ai_chat = AIChat.objects.get(id=self.ai_chat_id)
            return ai_chat.user == self.user
        except AIChat.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, role, content, prompt_tokens=None, completion_tokens=None, total_tokens=None):
        """Save a message to the database"""
        ai_chat = AIChat.objects.get(id=self.ai_chat_id)
        message = AIMessage.objects.create(
            ai_chat=ai_chat,
            role=role,
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
        return message
    
    @database_sync_to_async
    def prepare_messages(self, include_context, context_limit):
        """Prepare messages for OpenAI API"""
        ai_chat = AIChat.objects.get(id=self.ai_chat_id)
        messages = []
        
        # Add system prompt
        system_content = ai_chat.system_prompt
        
        # Optionally add related chat context
        if include_context and ai_chat.related_chat:
            related_messages = Message.objects.filter(
                chat=ai_chat.related_chat
            ).select_related('sender').order_by('-timestamp')[:context_limit]
            
            if related_messages:
                context_text = "\n\nContext from related chat:\n"
                for msg in reversed(related_messages):
                    context_text += f"{msg.sender.username}: {msg.content}\n"
                system_content += context_text
        
        messages.append({
            'role': 'system',
            'content': system_content
        })
        
        # Add conversation history
        ai_messages = AIMessage.objects.filter(ai_chat=ai_chat).order_by('timestamp')
        for msg in ai_messages:
            if msg.role in ['user', 'assistant']:
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
        
        return messages
