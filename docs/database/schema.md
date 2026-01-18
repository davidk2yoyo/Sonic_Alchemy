# Database Schema Documentation

## Overview

This document describes the database schema for Sonic Alchemy (VoiceCanvas).

## Entity Relationship Diagram

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

## Tables

### Users Table

Stores user authentication and profile information.

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

**Indexes:**
- `users_email_idx` on `email`
- `users_username_idx` on `username`

**Relationships:**
- One-to-many with `projects`

### Projects Table

Stores user music projects.

```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    canvas_id INTEGER REFERENCES canvases(id) ON DELETE SET NULL,
    voice_recording_id INTEGER REFERENCES voice_recordings(id) ON DELETE SET NULL,
    lyrics_id INTEGER REFERENCES lyrics(id) ON DELETE SET NULL,
    metadata JSONB,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `projects_user_id_idx` on `user_id`

**Relationships:**
- Many-to-one with `users`
- One-to-one with `canvases`
- One-to-one with `voice_recordings`
- One-to-one with `lyrics`

### Canvases Table

Stores image analysis and music generation data.

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

**Indexes:**
- `canvases_project_id_idx` on `project_id`

**Status Values:**
- `pending` - Image uploaded, awaiting analysis
- `analyzing` - Emotion analysis in progress
- `analyzed` - Analysis complete
- `generating` - Music generation in progress
- `completed` - Music generation complete
- `failed` - Processing failed

**Relationships:**
- Many-to-one with `projects`

### Voice Recordings Table

Stores audio files and processing metadata.

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

**Indexes:**
- `voice_recordings_project_id_idx` on `project_id`

**Status Values:**
- `pending` - Audio uploaded, awaiting processing
- `processing` - Audio processing in progress
- `completed` - Processing complete
- `failed` - Processing failed

**Relationships:**
- Many-to-one with `projects`

### Lyrics Table

Stores generated and edited song lyrics.

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

**Indexes:**
- `lyrics_project_id_idx` on `project_id`

**Structure JSON Format:**
```json
{
    "verses": ["verse1", "verse2"],
    "chorus": ["chorus line 1", "chorus line 2"],
    "bridge": ["bridge line 1"]
}
```

**Relationships:**
- Many-to-one with `projects`

## Data Types

### JSONB Fields

Several tables use JSONB for flexible metadata storage:

- `projects.metadata` - Project-specific settings and data
- `canvases.emotion_analysis` - Emotion analysis results from Gemini
- `voice_recordings.corrections_applied` - Applied audio corrections
- `lyrics.structure` - Song structure information

## Constraints

### Foreign Keys
- All foreign keys use `ON DELETE CASCADE` or `ON DELETE SET NULL` as appropriate
- Ensures referential integrity

### Unique Constraints
- `users.email` - Unique email addresses
- `users.username` - Unique usernames

### Check Constraints
- Status fields have predefined valid values
- File URLs must be valid (enforced at application level)

## Indexes

All foreign keys are automatically indexed. Additional indexes:
- Email and username for fast user lookups
- Project user_id for efficient user project queries

## Migration Strategy

Database migrations are managed using Alembic. See [Migrations Guide](migrations.md) for details.

---

**Last Updated**: [Date]
**Version**: 1.0
