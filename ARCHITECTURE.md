# MRM Chat 2 - Architecture Map

## Overview
A real-time multi-person chat backend built with Django, Django REST Framework, and Django Channels. The system supports both RESTful API and WebSocket connections for real-time messaging, including user-to-user chats and AI-powered conversations with ChatGPT.

---

## Technology Stack

### Core Framework
- **Django 5.2.7** - Web framework
- **Python 3.13** - Programming language
- **PostgreSQL** - Production database (with SQLite fallback)

### API Layer
- **Django REST Framework** - RESTful API framework
- **drf-spectacular** - OpenAPI 3 schema generation
- **drf-spectacular-sidecar** - Swagger UI and ReDoc integration

### Real-time Communication
- **Django Channels** - WebSocket support
- **Daphne** - ASGI server for handling WebSocket connections
- **In-Memory Channel Layer** - Message routing between WebSocket consumers

### Additional Tools
- **WhiteNoise** - Static file serving
- **python-dotenv** - Environment variable management
- **dj-database-url** - Database URL parsing for deployment
- **OpenAI** - ChatGPT API integration for AI-powered conversations

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  (Web Browsers, Mobile Apps, API Clients, WebSocket Clients)    │
└────────────────┬────────────────────────────┬────────────────────┘
                 │                            │
                 │ HTTP/HTTPS                 │ WebSocket (ws://)
                 │                            │
┌────────────────▼────────────────────────────▼────────────────────┐
│                      ASGI APPLICATION                             │
│                   (Daphne ASGI Server)                           │
│                                                                   │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │   HTTP Protocol Router   │  │  WebSocket Protocol      │    │
│  │   (Django WSGI App)      │  │  Router (Channels)       │    │
│  └────────────┬─────────────┘  └────────────┬─────────────┘    │
└───────────────┼──────────────────────────────┼──────────────────┘
                │                              │
                │                              │
┌───────────────▼──────────────┐  ┌───────────▼──────────────────┐
│     URL ROUTING LAYER        │  │   WEBSOCKET ROUTING          │
│   (myproject/urls.py)        │  │   (chat/routing.py)          │
│                              │  │                              │
│  /admin/        → Admin      │  │  /ws/chat/{id}/ → Consumer  │
│  /api/          → Chat URLs  │  │                              │
│  /api/schema/   → OpenAPI    │  │                              │
│  /api/docs/     → Swagger    │  │                              │
│  /api/redoc/    → ReDoc      │  │                              │
└───────────────┬──────────────┘  └───────────┬──────────────────┘
                │                              │
                │                              │
┌───────────────▼──────────────────────────────▼──────────────────┐
│                      APPLICATION LAYER                           │
│                                                                   │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │    REST API VIEWS        │  │   WEBSOCKET CONSUMERS    │    │
│  │   (chat/views.py)        │  │   (chat/consumers.py)    │    │
│  │                          │  │                          │    │
│  │  • register_user()       │  │  • ChatConsumer          │    │
│  │  • login_user()          │  │    - connect()           │    │
│  │  • logout_user()         │  │    - disconnect()        │    │
│  │  • current_user()        │  │    - receive()           │    │
│  │  • list_users()          │  │    - chat_message()      │    │
│  │  • ChatViewSet           │  │    - save_message()      │    │
│  │    - list()              │  │    - check_participant() │    │
│  │    - create()            │  │                          │    │
│  │    - retrieve()          │  │                          │    │
│  │    - send_message()      │  │                          │    │
│  │    - messages()          │  │                          │    │
│  │  • MessageViewSet        │  │                          │    │
│  │    - list()              │  │                          │    │
│  │    - retrieve()          │  │                          │    │
│  └────────────┬─────────────┘  └────────────┬─────────────┘    │
│               │                              │                   │
│               │                              │                   │
│  ┌────────────▼──────────────────────────────▼─────────────┐   │
│  │              SERIALIZERS LAYER                           │   │
│  │            (chat/serializers.py)                         │   │
│  │                                                           │   │
│  │  • UserRegistrationSerializer                            │   │
│  │  • UserSerializer                                        │   │
│  │  • UserListSerializer                                    │   │
│  │  • ChatSerializer                                        │   │
│  │  • MessageSerializer                                     │   │
│  └────────────┬──────────────────────────────────────────────┘  │
└───────────────┼──────────────────────────────────────────────────┘
                │
                │
┌───────────────▼──────────────────────────────────────────────────┐
│                      DATA LAYER                                   │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  MODELS (chat/models.py)                  │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │     User     │  │     Chat     │  │   Message    │   │   │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤   │   │
│  │  │ • username   │  │ • name       │  │ • chat (FK)  │   │   │
│  │  │ • email      │  │ • created_at │  │ • sender(FK) │   │   │
│  │  │ • password   │  │ • participants│ │ • content    │   │   │
│  │  │ • user_type  │  │   (M2M)      │  │ • timestamp  │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  └────────────┬──────────────────────────────────────────────┘  │
└───────────────┼──────────────────────────────────────────────────┘
                │
                │
┌───────────────▼──────────────────────────────────────────────────┐
│                   DATABASE (PostgreSQL)                           │
│                                                                    │
│  Tables: auth_user, chat_chat, chat_message, chat_chat_participants│
└───────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Entry Points

#### ASGI Application (`myproject/asgi.py`)
- **Purpose**: Main entry point for the ASGI server
- **Responsibilities**:
  - Protocol routing (HTTP vs WebSocket)
  - Authentication middleware for WebSockets
  - URL routing delegation

#### URL Configuration (`myproject/urls.py`)
- **Purpose**: HTTP route definitions
- **Routes**:
  - `/admin/` - Django admin interface
  - `/api/` - Chat application endpoints
  - `/api/schema/` - OpenAPI schema
  - `/api/docs/` - Swagger UI
  - `/api/redoc/` - ReDoc documentation

#### WebSocket Routing (`chat/routing.py`)
- **Purpose**: WebSocket route definitions
- **Routes**:
  - `/ws/chat/{chat_id}/` - Real-time chat connection

---

### 2. Application Layer

#### REST API Views (`chat/views.py`)

**Authentication Views** (Function-based)
- `register_user()` - User registration
- `login_user()` - Session-based authentication
- `logout_user()` - Session termination
- `current_user()` - Get authenticated user info
- `list_users()` - List all registered users

**Chat Management** (ViewSet)
- `ChatViewSet`
  - Standard CRUD operations
  - Custom actions:
    - `send_message()` - Send message via REST API
    - `messages()` - Retrieve chat messages
  - Automatic filtering by participant

**Message Management** (ViewSet)
- `MessageViewSet`
  - Read-only operations
  - Automatic filtering by chat participation

#### WebSocket Consumers (`chat/consumers.py`)

**ChatConsumer** (AsyncWebsocketConsumer)
- **Connection Lifecycle**:
  1. `connect()` - Authenticate and verify participation
  2. `receive()` - Handle incoming messages
  3. `disconnect()` - Clean up channel groups
  
- **Message Flow**:
  1. Receive JSON from client
  2. Validate and save to database
  3. Broadcast to all participants in room group
  
- **Security**:
  - Authentication check on connect
  - Participant verification
  - Error handling for invalid data

---

### 3. Data Layer

#### Models (`chat/models.py`)

**User Model** (extends AbstractUser)
```python
- username: CharField (unique)
- email: EmailField
- password: CharField (hashed)
- user_type: CharField (choices: owner, student, staff)
```

**Chat Model**
```python
- name: CharField
- participants: ManyToManyField(User)
- created_at: DateTimeField
```

**Message Model**
```python
- chat: ForeignKey(Chat)
- sender: ForeignKey(User)
- content: TextField
- timestamp: DateTimeField
```

#### Serializers (`chat/serializers.py`)
- Data validation and transformation
- Nested serialization for related objects
- Custom fields for participant management (IDs and usernames)

---

## Data Flow Diagrams

### REST API Message Flow
```
Client Request
    │
    ▼
Django URL Router
    │
    ▼
View Function/ViewSet
    │
    ├─→ Serializer (validation)
    │
    ├─→ Model (database operation)
    │
    ├─→ Serializer (response formatting)
    │
    ▼
JSON Response
```

### WebSocket Message Flow
```
WebSocket Client
    │
    ▼
ASGI Protocol Router
    │
    ▼
ChatConsumer.receive()
    │
    ├─→ Validate JSON
    │
    ├─→ save_message() → Database
    │
    ├─→ serialize_message()
    │
    ├─→ Channel Layer (group_send)
    │
    ▼
All Connected Clients in Room
```

---

## Authentication & Authorization

### Authentication Methods
1. **Session Authentication** (REST API)
   - Cookie-based sessions
   - CSRF protection enabled
   
2. **WebSocket Authentication**
   - Session passed via cookie
   - Verified in `connect()` method

### Authorization Rules
- **Public Endpoints**: Registration, Login
- **Authenticated Endpoints**: All other endpoints
- **Participant-based Access**:
  - Users can only see chats they participate in
  - Users can only send messages to chats they're in
  - WebSocket connections require participation

---

## Database Schema

### Entity Relationships
```
User ──────────┐
    │          │
    │ 1        │ M
    │          │
    │          ▼
    │    Chat_Participants (M2M)
    │          │
    │ 1        │ M
    │          │
    ▼          ▼
Message ────→ Chat
    │          
    │ M        
    │          
    └──────────
```

### Key Relationships
- **User ↔ Chat**: Many-to-Many (participants)
- **User → Message**: One-to-Many (sender)
- **Chat → Message**: One-to-Many (messages in chat)

---

## Configuration & Settings

### Django Settings (`myproject/settings.py`)

**Installed Apps**:
- `daphne` (ASGI server, must be first)
- Django core apps
- `rest_framework`
- `channels`
- `drf_spectacular`
- `chat` (custom app)

**Key Configurations**:
- `ASGI_APPLICATION`: Points to ASGI routing
- `CHANNEL_LAYERS`: In-memory channel layer for WebSockets
- `REST_FRAMEWORK`: Session auth, IsAuthenticated default
- `AUTH_USER_MODEL`: Custom User model
- `SPECTACULAR_SETTINGS`: API documentation config

**Database**:
- PostgreSQL (production via DATABASE_URL)
- Environment-based configuration
- Connection pooling enabled

---

## API Documentation

### Auto-generated Documentation
- **Swagger UI**: Interactive API testing at `/api/docs/`
- **ReDoc**: Alternative documentation at `/api/redoc/`
- **OpenAPI Schema**: Machine-readable spec at `/api/schema/`

### Documentation Features
- Request/response examples
- Schema definitions
- Authentication requirements
- WebSocket endpoint documentation
- Grouped by tags (Authentication, Chats, Messages, Users)

---

## Deployment Architecture

### Production Setup
```
Internet
    │
    ▼
Load Balancer / Reverse Proxy
    │
    ▼
Daphne ASGI Server
    │
    ├─→ HTTP Requests → Django
    │
    └─→ WebSocket Connections → Channels
    │
    ▼
PostgreSQL Database
```

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Individual DB config
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode toggle

### Static Files
- **WhiteNoise**: Serves static files in production
- **Compressed Manifest Storage**: Optimized static file serving
- **STATIC_ROOT**: `/staticfiles/`

---

## Security Features

### Built-in Security
- **CSRF Protection**: Enabled for all state-changing operations
- **Password Hashing**: Django's default PBKDF2 algorithm
- **SQL Injection Protection**: Django ORM parameterized queries
- **XSS Protection**: Template auto-escaping

### Custom Security
- **Participant Verification**: Users can only access their chats
- **WebSocket Authentication**: Required for all connections
- **Session Management**: Secure cookie-based sessions

### Trusted Origins
- Configured for localhost and production domain
- CORS-like protection for CSRF

---

## Testing & Development

### Management Commands
- `python manage.py test_chat` - Run custom test suite
- `python manage.py migrate` - Apply database migrations
- `python manage.py runserver` - Start development server

### Test Resources
- `websocket_test.html` - WebSocket testing interface
- Interactive Swagger UI for API testing

---

## Extension Points

### Adding New Features

1. **New Models**: Add to `chat/models.py`
2. **New API Endpoints**: 
   - Add views to `chat/views.py`
   - Register URLs in `chat/urls.py`
3. **New WebSocket Events**:
   - Extend `ChatConsumer` in `chat/consumers.py`
4. **New Serializers**: Add to `chat/serializers.py`

### Scalability Considerations

**Current Limitations**:
- In-memory channel layer (single server only)

**Production Upgrades**:
- Replace with Redis channel layer for multi-server support
- Add message queue for async tasks
- Implement database read replicas
- Add caching layer (Redis/Memcached)

---

## File Structure

```
mrm-chat-2/
├── myproject/              # Django project configuration
│   ├── __init__.py
│   ├── settings.py         # Main settings
│   ├── urls.py             # HTTP URL routing
│   ├── asgi.py             # ASGI application
│   └── wsgi.py             # WSGI application (legacy)
│
├── chat/                   # Main application
│   ├── migrations/         # Database migrations
│   ├── management/         # Custom management commands
│   │   └── commands/
│   ├── __init__.py
│   ├── models.py           # Data models
│   ├── views.py            # REST API views
│   ├── consumers.py        # WebSocket consumers
│   ├── serializers.py      # DRF serializers
│   ├── routing.py          # WebSocket routing
│   ├── urls.py             # App URL patterns
│   ├── admin.py            # Admin interface config
│   ├── apps.py             # App configuration
│   ├── tests.py            # Unit tests
│   └── websocket_docs.py   # WebSocket documentation
│
├── static/                 # Static files
├── staticfiles/            # Collected static files (production)
│
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project metadata
├── uv.lock                 # Dependency lock file
│
└── Documentation/
    ├── README.md
    ├── API_EXAMPLES.md
    ├── WEBSOCKET_GUIDE.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── MIGRATION_GUIDE.md
    ├── SWAGGER_DOCUMENTATION.md
    └── ARCHITECTURE.md     # This file
```

---

## Key Design Decisions

### 1. Dual Communication Protocols
- **REST API**: Backward compatibility, easier testing, stateless operations
- **WebSocket**: Real-time messaging, lower latency, persistent connections

### 2. Session-based Authentication
- Simpler than token-based for WebSocket
- Built-in Django support
- Suitable for web-based clients

### 3. In-Memory Channel Layer
- Sufficient for development and small deployments
- Easy setup, no external dependencies
- Upgrade path to Redis for production

### 4. Participant-based Access Control
- Fine-grained permissions
- Privacy by default
- Scalable filtering at database level

### 5. Custom User Model
- Extensible user types (owner, student, staff)
- Future-proof for additional user attributes
- Django best practice

---

## Performance Considerations

### Database Queries
- `select_related()` and `prefetch_related()` for related objects
- Filtering at database level (not in Python)
- Indexed foreign keys and many-to-many relationships

### WebSocket Efficiency
- Async consumers for non-blocking I/O
- Channel groups for efficient broadcasting
- Connection pooling for database access

### Static Files
- WhiteNoise for efficient serving
- Compressed manifest storage
- CDN-ready architecture

---

## Monitoring & Debugging

### Available Tools
- Django Admin: Database inspection
- Swagger UI: API testing and debugging
- `websocket_test.html`: WebSocket connection testing
- Django Debug Toolbar: (can be added)

### Logging Points
- Authentication failures
- WebSocket connection/disconnection
- Message send/receive events
- Database query errors

---

## Future Enhancements

### Potential Features
1. **Message Reactions**: Emoji reactions to messages
2. **File Attachments**: Upload and share files
3. **Typing Indicators**: Real-time typing status
4. **Read Receipts**: Message read tracking
5. **Push Notifications**: Mobile/desktop notifications
6. **Message Search**: Full-text search across chats
7. **User Presence**: Online/offline status
8. **Chat Moderation**: Admin controls, message deletion
9. **Rate Limiting**: Prevent spam and abuse
10. **Message Encryption**: End-to-end encryption

### Infrastructure Improvements
1. **Redis Channel Layer**: Multi-server support
2. **Celery**: Async task processing
3. **PostgreSQL Full-Text Search**: Better search performance
4. **Docker**: Containerization for deployment
5. **CI/CD Pipeline**: Automated testing and deployment
6. **Monitoring**: APM tools (Sentry, New Relic)
7. **Caching**: Redis/Memcached for frequent queries

---

## AI Chat Integration

### Overview
The `ai_chat` app provides one-on-one conversations between users and ChatGPT, with optional context from existing user-to-user chats.

### Key Features
- **One-on-One AI Conversations**: Private chats with ChatGPT
- **Context-Aware Responses**: Link to existing chats for context
- **Real-time & REST**: Both WebSocket and REST API support
- **Token Tracking**: Monitor API usage and costs
- **Custom System Prompts**: Customize AI behavior per conversation

### Data Models

#### AIChat Model
```python
- user: ForeignKey(User)
- related_chat: ForeignKey(Chat, optional)
- title: CharField
- system_prompt: TextField
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### AIMessage Model
```python
- ai_chat: ForeignKey(AIChat)
- role: CharField (user/assistant/system)
- content: TextField
- timestamp: DateTimeField
- prompt_tokens: IntegerField (optional)
- completion_tokens: IntegerField (optional)
- total_tokens: IntegerField (optional)
```

### API Endpoints

**Base URL**: `/api/ai/`

**AI Chat Management**:
- `GET /api/ai/chats/` - List user's AI chats
- `POST /api/ai/chats/` - Create new AI chat
- `GET /api/ai/chats/{id}/` - Get AI chat details
- `DELETE /api/ai/chats/{id}/` - Delete AI chat
- `POST /api/ai/chats/{id}/send_message/` - Send message to ChatGPT
- `GET /api/ai/chats/{id}/messages/` - Get chat messages
- `GET /api/ai/chats/{id}/related_chat_context/` - Get related chat context

**AI Messages**:
- `GET /api/ai/messages/` - List AI messages
- `GET /api/ai/messages/{id}/` - Get specific message

**WebSocket**:
- `ws://localhost:8000/ws/ai-chat/{ai_chat_id}/` - Real-time AI chat

### Integration with User-to-User Chats

The AI chat system integrates seamlessly with the existing chat system:

1. **Foreign Key Relationship**: `AIChat.related_chat` → `Chat`
2. **Context Injection**: Related chat messages included in AI prompts
3. **Participant Validation**: Only chats where user participates can be linked
4. **Read-Only Access**: AI reads from chats without modifying them
5. **Independent Lifecycle**: Deleting user chat sets `related_chat` to NULL

### How Context Works

When sending a message with `include_related_chat_context=true`:

1. System fetches recent messages from the related chat
2. Messages are formatted as "username: content"
3. Context is appended to the system prompt
4. ChatGPT receives full conversation history + context
5. Response is context-aware and relevant to both conversations

### Environment Configuration

Required environment variables:
```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo, etc.
```

### Security & Authorization

- **Authentication Required**: All endpoints require login
- **Ownership Validation**: Users access only their AI chats
- **Participant Verification**: Related chat links validated
- **API Key Security**: Stored in environment variables

### Cost Management

Token usage tracking enables cost monitoring:
- Tokens stored per message in database
- Admin interface for usage review
- Aggregate queries for cost analysis

### Testing Resources

- **REST API**: Test via Swagger UI at `/api/docs/`
- **WebSocket**: Use `ai_websocket_test.html` for testing
- **Documentation**: Full details in `ai_chat/README.md`

---

## Conclusion

This architecture provides a solid foundation for a real-time chat application with:
- ✅ Dual protocol support (REST + WebSocket)
- ✅ User-to-user and AI-powered conversations
- ✅ Context-aware AI responses
- ✅ Secure authentication and authorization
- ✅ Scalable data model
- ✅ Comprehensive API documentation
- ✅ Production-ready deployment configuration
- ✅ Clear extension points for future features

The modular design allows for incremental improvements while maintaining backward compatibility with existing clients.
