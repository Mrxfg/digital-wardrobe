# Contributing to Digital Wardrobe Backend

This is the backend repository for Digital Wardrobe — a Telegram Mini App for personal wardrobe management with AI-powered outfit suggestions.

> **Note:** This repo is part of a multi-repo project. Documentation, reports, and ADRs live in [digital_wardrobe_team_44](https://github.com/veronika1977/digital_wardrobe_team_44). The frontend lives in [digital_wardrobe_777](https://github.com/veronika1977/digital_wardrobe_777).

---

## Prerequisites

- Python 3.10+
- PostgreSQL 15+ (or SQLite for local development)
- Docker & Docker Compose (for full-stack local development)
- Git
- Telegram Bot Token (from @BotFather)

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mrxfg/digital-wardrobe.git
cd digital-wardrobe
```

### 2. Navigate to backend directory

All Python commands run from the `backend/` subdirectory:

```bash
cd backend
```

### 3. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools (pytest, mypy, flake8, vulture)
```

### 5. Set up environment variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values
TELEGRAM_BOT_TOKEN=your_bot_token_here
DASHSCOPE_API_KEY=your_dashscope_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/wardrobe
SECRET_KEY=your-secret-key-here
```

### 6. Run the server

```bash
python main.py
```

Or via uvicorn (recommended for development):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 7. (Optional) Run with Docker Compose

From the repository root:

```bash
docker-compose up -d
```

This starts both the database and backend services.

---

## Repository Structure

```
digital-wardrobe/
├── .github/                      # GitHub configuration
│   ├── workflows/
│   │   ├── backend-ci.yml        # Backend CI pipeline
│   │   ├── code-quality.yml      # Code quality checks
│   │   └── deploy.yml            # Deployment workflow
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── course_task.yml
│   │   └── user_story.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/                      # Python backend code
│   ├── app/
│   │   ├── routers/              # FastAPI routers (endpoints)
│   │   │   ├── auth.py           # Telegram auth
│   │   │   ├── bot.py            # Bot-specific endpoints
│   │   │   ├── capsules.py       # Capsule wardrobes
│   │   │   ├── clothes.py        # Wardrobe CRUD
│   │   │   ├── outfits.py        # Outfit management
│   │   │   ├── tags.py           # Tag management
│   │   │   ├── upload.py         # Image upload + Rembg
│   │   │   ├── wear_records.py   # Wear tracking
│   │   │   └── weather.py        # Weather integration
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── users.py
│   │   │   ├── clothing_item.py
│   │   │   ├── outfit.py
│   │   │   ├── outfit_item.py
│   │   │   ├── capsule.py
│   │   │   ├── capsule_item.py
│   │   │   ├── tag.py
│   │   │   ├── item_tag.py
│   │   │   └── wear_record.py
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Business logic
│   │   │   ├── ai_stylist.py     # Qwen AI integration
│   │   │   ├── auth.py           # Authentication logic
│   │   │   ├── upload.py         # Image processing (Rembg)
│   │   │   └── weather.py        # OpenWeatherMap integration
│   │   ├── dependencies/         # FastAPI dependencies
│   │   │   └── auth.py           # Auth dependency injection
│   │   ├── utils/                # Helper functions
│   │   │   └── telegram_auth.py  # Telegram auth utilities
│   │   ├── database.py           # DB connection & session
│   │   └── main.py               # FastAPI app entry point
│   ├── tests/                    # pytest tests
│   │   ├── quality/              # Quality Requirement Tests (QRT)
│   │   │   ├── test_qr001_response_time.py
│   │   │   ├── test_qr002_fault_tolerance.py
│   │   │   ├── test_qr004_weather_location.py
│   │   │   └── test_qr005_calendar_outfit.py
│   │   ├── test_background_removal.py
│   │   ├── test_capsules.py
│   │   ├── test_fallback_strategy.py
│   │   ├── test_items.py
│   │   ├── test_weather.py
│   │   └── conftest.py           # Test fixtures
│   ├── uploads/                  # Uploaded images
│   │   ├── original/             # Original uploads
│   │   └── processed/            # Rembg-processed images
│   ├── Dockerfile                # Production container
│   ├── requirements.txt          # Production dependencies
│   ├── requirements-dev.txt      # Development dependencies
│   ├── pyproject.toml            # Python project config
│   ├── setup.cfg                 # Linting config (flake8, mypy)
│   └── .env.example              # Environment variables template
├── memory/                       # AI agent context memory
├── docker-compose.yml            # Full-stack local development
├── CONTRIBUTING.md
├── AGENTS.md
├── API_DOCUMENTATION.md
├── DEPLOYMENT.md
├── TELEGRAM_AUTH_GUIDE.md
├── TELEGRAM_BOT_SETUP.md
└── README.md
```

---

## Branching Strategy

We use issue-linked branches:

- **Branch naming:** `<issue-number>-short-description`
- **Examples:** `217-ai-stylist-endpoint`, `218-bot-notification-worker`
- **Create PR against:** `main`

---

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear history and automated changelogs.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature (user-facing) |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code change, no new feature/bugfix |
| `test` | Adding/updating tests |
| `chore` | Build, config, tooling (no production code) |

### Examples

```bash
# Good:
feat(us-14): add AI outfit suggestion endpoint
fix(auth): handle Telegram API timeout gracefully
refactor(services): extract notification worker
test(qrt): add QR-001 response time test
chore(deps): update FastAPI to 0.104

# Bad:
update code
fixed bug
wip
```

---

## Pull Request Process

### Before Creating a PR

1. Create an issue (or link existing one) describing the change
2. Branch from `main`
3. Write tests for new functionality
4. Run local checks from `backend/` directory:
   ```bash
   cd backend
   pytest
   pytest tests/quality/  # QRT tests
   flake8 app/ tests/
   ```

### PR Template

Every PR must include:

```markdown
## Description
[Brief description of changes]

## Related Issue
Closes #<issue_number>

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring
- [ ] Tests

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] QRT tests pass (if applicable)
- [ ] Manual testing completed (API endpoint tested)

