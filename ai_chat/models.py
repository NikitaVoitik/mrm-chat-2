from django.db import models
from django.conf import settings


class AIChat(models.Model):
    """
    Represents a one-on-one conversation between a user and ChatGPT.
    Can optionally be linked to an existing user-to-user chat to provide context.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chats',
        help_text='User participating in this AI chat'
    )
    related_chat = models.ForeignKey(
        'chat.Chat',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_chats',
        help_text='Optional: Related user-to-user chat for context'
    )
    title = models.CharField(
        max_length=255,
        help_text='Title of the AI conversation'
    )
    system_prompt = models.TextField(
        default='You are a helpful assistant.',
        help_text='System prompt for ChatGPT'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class AIMessage(models.Model):
    """
    Represents a single message in an AI chat conversation.
    Can be from either the user or the AI assistant.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    ai_chat = models.ForeignKey(
        AIChat,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text='The AI chat this message belongs to'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        help_text='Role of the message sender'
    )
    content = models.TextField(help_text='Message content')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional: Store token usage for cost tracking
    prompt_tokens = models.IntegerField(null=True, blank=True)
    completion_tokens = models.IntegerField(null=True, blank=True)
    total_tokens = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role} in {self.ai_chat.title} at {self.timestamp}"
