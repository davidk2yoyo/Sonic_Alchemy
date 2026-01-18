# Database Migrations Guide

## Overview

This project uses Alembic for database migrations. All schema changes should be done through migrations to maintain version control and consistency.

## Setup

Alembic is configured in `backend/alembic/`. The configuration uses environment variables from `.env`.

## Creating Migrations

### Initial Migration

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

### Manual Migration

```bash
alembic revision -m "Description of changes"
```

## Running Migrations

### Apply All Pending Migrations

```bash
cd backend
alembic upgrade head
```

### Rollback One Migration

```bash
alembic downgrade -1
```

### Rollback to Specific Version

```bash
alembic downgrade <revision_id>
```

## Migration Best Practices

1. **Always Review Auto-Generated Migrations**
   - Check the generated migration file
   - Ensure it matches your intended changes
   - Add data migrations if needed

2. **Test Migrations**
   - Test on development database first
   - Verify both upgrade and downgrade paths
   - Check data integrity after migration

3. **Migration Naming**
   - Use descriptive names: `add_user_email_index`
   - Include ticket/issue number if applicable
   - Be specific about what changed

4. **Data Migrations**
   - For schema changes that require data transformation
   - Use `op.execute()` for custom SQL
   - Test thoroughly with sample data

## Migration File Structure

```python
"""Add user email index

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    op.create_index('users_email_idx', 'users', ['email'])

def downgrade():
    op.drop_index('users_email_idx', 'users')
```

## Environment-Specific Migrations

Migrations run automatically in Docker containers. For local development:

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
cd backend
alembic upgrade head
```

## Troubleshooting

### Migration Conflicts
- Check current database state: `alembic current`
- Review migration history: `alembic history`
- Resolve conflicts manually if needed

### Failed Migrations
- Check error messages carefully
- Rollback if needed: `alembic downgrade -1`
- Fix migration file and retry

---

**Last Updated**: [Date]
**Version**: 1.0
