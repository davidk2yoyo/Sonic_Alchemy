# ⚡ Quick Start - VoiceCanvas Services

Quick reference for starting all services. For detailed instructions, see [STARTUP_GUIDE.md](STARTUP_GUIDE.md).

## 🚀 Fast Startup Sequence

### Terminal 1: Infrastructure Services
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy
docker-compose up -d
docker-compose ps  # Wait for all services to be healthy
```

### Terminal 2: Backend
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
export POSTGRES_HOST=localhost POSTGRES_PORT=5442 MINIO_ENDPOINT=localhost:9010
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: Celery Worker
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
export POSTGRES_HOST=localhost POSTGRES_PORT=5442 MINIO_ENDPOINT=localhost:9010
celery -A app.tasks.celery_app worker --loglevel=info
```

### Terminal 4: Celery Beat
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/backend
source ../venv/bin/activate
export POSTGRES_HOST=localhost POSTGRES_PORT=5442
celery -A app.tasks.celery_app beat --loglevel=info
```

### Terminal 5: Frontend
```bash
cd /Users/feliperangel/Python/Sonic_Alchemy/frontend
npm run dev
```

## ✅ Quick Verification

```bash
# All services healthy?
curl http://localhost:8000/health && echo "✅ Backend"
docker-compose exec redis redis-cli ping && echo "✅ Redis"
curl -s http://localhost:9010/minio/health/live && echo "✅ MinIO"
```

## 🌐 Access Points

- **Frontend**: http://localhost:3010
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9011

---

For detailed troubleshooting, see [STARTUP_GUIDE.md](STARTUP_GUIDE.md).
