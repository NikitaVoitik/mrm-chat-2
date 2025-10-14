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

### 4. Get list of all users

```bash
curl -X GET http://localhost:8000/api/users/ \
  -b cookies.txt
```

Response:
```json
[
  {
    "username": "alice",
    "first_name": "Alice",
    "last_name": "Smith"
  },
  {
    "username": "bob",
    "first_name": "Bob",
    "last_name": "Johnson"
  }
]
```

## Chat Operations

### 5. Create a chat with user IDs

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

### 6. Create a chat with usernames

```bash
curl -X POST http://localhost:8000/api/chats/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Team Meeting",
    "participant_usernames": ["bob", "charlie", "invalid_user"]
  }'
```

**Note**: Invalid usernames (like "invalid_user") are automatically skipped. The chat will be created successfully with only the valid users.

Response:
```json
{
  "id": 2,
  "name": "Team Meeting",
  "participants": [
    {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "user_type": "student"
    },
    {
      "id": 2,
      "username": "bob",
      "email": "bob@example.com",
      "user_type": "staff"
    },
    {
      "id": 3,
      "username": "charlie",
      "email": "charlie@example.com",
      "user_type": "owner"
    }
  ],
  "messages": [],
  "created_at": "2025-10-14T07:01:00Z"
}
```

### 7. Create a chat with both IDs and usernames

```bash
curl -X POST http://localhost:8000/api/chats/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Mixed Participants",
    "participant_ids": [2],
    "participant_usernames": ["charlie"]
  }'
```

### 8. List all chats

```bash
curl -X GET http://localhost:8000/api/chats/ \
  -b cookies.txt
```

### 9. Send a message

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

### 10. Get chat messages

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

### 11. Logout

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

## Additional Features

### Creating Chats with Usernames vs IDs

You have three options when creating chats:

1. **Using participant_ids**: Traditional method with user IDs
   ```json
   {"name": "Chat", "participant_ids": [2, 3, 4]}
   ```

2. **Using participant_usernames**: New method with usernames (invalid usernames are skipped)
   ```json
   {"name": "Chat", "participant_usernames": ["alice", "bob", "invalid_user"]}
   ```

3. **Using both**: Combine both methods
   ```json
   {"name": "Chat", "participant_ids": [2], "participant_usernames": ["charlie"]}
   ```

The creator is automatically added as a participant in all cases.

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
