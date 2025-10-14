# API Usage Examples

This document provides examples of how to use the chat API with curl commands.

## Authentication

### 1. Register a new user

```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "user_type": "student"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "user_type": "student"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "username": "alice",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "user_type": "student"
}
```

### 3. Get current user info

```bash
curl -X GET http://localhost:8000/api/me/ \
  -b cookies.txt
```

## Chat Operations

### 4. Create a chat

```bash
curl -X POST http://localhost:8000/api/chats/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Study Group",
    "participant_ids": [2, 3]
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Study Group",
  "participants": [
    {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "user_type": "student"
    }
  ],
  "messages": [],
  "created_at": "2025-10-14T07:00:00Z"
}
```

### 5. List all chats

```bash
curl -X GET http://localhost:8000/api/chats/ \
  -b cookies.txt
```

### 6. Send a message

```bash
curl -X POST http://localhost:8000/api/chats/1/send_message/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "content": "Hello everyone! Ready to study?"
  }'
```

Response:
```json
{
  "id": 1,
  "chat": 1,
  "sender": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "user_type": "student"
  },
  "content": "Hello everyone! Ready to study?",
  "timestamp": "2025-10-14T07:05:00Z"
}
```

### 7. Get chat messages

```bash
curl -X GET http://localhost:8000/api/chats/1/messages/ \
  -b cookies.txt
```

Response:
```json
[
  {
    "id": 1,
    "chat": 1,
    "sender": {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "user_type": "student"
    },
    "content": "Hello everyone! Ready to study?",
    "timestamp": "2025-10-14T07:05:00Z"
  }
]
```

### 8. Logout

```bash
curl -X POST http://localhost:8000/api/logout/ \
  -b cookies.txt
```

Response:
```json
{
  "message": "Logged out successfully"
}
```

## User Types

When registering, users can select one of three user types:

- `student` - For students
- `staff` - For university staff members
- `owner` - For owners/administrators

Example for each type:

```bash
# Register a student
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "password": "pass123", "password_confirm": "pass123", "user_type": "student"}'

# Register a staff member
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "staff1", "password": "pass123", "password_confirm": "pass123", "user_type": "staff"}'

# Register an owner
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "owner1", "password": "pass123", "password_confirm": "pass123", "user_type": "owner"}'
```

## Notes

- All authenticated endpoints require a valid session cookie (use `-b cookies.txt` with curl)
- The `-c cookies.txt` flag saves the session cookie after login
- CSRF protection is enabled, so session-based authentication is required
- All timestamps are in UTC format