## Checklist
- [ ] Code follows PEP 8 style guide
- [ ] Self-reviewed my code
- [ ] Added docstrings for new functions/classes
- [ ] Updated API documentation (if new endpoint)
- [ ] No new flake8 errors
```

### Review Process

1. **Assign reviewers:** At least 1 team member (different from implementer)
2. **CI checks must pass:** pytest, flake8, QRT tests, coverage
3. **Address feedback:** Respond to all review comments
4. **Squash and merge:** Use "Squash and merge" for clean history
5. **Delete branch:** After merge, delete feature branch

---

## Definition of Done

A PBI/issue is "Done" when:

- [ ] Code is merged to `main`
- [ ] All tests pass (unit + integration + QRT)
- [ ] CI pipeline is green
- [ ] API documentation updated (Swagger/OpenAPI)
- [ ] Peer review completed
- [ ] No critical security issues
- [ ] Feature tested in staging environment

See [Definition of Done](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/definition-of-done.md) for details.

---

## Testing

### Run Tests

All test commands run from the `backend/` directory:

```bash
cd backend

# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_items.py

# Run only QRT (Quality Requirement Tests)
pytest tests/quality/

# Run specific QRT
pytest tests/quality/test_qr001_response_time.py

# Run with verbose output
pytest -v

# Run only unit tests (exclude QRT)
pytest tests/ --ignore=tests/quality/
```

### Testing Requirements

- **Unit tests** for all services and utilities
- **Integration tests** for all API endpoints
- **QRT tests** for quality requirements (QR-001, QR-002, QR-004, QR-005)
- **Minimum 30% overall coverage** (QRT-001)
- **Critical modules:** >=70% coverage
- **All new endpoints must have tests**

### Test Structure

```
backend/tests/
├── quality/                          # Quality Requirement Tests
│   ├── test_qr001_response_time.py   # API response time < 3s
│   ├── test_qr002_fault_tolerance.py # Graceful degradation
│   ├── test_qr004_weather_location.py # Weather geolocation
│   └── test_qr005_calendar_outfit.py # Calendar sync
├── test_background_removal.py        # Rembg integration
├── test_capsules.py                  # Capsule CRUD
├── test_fallback_strategy.py         # AI fallback logic
├── test_items.py                     # Clothing items
├── test_weather.py                   # Weather integration
└── conftest.py                       # Shared fixtures
```

### Coverage Reports

Coverage reports are generated in `backend/htmlcov/`. Open `htmlcov/index.html` in a browser to view.

---

## Code Style

### Python

- **PEP 8** compliant (enforced by flake8)
- **Maximum line length:** 100 characters (see `setup.cfg`)
- **Docstrings** for all public functions/classes (Google style)
- **Type hints** encouraged (mypy optional)

### FastAPI

- **Dependency injection** for testability (`Depends()`)
- **Pydantic models** for all request/response validation
- **Async endpoints** where I/O-bound (DB, external APIs)
- **Proper HTTP status codes** and error responses

### Database

- **SQLAlchemy ORM** only (no raw SQL unless justified)
- **Cascade deletes** configured at ORM level
- **Indexes** on frequently queried columns

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/telegram` | Telegram Mini App authentication |
| GET | `/auth/me` | Current user info |
| GET/POST | `/clothes` | List/add clothing items |
| PATCH/DELETE | `/clothes/{id}` | Update/delete item |
| POST | `/clothes/{id}/restore` | Restore from trash |
| GET/POST | `/outfits` | List/create outfits |
| POST | `/outfits/{id}/items` | Add item to outfit |
| GET/POST | `/capsules` | List/create capsules |
| GET/POST | `/wear-records` | Wear tracking |
| GET | `/weather` | Current weather by location |
| POST | `/upload/image` | Image upload + Rembg processing |
| GET | `/bot-api/users-to-notify` | Bot worker endpoint (US-15) |
| GET | `/health` | Health check |

