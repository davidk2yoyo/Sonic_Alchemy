# Sonic Alchemy (VoiceCanvas)

AI-powered music creation platform combining visual emotion analysis, voice transformation, and AI-generated lyrics.

## Overview

Sonic Alchemy is an innovative platform that allows users to create music through multiple creative pathways:

- **Emotion Canvas**: Draw or upload images → AI generates music based on emotional analysis
- **Voice Alchemy**: Transform anyone into a singer with AI-powered vocal processing
- **Lyric Composer**: Generate lyrics that match your melody and emotional theme

## Features

### Core Features

1. **Emotion Canvas**
   - Upload or draw images
   - AI analyzes emotional content
   - Generates music matching the emotion

2. **Voice Alchemy**
   - Record your voice (even if off-key)
   - AI corrects pitch, timing, and tone
   - Apply style transformations (jazz, rock, opera, etc.)
   - Generate harmonies automatically

3. **Lyric Composer**
   - Generate lyrics from themes
   - Match lyrics to melodies
   - AI-powered rhyme suggestions

4. **Project Management**
   - Save and load projects
   - Collaborative editing
   - Real-time synchronization

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Storage**: MinIO (S3-compatible)
- **AI**: Google Gemini API (Vision, Audio, Text)
- **Task Queue**: Celery
- **Real-time**: WebSockets

## Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/davidk2yoyo/Sonic_Alchemy.git
cd Sonic_Alchemy
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Services with Docker

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5442)
- Redis (port 6389)
- MinIO (ports 9010/9011)
- FastAPI backend (port 8010)
- React frontend (port 3010)

### 4. Set Up Backend (Local Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8010
```

### 5. Set Up Frontend (Local Development)

```bash
cd frontend
npm install
npm run dev
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Project Structure

```
Sonic_Alchemy/
├── .github/           # GitHub templates and workflows
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── docker-compose.yml # Docker services configuration
├── requirements.md    # AI-DLC requirements specification
├── design.md          # Technical design document
├── STEERING.md        # Technical constraints
└── ARCHITECTURE.md    # Architecture decisions
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `GEMINI_API_KEY` - Google Gemini API key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection URL
- `MINIO_ACCESS_KEY` - MinIO access key
- `SECRET_KEY` - JWT secret key

## API Documentation

Once the backend is running, visit:
- API docs: http://localhost:8010/docs
- ReDoc: http://localhost:8010/redoc

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[Add license information]

## Team

[Add team members and roles]

## Acknowledgments

Built for the Gemini Hackathon using AI-DLC methodology.
