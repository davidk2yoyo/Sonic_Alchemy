# WebSocket API Documentation

## Overview

WebSocket connections enable real-time collaboration and updates for projects.

## Connection

Connect to: `ws://localhost:8010` (development)

## Authentication

Include JWT token in connection query string:

```
ws://localhost:8010?token=<access_token>
```

## Events

### Client → Server

#### Join Project
```json
{
  "type": "join_project",
  "payload": {
    "project_id": 123
  }
}
```

#### Leave Project
```json
{
  "type": "leave_project",
  "payload": {
    "project_id": 123
  }
}
```

#### Update Project
```json
{
  "type": "update_project",
  "payload": {
    "project_id": 123,
    "data": {
      "title": "Updated Title"
    }
  }
}
```

### Server → Client

#### Project Updated
```json
{
  "type": "project_updated",
  "payload": {
    "project_id": 123,
    "changes": {
      "title": "New Title"
    },
    "updated_by": "user_id"
  }
}
```

#### User Joined
```json
{
  "type": "user_joined",
  "payload": {
    "project_id": 123,
    "user_id": 456,
    "username": "john_doe"
  }
}
```

#### User Left
```json
{
  "type": "user_left",
  "payload": {
    "project_id": 123,
    "user_id": 456
  }
}
```

#### Task Completed
```json
{
  "type": "task_completed",
  "payload": {
    "task_id": "celery_task_id",
    "task_type": "analyze_image_emotion",
    "result": {
      "canvas_id": 123,
      "status": "completed"
    }
  }
}
```

#### Task Progress
```json
{
  "type": "task_progress",
  "payload": {
    "task_id": "celery_task_id",
    "progress": 75,
    "message": "Processing audio..."
  }
}
```

## Error Handling

Errors are sent as:

```json
{
  "type": "error",
  "payload": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Connection Lifecycle

1. Client connects with authentication token
2. Server validates token
3. Client joins project rooms as needed
4. Server sends updates to all clients in room
5. Client disconnects or leaves rooms

## Reconnection

Clients should implement automatic reconnection with exponential backoff.

---

**Last Updated**: [Date]
**Version**: 1.0
