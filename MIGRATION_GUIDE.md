# WebSocket Migration Guide

This document explains the changes made to support WebSocket-based real-time messaging.

## What Changed

### New Features
1. **Real-time Messaging**: Messages sent via WebSocket are instantly delivered to all connected participants
2. **WebSocket Support**: Django Channels integration for bidirectional communication
3. **Backward Compatibility**: All existing REST API endpoints continue to work

### Technical Changes

#### Dependencies Added
- `channels` (4.3.1) - WebSocket support
- `channels-redis` (4.3.0) - Channel layers (for production with Redis)
- `daphne` (4.2.1) - ASGI server

#### Files Modified
- `myproject/settings.py` - Added Channels configuration
- `myproject/asgi.py` - Configured ASGI application with WebSocket routing
- `chat/serializers.py` - Fixed MessageSerializer (made `chat` field read-only)

#### Files Added
- `chat/consumers.py` - WebSocket consumer for chat rooms
- `chat/routing.py` - WebSocket URL routing
- `WEBSOCKET_GUIDE.md` - Comprehensive WebSocket usage documentation
- `websocket_test.html` - HTML test page for WebSocket functionality

## Upgrading

### For Development

1. Install new dependencies:
```bash
pip install channels daphne
```

2. The server will automatically start with ASGI/WebSocket support:
```bash
python manage.py runserver
```

### For Production

1. Install dependencies including Redis support:
```bash
pip install channels daphne channels-redis redis
```

2. Configure Redis channel layer in `settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

3. Run with Daphne:
```bash
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application
```

Or use a process manager like systemd or supervisor.

## API Changes

### Breaking Changes
**None** - All existing REST API endpoints remain functional.

### New Endpoints
- WebSocket endpoint: `ws://localhost:8000/ws/chat/{chat_id}/`

### Modified Endpoints
**None** - All REST endpoints work exactly as before.

### Serializer Fix
The `MessageSerializer` now correctly marks the `chat` field as read-only. This fixes a bug where sending messages via REST API required the chat field in the request body, even though it was being set by the view.

**Before:**
```json
// This would fail
POST /api/chats/1/send_message/
{"content": "Hello"}
```

**After:**
```json
// This now works correctly
POST /api/chats/1/send_message/
{"content": "Hello"}
```

## Usage Patterns

### REST API (Existing)
Use for:
- User authentication
- Chat creation and management
- Retrieving message history
- One-off message sending (if real-time not needed)

### WebSocket (New)
Use for:
- Real-time chat messaging
- Instant message delivery
- Live conversations
- Group chat rooms

## Example Integration

### Frontend Application
```javascript
// 1. Authenticate via REST API
const response = await fetch('/api/login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password}),
    credentials: 'include'
});

// 2. Connect to WebSocket (uses session cookie automatically)
const socket = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/`);

// 3. Handle messages
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'message') {
        displayMessage(data.message);
    }
};

// 4. Send messages
socket.send(JSON.stringify({content: 'Hello!'}));
```

## Performance Considerations

### Development
- Uses in-memory channel layer
- Suitable for single-process development
- Messages only delivered to connections on the same process

### Production
- **Recommended**: Use Redis channel layer
- Supports multiple Daphne processes
- Messages delivered across all processes
- Horizontally scalable

## Testing

### REST API
All existing tests continue to work:
```bash
python manage.py test_chat
```

### WebSocket
Use the provided `websocket_test.html` file:
1. Start the server: `python manage.py runserver`
2. Login via REST API
3. Open `websocket_test.html` in your browser
4. Change `CHAT_ID` to your chat ID
5. Test sending and receiving messages

## Troubleshooting

### WebSocket connection fails
- Ensure you're authenticated (logged in via REST API)
- Verify you're a participant in the chat
- Check the chat ID is correct

### Messages not appearing in real-time
- Verify WebSocket connection is open
- Check browser console for errors
- Ensure message format is correct JSON

### "Module not found" errors
- Install all dependencies: `pip install channels daphne`
- For production, also install: `pip install channels-redis redis`

## Support

See the comprehensive guides:
- [WEBSOCKET_GUIDE.md](WEBSOCKET_GUIDE.md) - Detailed WebSocket usage
- [API_EXAMPLES.md](API_EXAMPLES.md) - REST API examples
- [README.md](README.md) - General documentation
