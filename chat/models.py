from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('owner', 'Owner'),
        ('student', 'Student'),
        ('staff', 'University Staff'),
    ]
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='student',
        help_text='Type of user: owner, student, or staff'
    )

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Chat(models.Model):
    name = models.CharField(max_length=255, help_text='Name of the chat room')
    participants = models.ManyToManyField(User, related_name='chats', help_text='Users participating in this chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', help_text='The chat room this message belongs to')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', help_text='User who sent the message')
    content = models.TextField(help_text='Message content')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} in {self.chat.name} at {self.timestamp}"
