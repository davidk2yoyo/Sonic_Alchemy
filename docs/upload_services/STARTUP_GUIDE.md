# 🚀 VoiceCanvas Services Startup Guide

Complete step-by-step guide to start all services after a system reboot.

## 📋 Overview

This guide provides instructions to start all VoiceCanvas services in the correct order after a system restart. Follow these steps to ensure all services are operational.

## ✅ Prerequisites Check

Before starting services, verify:

- [ ] Docker Desktop is running (or Docker daemon is active)
- [ ] Python 3.9+ is installed
- [ ] Node.js 18+ is installed
- [ ] `.env` file exists in project root with all required variables
- [ ] Virtual environment exists at `venv/`

## 🔄 Startup Sequence

Services must be started in this order:

1. **Infrastructure Services** (Docker Compose)
2. **Database Migrations** (if needed)
3. **Backend Service** (FastAPI)
4. **Celery Worker** (Background tasks)
5. **Celery Beat** (Scheduled tasks)
6. **Frontend Service** (React)

## 📝 Step-by-Step Instructions

### Step 1: Navigate to Project Directory

```bash
cd /Users/feliperangel/Python/Sonic_Alchemy
```

### Step 2: Verify Docker is Running

```bash
docker ps
```

**Expected**: Should show running containers or empty list (not an error)

**If Docker is not running**:
- macOS: Open Docker Desktop application
- Linux: `sudo systemctl start docker`
- Wait for Docker to fully start (check system tray icon)

### Step 3: Start Infrastructure Services (Docker Compose)

```bash
docker-compose up -d
```

**What this starts**:
- PostgreSQL (port 5442)
- Redis (port 6389)
- MinIO (ports 9010/9011)

**Wait for services to be healthy** (30-60 seconds):
```bash
docker-compose ps
```

**Expected output**: All services should show `(healthy)` status

**Verify each service**:
```bash
# PostgreSQL
docker-compose exec postgres pg_isready -U voicecanvas

# Redis
docker-compose exec redis redis-cli ping
# Should return: PONG

# MinIO
curl -s http://localhost:9010/minio/health/live
# Should return: HTTP 200
```

### Step 4: Activate Python Virtual Environment

```bash
source venv/bin/activate
```

**Verify activation**:
```bash
which python
# Should show: /Users/feliperangel/Python/Sonic_Alchemy/venv/bin/python
```

### Step 5: Set Environment Variables

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5442
export MINIO_ENDPOINT=localhost:9010
```

**Or use the startup script**:
```bash
source start_backend.sh
# (This will start backend, but we'll do it manually in next steps)
```

### Step 6: Run Database Migrations (if needed)

```bash
cd backend
alembic upgrade head
```

**Expected**: Should show "INFO [alembic.runtime.migration] Running upgrade ..."

**If migrations fail**: Check database connection and ensure PostgreSQL is running.

### Step 7: Verify Environment Configuration

```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
python -c "from app.core.config import settings; print(f'Database: {settings.DATABASE_URL[:30]}...'); print(f'MinIO: {settings.MINIO_ENDPOINT}'); print(f'Gemini: {\"Configured\" if settings.GEMINI_API_KEY else \"NOT CONFIGURED\"}')"
```

**Expected**: Should show configuration values without errors.

### Step 8: Start Backend Service (FastAPI)

**Option A: Using uvicorn directly**
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5442
export MINIO_ENDPOINT=localhost:9010
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option B: Using the startup script**
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy
./start_backend.sh
```

**Verify backend is running**:
```bash
curl http://localhost:8000/health
```

**Expected**: Should return `{"status":"healthy"}`

**Keep this terminal open** - Backend must stay running.

### Step 9: Start Celery Worker (Background Tasks)

**Open a NEW terminal window/tab**:

```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5442
export MINIO_ENDPOINT=localhost:9010
celery -A app.tasks.celery_app worker --loglevel=info
```

**Verify worker is running**:
- Should see: `celery@hostname ready`
- Should show: `[INFO/MainProcess] Connected to redis://...`

**Keep this terminal open** - Worker must stay running.

