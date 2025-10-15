import os
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from openai import OpenAI

from .models import AIChat, AIMessage
from .serializers import (
    AIChatSerializer,
    AIChatCreateSerializer,
    AIMessageSerializer,
    SendAIMessageSerializer,
    RelatedChatContextSerializer
)
from chat.models import Message


@extend_schema_view(
    list=extend_schema(
        summary="List AI chats",
        description="Get all AI chats for the authenticated user",
        tags=['AI Chat']
    ),
    create=extend_schema(
        summary="Create AI chat",
        description="Create a new AI chat conversation",
        tags=['AI Chat']
    ),
    retrieve=extend_schema(
        summary="Get AI chat",
        description="Get a specific AI chat with all messages",
        tags=['AI Chat']
    ),
    destroy=extend_schema(
        summary="Delete AI chat",
        description="Delete an AI chat and all its messages",
        tags=['AI Chat']
    ),
)
class AIChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI chat conversations with ChatGPT.
    Users can create chats, optionally link them to existing user-to-user chats,
    and send messages to ChatGPT.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the authenticated user's AI chats"""
        return AIChat.objects.filter(user=self.request.user).prefetch_related('messages')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return AIChatCreateSerializer
        return AIChatSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating an AI chat"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        summary="Send message to ChatGPT",
        description="Send a message to ChatGPT and get a response. Optionally include related chat history as context.",
        request=SendAIMessageSerializer,
        responses={200: AIMessageSerializer},
        tags=['AI Chat']
    )
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message to ChatGPT and receive a response.
        Optionally includes related chat history as context.
        """
        ai_chat = self.get_object()
        serializer = SendAIMessageSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        content = serializer.validated_data['content']
        include_context = serializer.validated_data['include_related_chat_context']
        context_limit = serializer.validated_data['context_message_limit']
        
        # Save user message
        user_message = AIMessage.objects.create(
            ai_chat=ai_chat,
            role='user',
            content=content
        )
        
        try:
            # Prepare messages for OpenAI API
            messages = self._prepare_messages(ai_chat, include_context, context_limit)
            
            # Call OpenAI API
            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model=os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=messages
            )
            
            # Extract response
            assistant_content = response.choices[0].message.content
            usage = response.usage
            
            # Save assistant message
            assistant_message = AIMessage.objects.create(
                ai_chat=ai_chat,
                role='assistant',
                content=assistant_content,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            )
            
            return Response(
                AIMessageSerializer(assistant_message).data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get response from ChatGPT: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Get messages",
        description="Get all messages in this AI chat",
        responses={200: AIMessageSerializer(many=True)},
        tags=['AI Chat']
    )
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in this AI chat"""
        ai_chat = self.get_object()
        messages = ai_chat.messages.all()
        serializer = AIMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get related chat context",
        description="Get messages from the related user-to-user chat if one is linked",
        parameters=[
            OpenApiParameter(
                name='message_limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of recent messages to fetch',
                default=50
            )
        ],
        tags=['AI Chat']
    )
    @action(detail=True, methods=['get'])
    def related_chat_context(self, request, pk=None):
        """Get messages from the related user-to-user chat"""
        ai_chat = self.get_object()
        
        if not ai_chat.related_chat:
            return Response(
                {'error': 'No related chat linked to this AI chat'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RelatedChatContextSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        limit = serializer.validated_data['message_limit']
        
        # Get recent messages from related chat
        messages = Message.objects.filter(
            chat=ai_chat.related_chat
        ).select_related('sender').order_by('-timestamp')[:limit]
        
        # Format messages for context
        context_messages = [
            {
                'sender': msg.sender.username,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in reversed(messages)
        ]
        
        return Response({
            'chat_name': ai_chat.related_chat.name,
            'message_count': len(context_messages),
            'messages': context_messages
        })
    
    def _prepare_messages(self, ai_chat, include_context, context_limit):
        """
        Prepare messages array for OpenAI API.
        Includes system prompt, optional related chat context, and conversation history.
        """
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
        for msg in ai_chat.messages.all():
            if msg.role in ['user', 'assistant']:
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
        
        return messages


@extend_schema_view(
    list=extend_schema(
        summary="List AI messages",
        description="Get all AI messages for the authenticated user's chats",
        tags=['AI Messages']
    ),
    retrieve=extend_schema(
        summary="Get AI message",
        description="Get a specific AI message",
        tags=['AI Messages']
    ),
)
class AIMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing AI messages.
    Messages are read-only as they are created through the chat send_message action.
    """
    serializer_class = AIMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only messages from the authenticated user's AI chats"""
        return AIMessage.objects.filter(
            ai_chat__user=self.request.user
        ).select_related('ai_chat')
