# Deployment Guide

## Overview

This guide covers deployment procedures for Sonic Alchemy in production environments.

## Prerequisites

- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+
- MinIO or S3-compatible storage
- Domain name (for production)
- SSL certificates (for HTTPS)

## Environment Setup

### Production Environment Variables

Create `.env.production` with production values:

```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@db:5432/voicecanvas
SECRET_KEY=<strong_random_secret>
GEMINI_API_KEY=<your_gemini_key>
# ... other production values
```

## Docker Deployment

### Build Images

```bash
docker-compose -f docker-compose.prod.yml build
```

### Run Migrations

```bash
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Database Backup

### Backup Procedure

```bash
docker exec voicecanvas-postgres pg_dump -U voicecanvas voicecanvas > backup.sql
```

### Restore Procedure

```bash
docker exec -i voicecanvas-postgres psql -U voicecanvas voicecanvas < backup.sql
```

## Monitoring

### Health Checks

- API: `http://your-domain:8010/health`
- Database: Check container health status
- Redis: Check container health status

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
```

## Scaling

### Horizontal Scaling

- API servers: Scale backend service
- Workers: Scale worker service
- Frontend: Use CDN or load balancer

### Vertical Scaling

- Increase container resources
- Optimize database queries
- Use connection pooling

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable database encryption
- [ ] Regular security updates
- [ ] Monitor for vulnerabilities

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL
   - Verify network connectivity
   - Check database logs

2. **MinIO Connection Errors**
   - Verify MINIO_ENDPOINT
   - Check credentials
   - Verify network access

3. **Celery Tasks Not Running**
   - Check worker logs
   - Verify Redis connection
   - Check task queue status

---

**Last Updated**: [Date]
**Version**: 1.0