### Step 10: Start Celery Beat (Scheduled Tasks)

**Open a NEW terminal window/tab**:

```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5442
celery -A app.tasks.celery_app beat --loglevel=info
```

**Verify beat is running**:
- Should see: `celery beat v... is starting`
- Should show: `[INFO/MainProcess] Scheduler: Sending due task...`

**Keep this terminal open** - Beat must stay running.

### Step 11: Start Frontend Service (React)

**Open a NEW terminal window/tab**:

```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/frontend
npm run dev
```

**Verify frontend is running**:
- Should show: `Local: http://localhost:3010/`
- Should show: `ready in X ms`

**Keep this terminal open** - Frontend must stay running.

## ✅ Verification Checklist

After all services are started, verify everything is working:

### 1. Infrastructure Services
```bash
docker-compose ps
```
**Expected**: All services (postgres, redis, minio) should be `Up` and `(healthy)`

### 2. Backend API
```bash
curl http://localhost:8000/health
```
**Expected**: `{"status":"healthy"}`

### 3. API Documentation
Open browser: http://localhost:8000/docs
**Expected**: Swagger UI should load

### 4. Frontend
Open browser: http://localhost:3010
**Expected**: VoiceCanvas login page should load

### 5. MinIO Console
Open browser: http://localhost:9011
**Expected**: MinIO console should load (login with credentials from .env)

### 6. Database Connection
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('✅ Database connected'); db.close()"
```
**Expected**: Should print `✅ Database connected` without errors

### 7. Redis Connection
```bash
docker-compose exec redis redis-cli ping
```
**Expected**: `PONG`

### 8. MinIO Connection
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
python -c "from app.services.storage_service import storage_service; print('✅ MinIO connected' if storage_service.client else '❌ MinIO not connected')"
```
**Expected**: Should print `✅ MinIO connected`

## 🔧 Troubleshooting

### Docker services won't start
```bash
# Check Docker status
docker info

# Restart Docker services
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs
```

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check environment variables
echo $POSTGRES_HOST
echo $POSTGRES_PORT
echo $MINIO_ENDPOINT

# Check .env file exists
ls -la .env
```

### Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U voicecanvas -d voicecanvas -c "SELECT 1;"
```

### Frontend won't start
```bash
# Check if port 3010 is in use
lsof -i :3010

# Reinstall dependencies if needed
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Celery worker won't start
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Check Celery logs
# Look for connection errors in the terminal
```

## 📊 Service Status Summary

After successful startup, you should have:

| Service | Port | Status Check |
|---------|------|--------------|
| PostgreSQL | 5442 | `docker-compose ps postgres` |
| Redis | 6389 | `docker-compose exec redis redis-cli ping` |
| MinIO API | 9010 | `curl http://localhost:9010/minio/health/live` |
| MinIO Console | 9011 | Browser: http://localhost:9011 |
| FastAPI Backend | 8000 | `curl http://localhost:8000/health` |
| React Frontend | 3010 | Browser: http://localhost:3010 |
| Celery Worker | - | Check terminal output |
| Celery Beat | - | Check terminal output |

## 🎯 Quick Start Script

For convenience, you can create a startup script that runs all commands. However, services must run in separate terminals to stay active.

## 📝 Notes

- **Backend, Celery Worker, Celery Beat, and Frontend** must each run in separate terminal windows/tabs
- **Docker services** run in the background (detached mode)
- **All services** must remain running for the application to function
- **Environment variables** must be set in each terminal where services run
- **Virtual environment** must be activated in terminals running Python services

## 🔄 Restarting Services

If you need to restart a service:

1. **Stop the service** (Ctrl+C in its terminal)
2. **Follow the corresponding step** from this guide
3. **Verify** it's running correctly

## 🛑 Stopping All Services

To stop all services:

```bash
# Stop Docker services
docker-compose down

# Stop backend, worker, beat, frontend
# Press Ctrl+C in each terminal window
```

---

**Last Updated**: 2026-01-18
**Maintained by**: AI Assistant
**For**: VoiceCanvas Project
