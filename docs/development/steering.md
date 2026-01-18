# Steering File - Technical Constraints

This document defines immutable technical constraints that govern all development decisions in the Sonic Alchemy project. These constraints act as contracts between human intent and machine execution.

## Language and Code Standards

- **All code and comments must be in English**
- **All documentation must be in English**
- Code style: Follow PEP 8 for Python, ESLint/Prettier for TypeScript
- Maximum line length: 127 characters (Python), 100 characters (TypeScript)

## Port Configuration

All ports are configured +10 from defaults to avoid conflicts with other projects:

- **PostgreSQL**: External port `5442` (internal: `5432`)
- **Redis**: External port `6389` (internal: `6379`)
- **MinIO API**: External port `9010` (internal: `9000`)
- **MinIO Console**: External port `9011` (internal: `9001`)
- **FastAPI Backend**: External port `8010` (internal: `8000`)
- **React Frontend**: External port `3010` (internal: `3000`)

## Architecture Constraints

- **Backend**: Monolithic modular FastAPI application
- **Worker**: Separate Celery worker for async processing
- **Database**: PostgreSQL only (no NoSQL databases)
- **Cache/Queue**: Redis for both caching and message broker
- **Storage**: MinIO (S3-compatible) for audio and image files
- **API Versioning**: Use `/api/v1` prefix for all API endpoints

## AI/ML Constraints

- **AI Provider**: Google Gemini API only
- **Models**: Use Gemini multimodal capabilities (Vision, Audio, Text)
- **No external AI services**: Do not integrate other AI providers
- **Rate Limiting**: Implement rate limiting for Gemini API calls
- **Caching**: Cache Gemini API responses when appropriate

## Target Audience

- **Primary**: Amateur musicians (non-professional users)
- **Focus**: Accessibility and ease of use over professional features
- **User Experience**: Intuitive, guided workflows for non-technical users

## Technology Stack Restrictions

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Task Queue**: Celery with Redis broker
- **Authentication**: JWT tokens
- **File Processing**: librosa, pydub for audio

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **Build Tool**: Vite
- **State Management**: React Hooks (Context API or Zustand)
- **HTTP Client**: Axios
- **WebSocket**: Native WebSocket API or Socket.IO client

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Object Storage**: MinIO (S3-compatible)

## Security Constraints

- **Authentication**: JWT-based authentication required
- **Password Hashing**: Use bcrypt or argon2
- **Secrets**: Never commit secrets to repository
- **Environment Variables**: All sensitive data in `.env` file
- **CORS**: Configure CORS for frontend origin only
- **File Upload**: Validate file types and sizes

## Performance Constraints

- **Async Processing**: Heavy operations (audio processing, AI calls) must use Celery
- **Response Time**: API endpoints should respond within 2 seconds for synchronous operations
- **File Size Limits**: 
  - Images: Maximum 10MB
  - Audio: Maximum 50MB
- **Concurrent Users**: Support at least 50 concurrent users

## Data Constraints

- **Database**: Use PostgreSQL for all persistent data
- **File Storage**: All user-uploaded files in MinIO
- **Temporary Files**: Clean up temporary files after processing
- **Data Retention**: Define retention policy for user projects

## Development Constraints

- **Virtual Environment**: Use Python venv for local development
- **Docker**: All services must be containerizable
- **Environment Variables**: Use `.env` file for configuration
- **Git Workflow**: Follow Git Flow branching strategy
- **Code Reviews**: All code must be reviewed before merging to `develop`

## Testing Constraints

- **Test Coverage**: Aim for 70%+ coverage for critical paths
- **Test Types**: Unit tests, integration tests, API tests
- **CI/CD**: All tests must pass before merging

## Documentation Constraints

- **API Documentation**: Auto-generated from FastAPI (OpenAPI/Swagger)
- **Code Comments**: Document complex logic and algorithms
- **README**: Must include setup instructions
- **CONTRIBUTING**: Must include development workflow

## Compliance

- **AI-DLC Methodology**: Follow AI-DLC phases (Inception, Construction, Operations)
- **Spec-Driven**: No code without approved Specs
- **Steering Files**: These constraints are immutable unless explicitly changed through proper process

## Change Process

To modify these constraints:
1. Create an issue proposing the change
2. Get team approval
3. Update this document
4. Update affected code and documentation

---

**Last Updated**: [Date]
**Version**: 1.0
