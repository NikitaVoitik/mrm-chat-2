from django.contrib import admin
from .models import AIChat, AIMessage


@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'related_chat', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ['ai_chat', 'role', 'content_preview', 'timestamp', 'total_tokens']
    list_filter = ['role', 'timestamp']
    search_fields = ['content', 'ai_chat__title']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        """Show first 50 characters of content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
