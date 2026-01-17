# Contributing to Sonic Alchemy (VoiceCanvas)

Thank you for your interest in contributing to Sonic Alchemy! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [AI-DLC Methodology](#ai-dlc-methodology)
- [Development Setup](#development-setup)

## Code of Conduct

- Be respectful and inclusive
- Welcome constructive feedback
- Focus on what is best for the project
- Show empathy towards other contributors

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/Sonic_Alchemy.git`
3. Set up the development environment (see [Development Setup](#development-setup))
4. Create a branch for your work (see [Branching Strategy](#branching-strategy))

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch from `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the AI-DLC methodology (see below)
- Write clean, readable code
- Add comments for complex logic
- Write tests for new functionality
- Update documentation as needed

### 3. Commit Your Changes

Use conventional commit messages (see [Commit Message Format](#commit-message-format)):

```bash
git add .
git commit -m "feat(canvas): add emotion analysis from images"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request to `develop` on GitHub.

## Branching Strategy

We follow a Git Flow branching model:

### Main Branches

- **`main`** - Production-ready code (protected)
- **`develop`** - Integration branch for features (protected)

### Supporting Branches

- **`feature/*`** - New features
  - Example: `feature/canvas-emotion-analysis`
  - Example: `feature/voice-alchemy`
  
- **`bugfix/*`** - Bug fixes
  - Example: `bugfix/audio-processing-error`
  
- **`hotfix/*`** - Critical production fixes
  - Example: `hotfix/auth-security-patch`
  
- **`release/*`** - Release preparation
  - Example: `release/v1.0.0`

### Branch Naming Conventions

- Features: `feature/description`
- Bugs: `bugfix/issue-description`
- Hotfixes: `hotfix/critical-issue`
- Releases: `release/v1.0.0`

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(canvas): add emotion analysis from images

Implement Gemini Vision API integration to analyze emotions
from uploaded images and generate music prompts based on
the emotional content.

Closes #123
```

```
fix(voice): correct pitch detection algorithm

Fix issue where pitch detection was failing for low-frequency
audio samples. Updated librosa parameters for better accuracy.

Fixes #456
```

```
docs(readme): update setup instructions

Add venv setup steps and environment variable configuration
to README.md
```

## Pull Request Process

1. **Update your branch**: Rebase on latest `develop` before creating PR
2. **Fill out PR template**: Use the provided PR template
3. **Link related issues**: Reference any related issues
4. **Request reviews**: Assign at least one reviewer
5. **Address feedback**: Respond to review comments
6. **Wait for approval**: PR must be approved before merging
7. **Merge**: Squash and merge to `develop`

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Specs updated if requirements changed

## Code Review Guidelines

### For Authors

- Keep PRs focused and small when possible
- Respond to all review comments
- Be open to feedback and suggestions
- Update PR based on feedback

### For Reviewers

- Be constructive and respectful
- Focus on code quality and correctness
- Check that AI-DLC methodology is followed
- Verify tests are included
- Ensure documentation is updated

## AI-DLC Methodology

This project follows the AI-Driven Development Lifecycle (AI-DLC) methodology:

### Key Principles

1. **Spec-Driven Development**: No code without approved Specs
2. **Steering Files as Contracts**: Immutable technical constraints
3. **Mob Construction**: Technical planning before implementation

### Workflow Integration

- **Before coding**: Ensure requirements are documented in `requirements.md`
- **Design decisions**: Reference `design.md` and `ARCHITECTURE.md`
- **Technical constraints**: Follow `STEERING.md`
- **Updating Specs**: Update relevant Spec files if requirements change

### Linking PRs to Specs

When creating a PR:
- Link to related requirements in `requirements.md`
- Reference design decisions from `design.md`
- Ensure Specs are updated before merging if requirements changed

## Development Setup

### Prerequisites

- Python 3.9+ (for backend)
- Node.js 18+ (for frontend)
- Docker and Docker Compose
- Git

### Backend Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run services with Docker:
   ```bash
   docker-compose up -d postgres redis minio
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Questions?

If you have questions, please:
- Open an issue with the `question` label
- Check existing documentation
- Ask in team discussions

Thank you for contributing to Sonic Alchemy! 🎵
