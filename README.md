# mrm-chat-2

A FastAPI-based chat application API.

## Features

- RESTful API with FastAPI
- Automatic API documentation (Swagger/OpenAPI)
- CORS middleware configured
- Pydantic models for data validation
- Modular architecture with routers
- Docker support

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/NikitaVoitik/mrm-chat-2.git
cd mrm-chat-2
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional):
```bash
cp .env.example .env
```

### Running the Application

#### Using Python directly:
```bash
python main.py
```

Or using uvicorn:
```bash
uvicorn main:app --reload
```

#### Using Docker:
```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## API Endpoints

### Root Endpoints
- `GET /` - Welcome message and API information
- `GET /health` - Health check endpoint

### Messages API (v1)
- `GET /api/v1/messages/` - Get all messages
- `POST /api/v1/messages/` - Create a new message

## Project Structure

```
mrm-chat-2/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── messages.py      # Message endpoints
│   │       └── router.py        # API v1 router
│   ├── models/
│   │   ├── __init__.py
│   │   └── message.py           # Pydantic models
│   ├── __init__.py
│   └── config.py                # Application configuration
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore file
└── README.md                    # This file
```

## Development

### Adding New Endpoints

1. Create a new router file in `app/api/v1/`
2. Define your endpoints using FastAPI's routing decorators
3. Include the router in `app/api/v1/router.py`

### Adding New Models

1. Create a new model file in `app/models/`
2. Define your Pydantic models
3. Import and use them in your routers

## License

This project is licensed under the MIT License.
