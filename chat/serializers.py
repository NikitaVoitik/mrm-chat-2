from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, Message

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        help_text='Password for the new account (minimum 8 characters recommended)'
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        help_text='Confirm password (must match password field)'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'user_type']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'student')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type']
        read_only_fields = ['id']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing all users with username and names"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'chat', 'sender', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='List of user IDs to add as participants. The creator is automatically added.'
    )
    participant_usernames = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text='List of usernames to add as participants. Invalid usernames will be skipped. The creator is automatically added.'
    )

    class Meta:
        model = Chat
        fields = ['id', 'name', 'participants', 'messages', 'created_at', 'participant_ids', 'participant_usernames']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        participant_usernames = validated_data.pop('participant_usernames', [])
        chat = Chat.objects.create(**validated_data)
        
        # Add the creator to participants
        request = self.context.get('request')
        if request and request.user:
            chat.participants.add(request.user)
        
        # Add participants by IDs
        if participant_ids:
            chat.participants.add(*participant_ids)
        
        # Add participants by usernames (skip invalid ones)
        if participant_usernames:
            valid_users = User.objects.filter(username__in=participant_usernames)
            chat.participants.add(*valid_users)
        
        return chat
