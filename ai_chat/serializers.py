from rest_framework import serializers
from .models import AIChat, AIMessage
from chat.models import Chat, Message


class AIMessageSerializer(serializers.ModelSerializer):
    """Serializer for AI messages"""
    
    class Meta:
        model = AIMessage
        fields = [
            'id',
            'ai_chat',
            'role',
            'content',
            'timestamp',
            'prompt_tokens',
            'completion_tokens',
            'total_tokens'
        ]
        read_only_fields = ['id', 'timestamp', 'prompt_tokens', 'completion_tokens', 'total_tokens']


class AIChatSerializer(serializers.ModelSerializer):
    """Serializer for AI chats"""
    messages = AIMessageSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    related_chat_name = serializers.CharField(source='related_chat.name', read_only=True, allow_null=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AIChat
        fields = [
            'id',
            'user',
            'user_username',
            'related_chat',
            'related_chat_name',
            'title',
            'system_prompt',
            'created_at',
            'updated_at',
            'messages',
            'message_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        """Get the total number of messages in this AI chat"""
        return obj.messages.count()


class AIChatCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AI chats"""
    
    class Meta:
        model = AIChat
        fields = ['id', 'title', 'system_prompt', 'related_chat']
        read_only_fields = ['id']
    
    def validate_related_chat(self, value):
        """Ensure the user is a participant in the related chat"""
        if value:
            user = self.context['request'].user
            if not value.participants.filter(id=user.id).exists():
                raise serializers.ValidationError(
                    "You must be a participant in the related chat."
                )
        return value


class RelatedChatContextSerializer(serializers.Serializer):
    """Serializer for fetching related chat context"""
    message_limit = serializers.IntegerField(
        default=50,
        min_value=1,
        max_value=200,
        help_text='Number of recent messages to include from the related chat'
    )


class SendAIMessageSerializer(serializers.Serializer):
    """Serializer for sending a message to ChatGPT"""
    content = serializers.CharField(
        help_text='Message content to send to ChatGPT'
    )
    include_related_chat_context = serializers.BooleanField(
        default=False,
        help_text='Whether to include related chat history as context'
    )
    context_message_limit = serializers.IntegerField(
        default=20,
        min_value=1,
        max_value=100,
        help_text='Number of recent messages from related chat to include'
    )
