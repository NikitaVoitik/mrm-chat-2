# WebSocket Usage Guide

This document provides examples of how to use WebSocket connections for real-time messaging in the chat application.

## Overview

The chat application now supports real-time messaging through WebSockets. Messages sent via WebSocket are:
- Saved to the database automatically
- Broadcast to all participants in the chat room in real-time
- Available via REST API for message history retrieval

**Note:** The existing REST API endpoints remain functional for backward compatibility.

## WebSocket Connection

### Endpoint Format
```
ws://localhost:8000/ws/chat/{chat_id}/
```

Replace `{chat_id}` with the actual chat ID.

### Authentication

WebSocket connections require authentication. You must:
1. First authenticate via the REST API login endpoint
2. Use the session cookie when establishing the WebSocket connection

### Example: Connecting to a Chat Room

#### Using JavaScript (Browser)
```javascript
// First, authenticate via REST API (see API_EXAMPLES.md)
// Then connect to WebSocket

const chatId = 1;
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/`);

socket.onopen = function(e) {
    console.log("WebSocket connection established");
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'message') {
        console.log('New message:', data.message);
        // data.message contains:
        // - id: message ID
        // - chat: chat ID
        // - sender: {id, username, email, user_type}
        // - content: message content
        // - timestamp: ISO 8601 timestamp
    } else if (data.type === 'error') {
        console.error('Error:', data.message);
    }
};

socket.onerror = function(error) {
    console.error('WebSocket error:', error);
};

socket.onclose = function(event) {
    console.log('WebSocket connection closed');
};
```

## Sending Messages

### Message Format
Send messages as JSON with the following structure:
```json
{
  "content": "Your message here"
}
```

### Example: Sending a Message

#### JavaScript
```javascript
const message = {
    content: "Hello everyone! This is a real-time message."
};

socket.send(JSON.stringify(message));
```

#### Python (using websockets library)
```python
import asyncio
import websockets
import json

async def send_message():
    uri = "ws://localhost:8000/ws/chat/1/"
    
    # Note: You need to pass authentication cookies
    async with websockets.connect(uri) as websocket:
        message = {
            "content": "Hello from Python!"
        }
        await websocket.send(json.dumps(message))
        
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(send_message())
```

## Receiving Messages

When a message is sent by any participant in the chat room, all connected clients receive it in the following format:

```json
{
  "type": "message",
  "message": {
    "id": 1,
    "chat": 1,
    "sender": {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "user_type": "student"
    },
    "content": "Hello everyone! This is a real-time message.",
    "timestamp": "2025-10-14T08:00:00Z"
  }
}
```

## Error Handling

Errors are sent in the following format:
```json
{
  "type": "error",
  "message": "Error description"
}
```

Common errors:
- **"Content cannot be empty"**: Sent when trying to send a message without content
- **"Invalid JSON"**: Sent when the message format is invalid
- **Connection closed**: User is not authenticated or not a participant in the chat

## Complete Example: Chat Application

### HTML + JavaScript Client
```html
<!DOCTYPE html>
<html>
<head>
    <title>Chat Room</title>
</head>
<body>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>

    <script>
        const chatId = 1; // Replace with actual chat ID
        const socket = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/`);
        
        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'message') {
                const msg = data.message;
                const messagesDiv = document.getElementById('messages');
                const messageElement = document.createElement('div');
                messageElement.innerHTML = `
                    <strong>${msg.sender.username}</strong> 
                    (${new Date(msg.timestamp).toLocaleString()}): 
                    ${msg.content}
                `;
                messagesDiv.appendChild(messageElement);
            } else if (data.type === 'error') {
                alert('Error: ' + data.message);
            }
        };
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const content = input.value.trim();
            
            if (content) {
                socket.send(JSON.stringify({
                    content: content
                }));
                input.value = '';
            }
        }
        
        // Send message on Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
```

## REST API Compatibility

The existing REST API endpoints remain fully functional:

### Get Message History (REST)
```bash
curl -X GET http://localhost:8000/api/chats/1/messages/ \
  -b cookies.txt
```

### Send Message (REST)
```bash
curl -X POST http://localhost:8000/api/chats/1/send_message/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"content": "Message via REST API"}'
```

**Note:** Messages sent via REST API are also stored in the database but are NOT broadcast to WebSocket clients in real-time. Use WebSockets for real-time messaging.

## Architecture Notes

### Message Flow
1. **WebSocket Message**: Client → WebSocket → Consumer → Database → All connected clients
2. **REST API Message**: Client → REST API → Database (no real-time broadcast)

### Channel Layers
The application uses an in-memory channel layer for development. For production, consider using Redis:

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## Security Considerations

1. **Authentication Required**: Users must be authenticated to connect to WebSockets
2. **Participant Verification**: Only chat participants can connect to a chat room
3. **Session-based**: Uses Django's session authentication
4. **CSRF Protection**: WebSocket connections inherit session security

## Troubleshooting

### Connection Refused
- Ensure the server is running with ASGI support (automatically enabled with daphne)
- Verify the chat ID is correct
- Check that you're authenticated

### Connection Closes Immediately
- User is not authenticated
- User is not a participant in the chat
- Invalid chat ID

### Messages Not Appearing
- Check browser console for errors
- Verify message format is correct JSON
- Ensure WebSocket connection is established (check `socket.readyState === 1`)

## Testing WebSockets

You can test WebSocket connections using:
- Browser Developer Tools (Network tab → WS filter)
- Browser extensions like "WebSocket Test Client"
- Command-line tools like `wscat`
- Python libraries like `websockets`

### Example with wscat
```bash
npm install -g wscat
wscat -c ws://localhost:8000/ws/chat/1/
```

Then type messages in JSON format:
```json
{"content": "Test message"}
```
