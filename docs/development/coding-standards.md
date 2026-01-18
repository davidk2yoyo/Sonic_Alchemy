# Coding Standards

## Overview

This document defines coding standards and best practices for the Sonic Alchemy project.

## Language

- **All code and comments must be in English**
- **All documentation must be in English**

## Python (Backend)

### Style Guide

- Follow PEP 8
- Maximum line length: 127 characters
- Use type hints for function parameters and return types
- Use docstrings for all functions and classes

### Code Organization

```python
# Imports: standard library, third-party, local
import os
from typing import Optional

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
```

### Naming Conventions

- **Classes**: PascalCase (`UserService`)
- **Functions/Methods**: snake_case (`get_user`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_UPLOAD_SIZE`)
- **Variables**: snake_case (`user_id`)

### Type Hints

```python
def get_user(user_id: int, db: Session) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()
```

### Error Handling

```python
try:
    result = process_data()
except SpecificException as e:
    logger.error(f"Error processing: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

## TypeScript (Frontend)

### Style Guide

- Follow ESLint configuration
- Maximum line length: 100 characters
- Use TypeScript strict mode
- Prefer functional components with hooks

### Code Organization

```typescript
// Imports: React, third-party, local
import React, { useState } from 'react';
import axios from 'axios';

import apiClient from '../services/api';
```

### Naming Conventions

- **Components**: PascalCase (`UserProfile`)
- **Functions**: camelCase (`getUserData`)
- **Constants**: UPPER_SNAKE_CASE (`API_URL`)
- **Variables**: camelCase (`userId`)

### Type Definitions

```typescript
interface User {
  id: number;
  email: string;
  username: string;
}

const getUser = async (userId: number): Promise<User> => {
  // ...
};
```

## Git Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

### Examples

```
feat(canvas): add emotion analysis from images

Implement Gemini Vision API integration to analyze emotions
from uploaded images and generate music prompts.

Closes #123
```

## Code Review Guidelines

### For Authors

- Keep PRs focused and small
- Respond to all review comments
- Update PR based on feedback

### For Reviewers

- Be constructive and respectful
- Check code quality and correctness
- Verify tests are included
- Ensure documentation is updated

## Testing

- Write tests for new features
- Aim for 70%+ coverage on critical paths
- Use descriptive test names
- Test both success and error cases

---

**Last Updated**: [Date]
**Version**: 1.0
