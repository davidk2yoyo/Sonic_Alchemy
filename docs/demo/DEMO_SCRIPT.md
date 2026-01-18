# VoiceCanvas Demo Script

## Overview
This document provides a step-by-step guide for demonstrating VoiceCanvas features.

## Prerequisites
1. All Docker services running (`docker-compose up -d`)
2. Database migrations applied (`alembic upgrade head`)
3. Frontend running (`npm run dev` in frontend/)
4. Backend running (`uvicorn app.main:app --reload` in backend/)
5. Celery worker running (`celery -A app.tasks.celery_app worker`)

## Demo Flow

### 1. User Registration and Login
1. Open frontend at http://localhost:3010
2. Click "Register"
3. Enter:
   - Email: demo@example.com
   - Username: demouser
   - Password: demo123
4. Click "Register"
5. Verify redirect to dashboard

### 2. Create Project
1. Click "New Project"
2. Enter:
   - Title: "My First Song"
   - Description: "A demo project"
3. Click "Create"
4. Verify project appears in dashboard

### 3. Canvas Feature - Emotion to Music
1. Navigate to project
2. Click "Add Canvas"
3. Upload an image (e.g., sunset, happy scene)
4. Click "Analyze Emotion"
5. Wait for analysis (Celery task)
6. View emotion analysis results
7. Click "Generate Music"
8. Wait for music generation prompt

### 4. Voice Feature - Voice Processing
1. Navigate to project
2. Click "Add Voice"
3. Upload audio file (WAV, MP3)
4. Select processing options:
   - Pitch correction: Yes
   - Timing quantization: Yes
5. Click "Process"
6. Wait for processing
7. Download processed audio

### 5. Lyrics Feature - AI Generation
1. Navigate to project
2. Click "Generate Lyrics"
3. Enter:
   - Theme: "love and happiness"
   - Emotion: "joyful"
4. Click "Generate"
5. View generated lyrics
6. Edit lyrics if desired
7. Save changes

### 6. Real-time Collaboration (WebSocket)
1. Open project in two browser windows
2. Make changes in one window
3. Verify updates appear in other window
4. Test user presence indicators

## Troubleshooting

### Services Not Running
```bash
docker-compose ps  # Check service status
docker-compose logs backend  # Check backend logs
docker-compose logs worker  # Check Celery worker logs
```

### Database Issues
```bash
cd backend
alembic upgrade head  # Apply migrations
```

### Frontend Issues
```bash
cd frontend
npm install  # Reinstall dependencies
npm run dev  # Restart dev server
```

## Success Criteria
- All features work end-to-end
- No errors in browser console
- No errors in backend logs
- Celery tasks complete successfully
- WebSocket connections work