Full API documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=       # From @BotFather
DASHSCOPE_API_KEY=        # From DashScope Console (Qwen AI)
DATABASE_URL=             # PostgreSQL connection string (or SQLite for dev)
SECRET_KEY=               # JWT signing key

# Optional
LOG_LEVEL=INFO            # Logging level
CORS_ORIGINS=*            # Allowed CORS origins
OPENWEATHER_API_KEY=      # For weather integration
BOT_JWT_TOKEN=            # Service account token for bot worker
```

### Never Commit

- `.env` files with real credentials
- `.env.production` (already committed, but do not modify with real secrets)
- API keys, tokens, or passwords
- Database connection strings with credentials
- Personal data or PII

### If You Accidentally Expose Sensitive Data

1. **Stop and alert** a human team member immediately
2. **Do not proceed** with the commit or push
3. **Help rotate** the exposed credential if needed
4. **Document the incident** in team chat

---

## Image Uploads

Uploaded images are stored in `backend/uploads/`:

- `original/` — Original uploaded files (kept for backup)
- `processed/` — Rembg-processed images (background removed)

### Important

- Both directories are gitignored (contain user-uploaded content)
- `.gitkeep` files preserve the directory structure
- Never commit real uploaded images to git
- In production, consider using S3 or similar object storage

---

## Architecture & ADRs

See [digital_wardrobe_team_44/docs/architecture/adr/](https://github.com/veronika1977/digital_wardrobe_team_44/tree/main/docs/architecture/adr)

Key ADRs for backend:
- [ADR-001: FastAPI + PostgreSQL](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/architecture/adr/ADR-001-fastapi-backend.md)
- [ADR-002: Rembg Background Removal](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/architecture/adr/ADR-002-rembg-background-removal.md)
- [ADR-004: Qwen AI Strategy](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/architecture/adr/ADR-004-ai-strategy.md)
- [ADR-005: Bot Architecture](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/architecture/adr/ADR-005-bot-architecture.md)

---

## AI Assistant Rules

See [AGENTS.md](AGENTS.md) in this repo.

---

## Deployment

- **Development:** `python main.py` or `uvicorn app.main:app --reload` (from `backend/`)
- **Staging/Production:** Docker Compose on VPS

### Docker Commands

From repository root:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop all services
docker-compose down

# Rebuild after dependency changes
docker-compose up -d --build
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions.

---

## Related Documentation

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — Full API reference
- [DEPLOYMENT.md](DEPLOYMENT.md) — Production deployment guide
- [TELEGRAM_AUTH_GUIDE.md](TELEGRAM_AUTH_GUIDE.md) — Telegram auth flow
- [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md) — Bot configuration
- [CICD_SETUP.md](CICD_SETUP.md) — CI/CD pipeline setup

---

## Getting Help

- **Questions?** Ask in team chat or create a `question` issue
- **Code review stuck?** Tag `@veronika1977` (Scrum Master)
- **Architecture decisions?** Refer to `docs/architecture/adr/` or create new ADR
- **Course requirements?** Check Assignment 6 spec in Moodle

---

## Course-Specific Notes

This repository is part of **Innopolis University Software Project course**. Key reminders:

- **All work must be traceable:** Link every PR to a PBI/issue
- **Maintain documentation:** Update ADRs and testing docs in coordination repo when relevant changes are made
- **Weekly reports** (`reports/week6/`, `reports/week7/`) are graded artifacts in the coordination repo
- **Demo Day preparation** is mandatory — ensure generated code supports the final presentation

---

*This document is a maintained artifact. It is updated when contribution workflow, verification commands, review expectations, or linked documentation change.*

*Last updated: 2026-07-07*
*Maintained by: Team 44 — Digital Wardrobe*