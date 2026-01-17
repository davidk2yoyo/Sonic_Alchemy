# Design Specification

Technical design document for Sonic Alchemy (VoiceCanvas) following AI-DLC methodology.

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   React     │  Frontend (Port 3010)
│  Frontend   │
└──────┬──────┘
       │ HTTP/REST
       │ WebSocket
┌──────▼──────┐
│   FastAPI   │  Backend API (Port 8010)
│   Backend   │
└──────┬──────┘
       │
       ├───► PostgreSQL (Port 5442)
       ├───► Redis (Port 6389)
       ├───► MinIO (Ports 9010/9011)
       │
┌──────▼──────┐
│   Celery    │  Async Worker
│   Worker    │
└──────┬──────┘
       │
       └───► Gemini API (External)
```

## Database Schema

### Entity Relationship Diagram

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  User    │────────│ Project   │────────│ Canvas   │
│          │1      *│          *│      1 │          │
└──────────┘        └──────────┘        └──────────┘
                            │
                            │
                     ┌──────▼────────┐
                     │ VoiceRecording│
                     │               │
                     └───────────────┘
                            │
                     ┌──────▼──────┐
                     │   Lyrics     │
                     │              │
                     └──────────────┘
```

### Database Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### Projects Table
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    canvas_id INTEGER REFERENCES canvases(id),
    voice_recording_id INTEGER REFERENCES voice_recordings(id),
    lyrics_id INTEGER REFERENCES lyrics(id),
    metadata JSONB,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Canvases Table
