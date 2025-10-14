from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Chat, Message
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    ChatSerializer, MessageSerializer
)


@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='Create a new user account with username, email, password, and user type.',
    request=UserRegistrationSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiResponse(description='Invalid data provided'),
    },
    examples=[
        OpenApiExample(
            'Registration Example',
            value={
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'securepassword123',
                'password_confirm': 'securepassword123',
                'user_type': 'student'
            },
            request_only=True,
        ),
    ]
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='Login user',
    description='Authenticate a user and create a session.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: UserSerializer,
        401: OpenApiResponse(description='Invalid credentials'),
    },
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'username': 'john_doe',
                'password': 'securepassword123'
            },
            request_only=True,
        ),
    ]
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK
        )
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@extend_schema(
    tags=['Authentication'],
    summary='Logout user',
    description='End the current user session.',
    request=None,
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Logged out successfully'}
            }
        },
    }
)
@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    summary='Get current user',
    description='Retrieve information about the currently authenticated user.',
    responses={
        200: UserSerializer,
    }
)
@api_view(['GET'])
def current_user(request):
    return Response(UserSerializer(request.user).data)


@extend_schema_view(
    list=extend_schema(
        tags=['Chats'],
        summary='List user chats',
        description='Get all chats where the current user is a participant.',
    ),
    retrieve=extend_schema(
        tags=['Chats'],
        summary='Get chat details',
        description='Retrieve details of a specific chat including participants and messages.',
    ),
    create=extend_schema(
        tags=['Chats'],
        summary='Create a new chat',
        description='Create a new chat room with the specified participants. The creator is automatically added as a participant.',
        examples=[
            OpenApiExample(
                'Create Chat Example',
                value={
                    'name': 'Project Discussion',
                    'participant_ids': [2, 3, 4]
                },
                request_only=True,
            ),
        ]
    ),
    update=extend_schema(
        tags=['Chats'],
        summary='Update chat',
        description='Update chat details.',
    ),
    partial_update=extend_schema(
        tags=['Chats'],
        summary='Partially update chat',
        description='Partially update chat details.',
    ),
    destroy=extend_schema(
        tags=['Chats'],
        summary='Delete chat',
        description='Delete a chat room.',
    ),
)
class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return chats where the user is a participant
        return Chat.objects.filter(participants=self.request.user).distinct()

    @extend_schema(
        tags=['Chats'],
        summary='Send a message to chat',
        description='Send a message to a chat room via REST API. For real-time messaging, use WebSocket endpoint: ws://localhost:8000/ws/chat/{chat_id}/',
        request=MessageSerializer,
        responses={
            201: MessageSerializer,
            403: OpenApiResponse(description='User is not a participant in this chat'),
        },
        examples=[
            OpenApiExample(
                'Send Message Example',
                value={'content': 'Hello, everyone!'},
                request_only=True,
            ),
        ]
    )
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat = self.get_object()
        
        # Check if user is a participant
        if not chat.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not a participant in this chat'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Chats'],
        summary='Get chat messages',
        description='Retrieve all messages in a specific chat.',
        responses={
            200: MessageSerializer(many=True),
            403: OpenApiResponse(description='User is not a participant in this chat'),
        }
    )
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat = self.get_object()
        
        # Check if user is a participant
        if not chat.participants.filter(id=request.user.id).exists():
            return Response(
                {'error': 'You are not a participant in this chat'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = chat.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Messages'],
        summary='List messages',
        description='Get all messages from chats where the current user is a participant.',
    ),
    retrieve=extend_schema(
        tags=['Messages'],
        summary='Get message details',
        description='Retrieve details of a specific message.',
    ),
)
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return messages from chats where the user is a participant
        return Message.objects.filter(chat__participants=self.request.user).distinct()
