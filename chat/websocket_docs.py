"""
WebSocket endpoint documentation for Swagger UI.

Since drf-spectacular doesn't automatically document WebSocket endpoints,
this module provides manual documentation that can be referenced.
"""

WEBSOCKET_DOCUMENTATION = """
## WebSocket Real-Time Messaging

### Endpoint
```
ws://localhost:8000/ws/chat/{chat_id}/
```

Replace `{chat_id}` with the actual chat ID.

### Authentication
WebSocket connections require authentication. You must:
1. First authenticate via the REST API login endpoint (`POST /api/login/`)
2. Use the session cookie when establishing the WebSocket connection

### Connecting
```javascript
// JavaScript example
const chatId = 1;
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/`);

socket.onopen = function(event) {
    console.log('WebSocket connection established');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message received:', data);
};

socket.onclose = function(event) {
    console.log('WebSocket connection closed');
};
```

### Sending Messages
Send messages as JSON objects with a `content` field:
```javascript
socket.send(JSON.stringify({
    content: 'Hello, everyone!'
}));
```

### Receiving Messages
Messages are received as JSON objects with the following structure:
```json
{
    "type": "chat_message",
    "message": {
        "id": 1,
        "chat": 1,
        "sender": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "user_type": "student"
        },
        "content": "Hello, everyone!",
        "timestamp": "2025-10-14T08:30:00Z"
    }
}
```

### Error Handling
Error messages are sent with `type: "error"`:
```json
{
    "type": "error",
    "message": "Error description"
}
```

### Access Control
- Users must be participants in the chat to connect
- WebSocket connections are authenticated using Django sessions
- Non-participants will have their connection closed immediately

### Testing
You can test WebSocket connections using:
- Browser Developer Tools (Network tab → WS filter)
- Command-line tools like `wscat`
- The test page at `/websocket_test.html`

For more details, see [WEBSOCKET_GUIDE.md](../WEBSOCKET_GUIDE.md)
"""