```sql
CREATE TABLE canvases (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    emotion_analysis JSONB,
    music_generation_prompt TEXT,
    generated_music_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Voice Recordings Table
```sql
CREATE TABLE voice_recordings (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    raw_audio_url VARCHAR(500) NOT NULL,
    processed_audio_url VARCHAR(500),
    style VARCHAR(100),
    corrections_applied JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Lyrics Table
```sql
CREATE TABLE lyrics (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    theme TEXT,
    generated_lyrics TEXT NOT NULL,
    edited_lyrics TEXT,
    structure JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints Specification

### Authentication Endpoints

#### POST `/api/v1/auth/register`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username"
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

#### POST `/api/v1/auth/login`
Authenticate user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** Same as register

#### POST `/api/v1/auth/refresh`
Refresh access token.

**Request:**
```json
{
  "refresh_token": "refresh_token"
}
```

**Response:**
```json
{
  "access_token": "new_jwt_token"
}
```

#### GET `/api/v1/auth/me`
Get current user information.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Canvas Endpoints

#### POST `/api/v1/canvas/upload`
Upload image for emotion analysis.

**Request:** Multipart form data
- `file`: Image file
- `project_id`: Optional project ID

**Response:**
```json
{
  "canvas_id": 1,
  "image_url": "https://minio.../image.jpg",
  "status": "uploaded"
}
```

#### POST `/api/v1/canvas/analyze`
Analyze image emotion using Gemini Vision.

**Request:**
```json
{
  "canvas_id": 1
}
```

**Response:**
```json
{
  "canvas_id": 1,
  "emotions": ["happy", "energetic"],
  "analysis": {
    "primary_emotion": "happy",
    "confidence": 0.85,
    "details": "..."
  },
  "status": "analyzed"
}
```

#### POST `/api/v1/canvas/generate-music`
Generate music from canvas analysis.

**Request:**
```json
{
  "canvas_id": 1,
  "duration_seconds": 60,
  "style": "ambient"
}
```

**Response:**
```json
{
  "task_id": "celery_task_id",
  "status": "processing",
  "estimated_completion": "2024-01-01T00:01:00Z"
}
```

#### GET `/api/v1/canvas/{canvas_id}`
Get canvas details.

**Response:**
```json
{
  "id": 1,
  "image_url": "https://...",
  "emotion_analysis": {...},
  "generated_music_url": "https://...",
  "status": "completed"
}
```

### Voice Endpoints

#### POST `/api/v1/voice/upload`
Upload raw audio file.

**Request:** Multipart form data
- `file`: Audio file
- `project_id`: Optional project ID

**Response:**
```json
{
  "voice_id": 1,
  "raw_audio_url": "https://minio.../audio.wav",
  "duration_seconds": 120.5,
  "status": "uploaded"
}
```

#### POST `/api/v1/voice/process`
Process voice with corrections.

**Request:**
```json
{
  "voice_id": 1,
  "corrections": {
    "pitch_correction": true,
    "timing_quantization": true,
    "breath_control": true
  }
}
```

**Response:**
```json
{
  "task_id": "celery_task_id",
  "status": "processing"
}
```

#### POST `/api/v1/voice/style-transfer`
Apply style transfer to voice.

**Request:**
```json
{
  "voice_id": 1,
  "style": "jazz",
  "reference_audio_url": "https://..." // Optional
}
```

**Response:**
```json
{
  "task_id": "celery_task_id",
  "status": "processing"
}
```

#### GET `/api/v1/voice/{voice_id}`
Get voice recording details.

**Response:**
```json
{
  "id": 1,
  "raw_audio_url": "https://...",
  "processed_audio_url": "https://...",
  "style": "jazz",
  "status": "completed"
}
```

### Lyrics Endpoints

#### POST `/api/v1/lyrics/generate`
Generate lyrics from theme.

**Request:**
```json
{
  "theme": "heartbreak in the rain",
  "emotion": "sad",
  "project_id": 1
}
```

**Response:**
```json
{
  "lyrics_id": 1,
  "generated_lyrics": "Verse 1...\nChorus...",
  "structure": {
    "verses": 2,
    "chorus": true,
    "bridge": false
  }
}
```

#### POST `/api/v1/lyrics/match`
Match lyrics to melody.

**Request:**
```json
{
  "lyrics_id": 1,
  "melody_url": "https://...",
  "project_id": 1
}
```

**Response:**
```json
{
  "lyrics_id": 1,
  "matched_lyrics": "Adjusted lyrics...",
  "changes": ["Line 3 adjusted", "Chorus timing updated"]
}
```

#### PUT `/api/v1/lyrics/{lyrics_id}`
Update lyrics.

**Request:**
```json
{
  "edited_lyrics": "User edited lyrics..."
}
```

**Response:**
```json
{
  "lyrics_id": 1,
  "edited_lyrics": "User edited lyrics...",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Project Endpoints

#### GET `/api/v1/projects`
List user projects.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `search`: Search term

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "title": "My Song",
      "description": "...",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20
}
```

#### POST `/api/v1/projects`
Create new project.

**Request:**
```json
{
  "title": "My New Song",
  "description": "A song about..."
}
```

**Response:**
```json
{
  "id": 1,
  "title": "My New Song",
  "description": "A song about...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/v1/projects/{project_id}`
Get project details.

**Response:**
```json
{
  "id": 1,
  "title": "My Song",
  "canvas": {...},
  "voice_recording": {...},
  "lyrics": {...},
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT `/api/v1/projects/{project_id}`
Update project.

**Request:**
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response:** Updated project object

#### DELETE `/api/v1/projects/{project_id}`
Delete project.

**Response:**
```json
{
  "message": "Project deleted successfully"
}
```

## Data Flow Diagrams

### Emotion Canvas Flow

```
User Uploads Image
    ↓
Store in MinIO
    ↓
Create Canvas Record (status: uploaded)
    ↓
Queue Celery Task: analyze_image_emotion
    ↓
Gemini Vision API Analysis
    ↓
Update Canvas (emotion_analysis, status: analyzed)
    ↓
Queue Celery Task: generate_music
    ↓
Music Generation (Gemini/External)
    ↓
Store Generated Music in MinIO
    ↓
Update Canvas (generated_music_url, status: completed)
    ↓
WebSocket Notification to Frontend
    ↓
User Sees Results
```

### Voice Processing Flow

```
User Uploads Audio
    ↓
Store Raw Audio in MinIO
    ↓
Create VoiceRecording Record
    ↓
Queue Celery Task: process_voice_audio
    ↓
Audio Analysis (librosa)
    - Pitch detection
    - Timing analysis
    - Breath detection
    ↓
Apply Corrections
    - Pitch correction
    - Timing quantization
    - Breath smoothing
    ↓
Style Transfer (if requested)
    ↓
Store Processed Audio in MinIO
    ↓
Update VoiceRecording (processed_audio_url, status: completed)
    ↓
WebSocket Notification
    ↓
User Can Preview/Download
```

### Lyric Generation Flow

```
User Provides Theme
    ↓
Gemini Text API: Generate Lyrics
    ↓
Parse Structure (verses, chorus, bridge)
    ↓
Create Lyrics Record
    ↓
If Melody Provided:
    ↓
Analyze Melody Rhythm
    ↓
Match Lyrics to Melody
    ↓
Update Lyrics
    ↓
Return to User
```

## Integration Points

### Gemini API Integration

#### Vision API
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent`
- **Use Case**: Image emotion analysis
- **Input**: Base64 encoded image
- **Output**: JSON with emotion analysis
- **Rate Limit**: 60 requests/minute
- **Error Handling**: Retry with exponential backoff

#### Audio API
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`
- **Use Case**: Audio transcription and analysis
- **Input**: Audio file (converted to text or analyzed)
- **Output**: Transcription and analysis
- **Rate Limit**: 60 requests/minute

#### Text API
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`
- **Use Case**: Lyric generation
- **Input**: Theme and emotion
- **Output**: Generated lyrics
- **Rate Limit**: 60 requests/minute

### MinIO Integration

- **Endpoint**: Configured via environment variables
- **Buckets**: `audio`, `images`, `exports`
- **Access**: Private by default, signed URLs for access
- **File Naming**: `{user_id}/{project_id}/{type}/{timestamp}_{filename}`

### Redis Integration

- **Cache**: API responses, Gemini results
- **Queue**: Celery message broker
- **Sessions**: User sessions (optional)
- **TTL**: Varies by data type

## File Storage Structure

```
MinIO/
├── audio/
│   ├── {user_id}/
│   │   ├── {project_id}/
│   │   │   ├── raw/
│   │   │   │   └── {timestamp}_voice.wav
│   │   │   └── processed/
│   │   │       └── {timestamp}_processed.wav
│
├── images/
│   ├── {user_id}/
│   │   ├── {project_id}/
│   │   │   └── {timestamp}_canvas.{ext}
│
└── exports/
    ├── {user_id}/
    │   ├── {project_id}/
    │   │   └── {timestamp}_final.{ext}
```

## WebSocket Events

### Client → Server
- `join_project`: Join project room
- `leave_project`: Leave project room
- `update_project`: Update project data

### Server → Client
- `project_updated`: Project data changed
- `user_joined`: User joined project
- `user_left`: User left project
- `task_completed`: Async task completed
- `task_progress`: Async task progress update

---

**Last Updated**: [Date]
**Version**: 1.0
