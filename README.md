# mrm-chat-2

A multi-person chat backend built with Django, Django REST Framework, and Django Channels with WebSocket support for real-time messaging.

## Features

- **User Authentication**: Registration, login, and logout functionality
- **User Types**: Users can be categorized as:
  - Owner
  - Student
  - University Staff
- **Multi-person Chats**: Create chat rooms with multiple participants
- **Real-time Messaging**: WebSocket support for instant message delivery
- **Message History**: All messages are saved in SQLite database
- **RESTful API**: Full REST API for all chat operations
- **Backward Compatible**: REST API endpoints remain functional alongside WebSocket support

## Installation

1. Install dependencies:
```bash
pip install django djangorestframework channels daphne drf-spectacular drf-spectacular-sidecar
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

4. Start the development server:
```bash
python manage.py runserver
```

The server will automatically start with ASGI/WebSocket support.

## API Documentation

Interactive API documentation is available via Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

The Swagger UI provides:
- Complete API endpoint documentation
- Interactive API testing
- Request/response examples
- Schema definitions
- WebSocket endpoint documentation

## API Endpoints

### Authentication

- `POST /api/register/` - Register a new user
  - Body: `{"username": "...", "email": "...", "password": "...", "password_confirm": "...", "user_type": "student|staff|owner"}`
  
- `POST /api/login/` - Login
  - Body: `{"username": "...", "password": "..."}`
  
- `POST /api/logout/` - Logout (requires authentication)

- `GET /api/me/` - Get current user info (requires authentication)

### Chats

- `GET /api/chats/` - List all chats for the current user
- `POST /api/chats/` - Create a new chat
  - Body: `{"name": "Chat Name", "participant_ids": [1, 2, 3]}`
- `GET /api/chats/{id}/` - Get chat details
- `POST /api/chats/{id}/send_message/` - Send a message to a chat (REST API, not real-time)
  - Body: `{"content": "Message content"}`
- `GET /api/chats/{id}/messages/` - Get all messages in a chat

### WebSocket (Real-time Messaging)

- `ws://localhost:8000/ws/chat/{chat_id}/` - Connect to a chat room for real-time messaging
  - Send: `{"content": "Your message"}`
  - Receive: `{"type": "message", "message": {...}}`

See [WEBSOCKET_GUIDE.md](WEBSOCKET_GUIDE.md) for detailed WebSocket usage examples.

### Messages

- `GET /api/messages/` - List all messages from chats the user participates in

## Database Schema

### User Model
- username (unique)
- email
- password (hashed)
- user_type (owner, student, staff)

### Chat Model
- name
- participants (many-to-many with User)
- created_at (timestamp)

### Message Model
- chat (foreign key to Chat)
- sender (foreign key to User)
- content (text)
- timestamp

## Testing

Run the test command to verify functionality:
```bash
python manage.py test_chat
```

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to manage users, chats, and messages directly.

## Technologies Used

- **Django 5.2.7** - Web framework
- **Django REST Framework** - API framework
- **drf-spectacular** - OpenAPI 3 schema generation and Swagger UI
- **Django Channels** - WebSocket support for real-time messaging
- **Daphne** - ASGI server for handling WebSocket connections
- **SQLite** - Database for development
- **Python 3.13** - Programming language

## Documentation

- [API_EXAMPLES.md](API_EXAMPLES.md) - REST API usage examples
- [WEBSOCKET_GUIDE.md](WEBSOCKET_GUIDE.md) - WebSocket real-time messaging guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details

Note: Access the interactive Swagger UI documentation at http://localhost:8000/api/docs/ for a complete, interactive API reference with examples and the ability to test endpoints directly in your browser.
