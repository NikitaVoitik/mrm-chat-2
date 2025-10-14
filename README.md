# mrm-chat-2

A multi-person chat backend built with Django and Django REST Framework.

## Features

- **User Authentication**: Registration, login, and logout functionality
- **User Types**: Users can be categorized as:
  - Owner
  - Student
  - University Staff
- **Multi-person Chats**: Create chat rooms with multiple participants
- **Message History**: All messages are saved in SQLite database
- **RESTful API**: Full REST API for all chat operations

## Installation

1. Install dependencies:
```bash
pip install django djangorestframework
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
- `POST /api/chats/{id}/send_message/` - Send a message to a chat
  - Body: `{"content": "Message content"}`
- `GET /api/chats/{id}/messages/` - Get all messages in a chat

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
- **SQLite** - Database for development
- **Python 3.13** - Programming language