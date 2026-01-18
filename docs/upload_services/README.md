# 📚 Services Startup Documentation

This directory contains documentation for starting all VoiceCanvas services after a system reboot.

## 📖 Documentation Files

- **[STARTUP_GUIDE.md](STARTUP_GUIDE.md)** - Complete step-by-step guide with detailed instructions, troubleshooting, and verification steps
- **[QUICK_START.md](QUICK_START.md)** - Quick reference for experienced users who need fast startup commands

## 🎯 Purpose

When you request the AI assistant to start services, it will:

1. Review this documentation
2. Follow the step-by-step instructions
3. Verify each service is running correctly
4. Ensure continuity of all operations

## 🔄 Usage

**To request service startup**, simply ask:
> "Start all services" or "Upload services" or "Start VoiceCanvas services"

The AI assistant will:
- Navigate to the project directory
- Start Docker services
- Start backend, worker, beat, and frontend
- Verify all services are operational
- Report status of each service

## 📋 Service Checklist

After startup, the following services should be running:

- [ ] PostgreSQL (Docker)
- [ ] Redis (Docker)
- [ ] MinIO (Docker)
- [ ] FastAPI Backend
- [ ] Celery Worker
- [ ] Celery Beat
- [ ] React Frontend

## 🔧 Maintenance

This documentation should be updated when:
- Service ports change
- New services are added
- Startup sequence changes
- Environment variables are modified

---

**Note**: All services must remain running for the application to function. Each service runs in its own terminal process.
