# Architecture Document

This document describes the key architectural decisions for the Sonic Alchemy (VoiceCanvas) project.

## System Overview

Sonic Alchemy is a monolithic modular application with clear service boundaries, designed to handle AI-powered music creation workflows.

## Architecture Pattern

**Monolithic Modular Architecture**
- Single FastAPI application with modular structure
- Separate Celery worker for async processing
- Clear separation of concerns through service layers

## Service Boundaries

### Backend Services

1. **API Layer** (`app/api/v1/`)
   - RESTful API endpoints
   - Request/response handling
   - Authentication middleware
   - Input validation

2. **Service Layer** (`app/services/`)
   - Business logic
   - External API integration (Gemini)
   - Audio processing
   - File management

3. **Data Layer** (`app/models/`)
   - SQLAlchemy models
   - Database interactions
   - Relationships and constraints

4. **Task Layer** (`app/tasks/`)
   - Celery tasks
   - Async processing
   - Background jobs

5. **WebSocket Layer** (`app/websocket/`)
   - Real-time communication
   - Collaboration features
   - Presence tracking

## Communication Patterns

### Synchronous Communication
- Frontend → Backend: REST API (HTTP/HTTPS)
- Backend → Database: SQLAlchemy ORM
- Backend → MinIO: S3-compatible API

### Asynchronous Communication
- Backend → Celery: Redis message broker
- Celery → Gemini API: HTTP requests
- Frontend → Backend: WebSocket for real-time updates

### Event Flow

```
User Action → Frontend → API Endpoint → Service Layer
                                    ↓
                            [Sync Response] OR [Async Task]
                                    ↓
                            Database/MinIO/Gemini API
                                    ↓
                            WebSocket Notification (if async)
                                    ↓
                            Frontend Update
```

## Database Schema Principles

### Design Principles
- Normalize data to 3NF where possible
- Use foreign keys for relationships
- Index frequently queried fields
- Use JSON fields for flexible metadata
- Soft deletes for user data

### Core Entities
- **Users**: Authentication and user profiles
- **Projects**: User's music projects
- **Canvases**: Image analysis and music generation
- **VoiceRecordings**: Audio files and processing metadata
- **Lyrics**: Generated and user-edited lyrics

## API Versioning Strategy

- **Current Version**: `v1`
- **URL Pattern**: `/api/v1/{resource}`
- **Versioning Method**: URL path versioning
- **Backward Compatibility**: Maintain v1 until v2 is released
- **Deprecation**: Announce deprecation 3 months before removal

## Async Processing Patterns

### When to Use Celery
- Image analysis (Gemini Vision API)
- Audio processing (pitch correction, style transfer)
- Music generation
- Large file operations
- Long-running AI operations

### Task Patterns
- **Fire and Forget**: For non-critical operations
- **Result Tracking**: For operations requiring status updates
- **Chaining**: For dependent operations
- **Retry Logic**: For transient failures

## File Storage Architecture

### MinIO Buckets
- `audio`: Raw and processed audio files
- `images`: User-uploaded images and canvas drawings
- `exports`: Final exported music files

### File Naming Convention
- `{user_id}/{project_id}/{type}/{timestamp}_{filename}`
- Example: `user123/proj456/audio/20240101_120000_voice.wav`

### Access Control
- Private by default
- Signed URLs for temporary access
- CDN integration (future)

## Caching Strategy

### Redis Cache Layers
1. **API Response Cache**: Cache Gemini API responses
2. **Session Cache**: User sessions and tokens
3. **Query Cache**: Frequently accessed database queries

### Cache Keys
- Pattern: `{service}:{resource}:{identifier}`
- Example: `gemini:emotion:image_hash_123`
- TTL: Varies by data type (1 hour to 24 hours)

## Security Architecture

### Authentication Flow
1. User registers/logs in
2. Backend validates credentials
3. JWT token issued (access + refresh)
4. Frontend stores token
5. Token included in API requests
6. Backend validates token on each request

### Authorization
- Role-based access control (future)
- Resource ownership validation
- API rate limiting per user

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### Error Categories
- **4xx**: Client errors (validation, authentication)
- **5xx**: Server errors (internal, external API failures)
- **Async Errors**: Tracked in task results, notified via WebSocket

## Logging Strategy

### Log Levels
- **DEBUG**: Development and troubleshooting
- **INFO**: Normal operations and flow
- **WARNING**: Recoverable issues
- **ERROR**: Failures requiring attention

### Log Structure
- Structured logging (JSON format)
- Include request ID for tracing
- Log user actions (audit trail)
- Log external API calls

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers (can scale horizontally)
- Celery workers (can scale independently)
- Database connection pooling

### Vertical Scaling
- Optimize database queries
- Cache frequently accessed data
- Use CDN for static assets (future)

## Integration Points

### Gemini API Integration
- **Vision API**: Image emotion analysis
- **Audio API**: Voice transcription and analysis
- **Text API**: Lyric generation
- **Rate Limiting**: Implement exponential backoff
- **Error Handling**: Retry transient failures

### External Services
- MinIO for object storage
- Redis for caching and queuing
- PostgreSQL for persistence

## Deployment Architecture

### Development
- Local services via Docker Compose
- Local code execution with venv
- Hot reload for development

### Production (Future)
- Container orchestration (Kubernetes/Docker Swarm)
- Load balancer for API servers
- Database replication
- CDN for static assets

## Technology Decisions

### Why FastAPI?
- High performance
- Automatic API documentation
- Type hints and validation
- Async support

### Why React + TypeScript?
- Component reusability
- Type safety
- Large ecosystem
- Developer experience

### Why Celery?
- Proven async task processing
- Redis integration
- Task monitoring
- Retry mechanisms

### Why MinIO?
- S3-compatible API
- Self-hosted option
- Easy migration to S3
- Local development support

## Future Considerations

- Microservices migration (if needed)
- GraphQL API (alternative to REST)
- Real-time collaboration enhancements
- Mobile app support
- AI model fine-tuning

---

**Last Updated**: [Date]
**Version**: 1.0
