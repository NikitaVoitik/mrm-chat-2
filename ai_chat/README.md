# AI Chat App - ChatGPT Integration

## Overview
The `ai_chat` app provides one-on-one chat functionality between users and ChatGPT. It can optionally reference existing user-to-user chat history to provide context-aware AI responses.

## Features

### Core Capabilities
- **One-on-One AI Conversations**: Users can create private conversations with ChatGPT
- **Context-Aware Responses**: Link AI chats to existing user-to-user chats to provide conversation context
- **Real-time Communication**: WebSocket support for instant messaging
- **REST API**: Full CRUD operations via REST endpoints
- **Token Tracking**: Monitor API usage and costs
- **Custom System Prompts**: Customize AI behavior per conversation

## Models

### AIChat
Represents a conversation between a user and ChatGPT.

**Fields:**
- `user` (FK): User who owns this AI chat
- `related_chat` (FK, optional): Link to an existing user-to-user chat for context
- `title`: Name of the conversation
- `system_prompt`: Instructions for ChatGPT behavior
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### AIMessage
Individual messages in an AI conversation.

**Fields:**
- `ai_chat` (FK): Parent AI chat
- `role`: Message sender (user, assistant, system)
- `content`: Message text
- `timestamp`: When the message was sent
- `prompt_tokens`: Tokens used in the prompt (optional)
- `completion_tokens`: Tokens used in the response (optional)
- `total_tokens`: Total tokens used (optional)

## API Endpoints

### REST API
Base URL: `/api/ai/`

#### AI Chats
- `GET /api/ai/chats/` - List all AI chats for authenticated user
- `POST /api/ai/chats/` - Create a new AI chat
- `GET /api/ai/chats/{id}/` - Get specific AI chat with messages
- `DELETE /api/ai/chats/{id}/` - Delete an AI chat
- `POST /api/ai/chats/{id}/send_message/` - Send message to ChatGPT
- `GET /api/ai/chats/{id}/messages/` - Get all messages in chat
- `GET /api/ai/chats/{id}/related_chat_context/` - Get context from related chat

#### AI Messages
- `GET /api/ai/messages/` - List all AI messages
- `GET /api/ai/messages/{id}/` - Get specific message

### WebSocket
- `ws://localhost:8000/ws/ai-chat/{ai_chat_id}/` - Real-time AI chat connection

## Usage Examples

### 1. Create an AI Chat

**Without related chat:**
```bash
curl -X POST http://localhost:8000/api/ai/chats/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "title": "General Assistant",
    "system_prompt": "You are a helpful assistant."
  }'
```

**With related chat context:**
```bash
curl -X POST http://localhost:8000/api/ai/chats/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "title": "Project Discussion Helper",
    "system_prompt": "You are an assistant helping with project discussions.",
    "related_chat": 1
  }'
```

### 2. Send Message to ChatGPT (REST)

**Simple message:**
```bash
curl -X POST http://localhost:8000/api/ai/chats/1/send_message/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "content": "Hello, how can you help me?"
  }'
```

**With related chat context:**
```bash
curl -X POST http://localhost:8000/api/ai/chats/1/send_message/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "content": "Can you summarize our previous discussion?",
    "include_related_chat_context": true,
    "context_message_limit": 20
  }'
```

### 3. WebSocket Connection

```javascript
// Connect to AI chat
const ws = new WebSocket('ws://localhost:8000/ws/ai-chat/1/');

ws.onopen = () => {
    console.log('Connected to AI chat');
    
    // Send a message
    ws.send(JSON.stringify({
        type: 'message',
        content: 'Hello ChatGPT!',
        include_related_chat_context: false
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'user_message') {
        console.log('Your message:', data.message.content);
    } else if (data.type === 'assistant_message') {
        console.log('ChatGPT:', data.message.content);
        console.log('Tokens used:', data.message.usage);
    } else if (data.type === 'error') {
        console.error('Error:', data.message);
    }
};
```

### 4. Get Related Chat Context

```bash
curl -X GET "http://localhost:8000/api/ai/chats/1/related_chat_context/?message_limit=50" \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

## Environment Variables

Add these to your `.env` file:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo, etc.
```

## How Context Works

When an AI chat is linked to a user-to-user chat:

1. **Automatic Context Injection**: When `include_related_chat_context=true`, recent messages from the related chat are included in the system prompt
2. **Configurable Limit**: Control how many messages to include (1-100)
3. **Formatted Context**: Messages are formatted as "username: content" for clarity
4. **Preserved Privacy**: Only chats where the user is a participant can be linked

## Integration with Existing Chat System

The AI chat app integrates seamlessly with the existing `chat` app:

- **Foreign Key Relationship**: `AIChat.related_chat` links to `Chat` model
- **Participant Validation**: Users can only link chats they participate in
- **Read-Only Access**: AI chat reads from user-to-user chats without modifying them
- **Independent Lifecycle**: Deleting a user-to-user chat sets `related_chat` to NULL

## Admin Interface

Both models are registered in Django admin:

- **AIChat Admin**: View/edit AI chats, filter by date, search by title/user
- **AIMessage Admin**: View messages, filter by role/date, see token usage

## Security Considerations

1. **Authentication Required**: All endpoints require authentication
2. **Ownership Validation**: Users can only access their own AI chats
3. **Participant Verification**: Related chat links are validated
4. **API Key Security**: Store OpenAI API key in environment variables
5. **Rate Limiting**: Consider implementing rate limiting for production

## Cost Management

Track API usage through:
- Token counts stored in `AIMessage` model
- Admin interface for monitoring
- Aggregate queries for cost analysis

Example query:
```python
from ai_chat.models import AIMessage
total_tokens = AIMessage.objects.aggregate(Sum('total_tokens'))
```

## Testing

Test the AI chat functionality:

```bash
# Run tests
python manage.py test ai_chat

# Test WebSocket connection
# Use the provided websocket_test.html or create a custom client
```

## API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Future Enhancements

Potential improvements:
- Streaming responses for real-time token generation
- Message editing and regeneration
- Conversation branching
- Export conversations
- Custom AI models per chat
- Image generation support
- Function calling capabilities
