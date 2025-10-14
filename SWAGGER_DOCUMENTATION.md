# Swagger API Documentation

This document describes the Swagger/OpenAPI documentation that has been added to the MRM Chat API.

## Overview

The project now includes comprehensive API documentation using **drf-spectacular**, which automatically generates OpenAPI 3.0 schema from your Django REST Framework code.

## Accessing the Documentation

After starting the development server (`python manage.py runserver`), you can access:

### Swagger UI (Interactive Documentation)
**URL:** http://localhost:8000/api/docs/

Features:
- Browse all API endpoints organized by categories
- View detailed request/response schemas
- Test endpoints directly in the browser ("Try it out" button)
- See example requests and responses
- View authentication requirements

### ReDoc (Alternative View)
**URL:** http://localhost:8000/api/redoc/

Features:
- Clean, three-panel interface
- Search functionality
- Code samples
- Responsive design

### OpenAPI Schema (Raw JSON/YAML)
**URL:** http://localhost:8000/api/schema/

Features:
- Machine-readable API specification
- Can be imported into API clients (Postman, Insomnia, etc.)
- Used for code generation

## What's Documented

### Authentication Endpoints
- `POST /api/register/` - Register a new user
- `POST /api/login/` - Authenticate and create session
- `POST /api/logout/` - End session
- `GET /api/me/` - Get current user information

### Chat Management Endpoints
- `GET /api/chats/` - List user's chats
- `POST /api/chats/` - Create new chat
- `GET /api/chats/{id}/` - Get chat details
- `PUT /api/chats/{id}/` - Update chat
- `PATCH /api/chats/{id}/` - Partially update chat
- `DELETE /api/chats/{id}/` - Delete chat
- `GET /api/chats/{id}/messages/` - Get chat messages
- `POST /api/chats/{id}/send_message/` - Send message (REST API)

### Message Endpoints
- `GET /api/messages/` - List messages
- `GET /api/messages/{id}/` - Get message details

### WebSocket Documentation
While WebSocket connections can't be tested directly in Swagger UI, the documentation includes:
- WebSocket endpoint URL format: `ws://localhost:8000/ws/chat/{chat_id}/`
- Connection requirements
- Message format
- Authentication requirements
- Links to detailed WebSocket guide

## Features

### Request Examples
Each endpoint includes example request bodies showing:
- Required fields
- Optional fields
- Expected data types
- Sample values

### Response Schemas
Complete response documentation including:
- Success responses with status codes
- Error responses
- Response body structure
- Field descriptions

### Authentication
The documentation clearly indicates:
- Which endpoints require authentication (🔒 icon)
- Which endpoints are public (🔓 icon)
- Authentication method (Session-based)

### Field Descriptions
All model fields include helpful descriptions:
- User types (owner, student, staff)
- Chat participant management
- Message content requirements

## Configuration

The Swagger UI is configured in `myproject/settings.py`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'MRM Chat API',
    'DESCRIPTION': 'A multi-person chat backend...',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication endpoints'},
        {'name': 'Chats', 'description': 'Chat management endpoints'},
        {'name': 'Messages', 'description': 'Message endpoints'},
        {'name': 'WebSockets', 'description': 'WebSocket endpoints for real-time messaging'},
    ],
}
```

## Testing Endpoints

To test an endpoint in Swagger UI:

1. Navigate to http://localhost:8000/api/docs/
2. Click on an endpoint to expand it
3. Click the "Try it out" button
4. Fill in required parameters/request body
5. Click "Execute"
6. View the response below

**Note:** For authenticated endpoints, you must first login via `/api/login/` to create a session.

## Integration with External Tools

The OpenAPI schema can be:
- Imported into Postman or Insomnia for API testing
- Used with code generators (e.g., openapi-generator)
- Integrated with CI/CD pipelines for API validation
- Used for contract testing

## Additional Resources

- [DRF Spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [WEBSOCKET_GUIDE.md](WEBSOCKET_GUIDE.md) - Detailed WebSocket usage
- [API_EXAMPLES.md](API_EXAMPLES.md) - REST API examples
