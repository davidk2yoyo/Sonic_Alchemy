# API Documentation

## Overview

Sonic Alchemy provides a RESTful API for all operations. The API is versioned and follows REST principles.

## Base URL

- Development: `http://localhost:8010`
- Production: (TBD)

## API Versioning

Current version: `v1`

All endpoints are prefixed with `/api/v1`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Interactive Documentation

- Swagger UI: `http://localhost:8010/docs`
- ReDoc: `http://localhost:8010/redoc`

## Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Authenticate user
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### Canvas

- `POST /api/v1/canvas/upload` - Upload image
- `POST /api/v1/canvas/analyze` - Analyze image emotion
- `POST /api/v1/canvas/generate-music` - Generate music from canvas
- `GET /api/v1/canvas/{canvas_id}` - Get canvas details

### Voice

- `POST /api/v1/voice/upload` - Upload raw audio
- `POST /api/v1/voice/process` - Process voice with corrections
- `POST /api/v1/voice/style-transfer` - Apply style transfer
- `GET /api/v1/voice/{voice_id}` - Get voice recording details

### Lyrics

- `POST /api/v1/lyrics/generate` - Generate lyrics from theme
- `POST /api/v1/lyrics/match` - Match lyrics to melody
- `PUT /api/v1/lyrics/{lyrics_id}` - Update lyrics

### Projects

- `GET /api/v1/projects` - List user projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{project_id}` - Get project
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project

## WebSocket Events

See [WebSocket Documentation](websocket.md) for real-time collaboration events.

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API rate limiting may be implemented in production. Check response headers for rate limit information.

---

**Last Updated**: [Date]
**Version**: 1.0
