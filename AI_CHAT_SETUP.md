# AI Chat Setup Guide

## Overview
A new Django app `ai_chat` has been created to provide one-on-one ChatGPT conversations with optional context from existing user-to-user chats.

## What Was Created

### 1. Django App Structure
```
ai_chat/
├── __init__.py
├── admin.py              # Admin interface configuration
├── apps.py               # App configuration
├── consumers.py          # WebSocket consumer for real-time chat
├── models.py             # AIChat and AIMessage models
├── routing.py            # WebSocket URL routing
├── serializers.py        # DRF serializers
├── urls.py               # REST API URL patterns
├── views.py              # ViewSets for API endpoints
├── migrations/           # Database migrations
│   └── 0001_initial.py
├── README.md             # Comprehensive documentation
└── ai_websocket_test.html # WebSocket testing interface
```

### 2. Models

#### AIChat
- Links a user to a ChatGPT conversation
- Optional `related_chat` field to reference user-to-user chats
- Customizable `system_prompt` for AI behavior
- Tracks creation and update timestamps

#### AIMessage
- Stores individual messages (user, assistant, or system)
- Tracks token usage for cost monitoring
- Ordered by timestamp

### 3. API Endpoints

**Base URL**: `/api/ai/`

**REST Endpoints**:
- `GET /api/ai/chats/` - List AI chats
- `POST /api/ai/chats/` - Create AI chat
- `GET /api/ai/chats/{id}/` - Get AI chat
- `DELETE /api/ai/chats/{id}/` - Delete AI chat
- `POST /api/ai/chats/{id}/send_message/` - Send message to ChatGPT
- `GET /api/ai/chats/{id}/messages/` - Get messages
- `GET /api/ai/chats/{id}/related_chat_context/` - Get related chat context

**WebSocket**:
- `ws://localhost:8000/ws/ai-chat/{ai_chat_id}/` - Real-time AI chat

### 4. Key Features

✅ **One-on-One AI Conversations**: Private chats with ChatGPT  
✅ **Context-Aware**: Include history from related user-to-user chats  
✅ **Real-time**: WebSocket support for instant responses  
✅ **REST API**: Full CRUD operations  
✅ **Token Tracking**: Monitor API usage and costs  
✅ **Custom Prompts**: Customize AI behavior per conversation  
✅ **Admin Interface**: Manage chats and messages via Django admin  
✅ **API Documentation**: Integrated with Swagger UI  

## Setup Instructions

### 1. Install Dependencies

The OpenAI package has already been installed. To update requirements.txt:

```bash
source .venv/bin/activate
uv pip compile pyproject.toml -o requirements.txt
```

### 2. Run Migrations

```bash
source .venv/bin/activate
python manage.py migrate
```

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

**Get your API key**: https://platform.openai.com/api-keys

### 4. Start the Server

```bash
source .venv/bin/activate
python manage.py runserver
```

## Usage Examples

### Create an AI Chat (REST API)

```bash
curl -X POST http://localhost:8000/api/ai/chats/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "title": "My AI Assistant",
    "system_prompt": "You are a helpful coding assistant."
  }'
```

### Create AI Chat Linked to User Chat

```bash
curl -X POST http://localhost:8000/api/ai/chats/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "title": "Project Discussion Helper",
    "system_prompt": "You help analyze project discussions.",
    "related_chat": 1
  }'
```

### Send Message with Context

```bash
curl -X POST http://localhost:8000/api/ai/chats/1/send_message/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "content": "Summarize our previous discussion",
    "include_related_chat_context": true,
    "context_message_limit": 20
  }'
```

### WebSocket Connection

Open `ai_chat/ai_websocket_test.html` in your browser or use JavaScript:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ai-chat/1/');

ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'message',
        content: 'Hello ChatGPT!',
        include_related_chat_context: false
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

## Testing

### 1. REST API Testing
- Navigate to http://localhost:8000/api/docs/
- Look for "AI Chat" and "AI Messages" sections
- Test endpoints interactively

### 2. WebSocket Testing
- Open `ai_chat/ai_websocket_test.html` in browser
- Enter AI Chat ID
- Click "Connect"
- Send messages and see real-time responses

### 3. Admin Interface
- Navigate to http://localhost:8000/admin/
- View "AI Chats" and "AI Messages" sections
- Monitor conversations and token usage

## Integration with Existing Chats

The AI chat system integrates with your existing `chat` app:

1. **Link Chats**: Set `related_chat` when creating an AI chat
2. **Validation**: System ensures user is a participant in the related chat
3. **Context Injection**: Related chat messages are included in AI prompts
4. **Read-Only**: AI chat reads from user chats without modifying them

## Architecture Updates

The following files were modified:

- `myproject/settings.py` - Added `ai_chat` to INSTALLED_APPS
- `myproject/urls.py` - Added `/api/ai/` URL pattern
- `myproject/asgi.py` - Added AI chat WebSocket routing
- `pyproject.toml` - Added `openai>=1.0.0` dependency
- `ARCHITECTURE.md` - Added AI Chat Integration section

## Security Notes

1. **API Key**: Never commit your OpenAI API key to version control
2. **Environment Variables**: Always use `.env` file for secrets
3. **Authentication**: All endpoints require user authentication
4. **Authorization**: Users can only access their own AI chats
5. **Validation**: Related chat links are validated for participation

## Cost Management

Monitor API costs through:

1. **Token Tracking**: Each message stores token usage
2. **Admin Interface**: Review token consumption per chat
3. **Database Queries**: Aggregate token usage for reporting

Example query:
```python
from django.db.models import Sum
from ai_chat.models import AIMessage

total = AIMessage.objects.aggregate(Sum('total_tokens'))
print(f"Total tokens used: {total['total_tokens__sum']}")
```

## Next Steps

1. **Set up OpenAI API key** in `.env` file
2. **Run migrations** to create database tables
3. **Test REST API** via Swagger UI
4. **Test WebSocket** using the provided HTML file
5. **Create your first AI chat** and start conversing!

## Documentation

- **Full Documentation**: `ai_chat/README.md`
- **Architecture**: `ARCHITECTURE.md` (AI Chat Integration section)
- **API Docs**: http://localhost:8000/api/docs/
- **WebSocket Test**: `ai_chat/ai_websocket_test.html`

## Troubleshooting

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has sufficient credits
- Ensure model name is valid (e.g., `gpt-3.5-turbo`)

### WebSocket Connection Issues
- Ensure server is running
- Check AI chat ID exists and belongs to you
- Verify you're authenticated (have valid session)

### Related Chat Context Not Working
- Verify you're a participant in the related chat
- Check `include_related_chat_context=true` in request
- Ensure related chat has messages

## Support

For issues or questions:
1. Check `ai_chat/README.md` for detailed documentation
2. Review API documentation at `/api/docs/`
3. Inspect Django admin for data verification
4. Check server logs for error messages
