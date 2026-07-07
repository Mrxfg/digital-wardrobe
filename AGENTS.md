# AGENTS.md — Backend Guidelines for Coding Agents

This document provides operating instructions for AI coding agents working on the Digital Wardrobe backend repository.

> Note: This repo is part of a multi-repo project. Documentation, reports, and ADRs live in [digital_wardrobe_team_44](https://github.com/veronika1977/digital_wardrobe_team_44). The frontend lives in [digital_wardrobe_777](https://github.com/veronika1977/digital_wardrobe_777). All generated code must be reviewed by a human before merging.

---

## Project Context

This repository contains the backend for Digital Wardrobe — a Telegram Mini App for personal wardrobe management with AI-powered outfit suggestions, calendar planning, and daily wear tracking.

### Repository Map

| Repository | Purpose |
|------------|---------|
| **This repo** (`digital-wardrobe`) | FastAPI + PostgreSQL backend |
| Frontend (`digital_wardrobe_777`) | React + TypeScript frontend |
| Documentation (`digital_wardrobe_team_44`) | ADRs, reports, handover docs |

---

## Tech Stack

- Python 3.10+
- FastAPI (web framework)
- SQLAlchemy (ORM)
- PostgreSQL 15+ (production) or SQLite (local development)
- Pydantic (data validation)
- pytest (testing)
- aiohttp (async HTTP client for Telegram Bot API)
- Rembg (AI background removal, CPU-based)
- Qwen via DashScope API (AI Stylist, OpenAI-compatible endpoint)
- OpenWeatherMap API (weather integration)

---

## Repository Structure

All Python code lives in `backend/app/`:

```
digital-wardrobe/
├── .github/
│   ├── workflows/
│   │   ├── backend-ci.yml
│   │   ├── code-quality.yml
│   │   └── deploy.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── bot.py
│   │   │   ├── capsules.py
│   │   │   ├── clothes.py
│   │   │   ├── outfits.py
│   │   │   ├── tags.py
│   │   │   ├── upload.py
│   │   │   ├── wear_records.py
│   │   │   └── weather.py
│   │   ├── models/
│   │   │   ├── users.py
│   │   │   ├── clothing_item.py
│   │   │   ├── outfit.py
│   │   │   ├── outfit_item.py
│   │   │   ├── capsule.py
│   │   │   ├── capsule_item.py
│   │   │   ├── tag.py
│   │   │   ├── item_tag.py
│   │   │   └── wear_record.py
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ai_stylist.py
│   │   │   ├── auth.py
│   │   │   ├── upload.py
│   │   │   └── weather.py
│   │   ├── dependencies/
│   │   │   └── auth.py
│   │   ├── utils/
│   │   │   └── telegram_auth.py
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   │   ├── quality/
│   │   │   ├── test_qr001_response_time.py
│   │   │   ├── test_qr002_fault_tolerance.py
│   │   │   ├── test_qr004_weather_location.py
│   │   │   └── test_qr005_calendar_outfit.py
│   │   ├── test_background_removal.py
│   │   ├── test_capsules.py
│   │   ├── test_fallback_strategy.py
│   │   ├── test_items.py
│   │   ├── test_weather.py
│   │   └── conftest.py
│   ├── uploads/
│   │   ├── original/
│   │   └── processed/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   ├── setup.cfg
│   ├── Dockerfile
│   └── .env.example
├── memory/
├── docker-compose.yml
├── CONTRIBUTING.md
├── AGENTS.md
├── API_DOCUMENTATION.md
├── DEPLOYMENT.md
├── TELEGRAM_AUTH_GUIDE.md
├── TELEGRAM_BOT_SETUP.md
├── CICD_SETUP.md
└── README.md
```

---

## Essential Commands

All Python commands must be run from the `backend/` directory:

```bash
# Navigate to backend directory first
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or simpler
python main.py

# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_items.py

# Run only QRT (Quality Requirement Tests)
pytest tests/quality/

# Lint
flake8 app/ tests/

# Dead code detection
vulture app/

# Docker (from repository root, NOT backend/)
cd ..
docker-compose up -d
docker-compose logs -f backend
```

---

## Workflow for Agents

### Before Generating Code

1. Read the relevant issue or PBI in the coordination repo
2. Check existing code in the target module for style and patterns
3. Review related ADRs in [digital_wardrobe_team_44/docs/architecture/adr/](https://github.com/veronika1977/digital_wardrobe_team_44/tree/main/docs/architecture/adr)
4. Verify acceptance criteria are testable

### When Generating Code

1. Follow existing code style:
   - PEP 8 compliant (flake8)
   - Maximum 100 characters per line (see `setup.cfg`)
   - Docstrings for all public functions/classes (Google style)
   - FastAPI dependency injection for testability

2. Place code in the correct subdirectory:
   - New endpoint -> `app/routers/<domain>.py`
   - New model -> `app/models/<name>.py`
   - New schema -> `app/schemas/<name>.py`
   - Business logic -> `app/services/<name>.py`
   - Helpers -> `app/utils/<name>.py`

3. Add tests for new functionality:
   - pytest unit tests in `tests/`
   - QRT tests in `tests/quality/` if quality-related
   - Test file naming: `test_<feature>.py`

4. Update documentation:
   - Add docstrings to new functions/classes
   - Update `API_DOCUMENTATION.md` if new endpoint
   - Update related guides (`TELEGRAM_AUTH_GUIDE.md`, etc.) if relevant

5. Use Conventional Commits format:
   ```
   <type>(<scope>): <description>
   
   # Examples:
   feat(us-14): add AI outfit suggestion endpoint
   fix(auth): handle Telegram API timeout gracefully
   refactor(services): extract notification worker
   test(qrt): add QR-001 response time test
   ```

### After Generating Code

1. Run local checks from `backend/` directory:
   ```bash
   cd backend
   pytest
   pytest tests/quality/
   flake8 app/ tests/
   vulture app/
   ```

2. Ensure no new flake8 errors are introduced

3. Do not commit:
   - Secrets, credentials, or PII
   - Files in `uploads/original/` or `uploads/processed/` (gitignored)
   - `.env` files with real values

4. Link the change to the relevant issue in the PR description

---

## Sensitive Data and Safety Cautions

### Never Generate or Commit

- Real API keys, tokens, or credentials
- Database connection strings with passwords
- Personal data, PII, or customer-identifying information
- `.env` files with real values (use `.env.example` as template)
- Files in `uploads/original/` or `uploads/processed/` (user-uploaded content)
- `.env.production` modifications with real secrets

### Environment Variables Reference

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

### If You Accidentally Expose Sensitive Data

1. Stop and alert a human team member immediately
2. Do not proceed with the commit or push
3. Help rotate the exposed credential if needed
4. Document the incident in team chat

---

## Architecture and Design Constraints

### FastAPI

- Dependency injection for testability (`Depends()`)
- Pydantic models for all request/response validation
- Async endpoints where I/O-bound (DB, external APIs)
- Proper HTTP status codes and error responses
- Routers organized by domain (auth, clothes, outfits, etc.)

### SQLAlchemy

- ORM only (no raw SQL unless justified with comment)
- Relationships defined at model level with cascade rules
- Indexes on frequently queried columns
- Soft deletes via `is_deleted` flag where applicable

### Pydantic

- Request schemas for input validation
- Response schemas for output serialization
- Config classes with `from_attributes = True` for ORM compatibility
- Validators for custom business rules

### Services Layer

- Business logic in services, not in API routers
- Single responsibility per service class
- Dependency injection for external services (AI, image processing)
- Error handling with custom exceptions

### AI Integration (Qwen via DashScope)

- OpenAI-compatible client for Qwen API calls
- Timeout: 10 seconds per request
- Fallback logic: Return versatile wardrobe items if AI fails
- Caching: Cache responses for identical inputs (1 hour)
- Never send user PII to external AI APIs

### Bot Notifications (US-15)

- Polling architecture: Separate worker polls `/bot-api/users-to-notify`
- Direct HTTP to Telegram Bot API (no heavy frameworks)
- Retry logic with exponential backoff
- Idempotency: Track sent notifications in `notification_log`

### Image Processing (Rembg)

- CPU-based Rembg for background removal
- Fallback: Return original image if Rembg fails
- Store originals in `uploads/original/` and processed in `uploads/processed/`
- Both directories are gitignored

---

## API Endpoint Patterns

### Router Structure

```python
from fastapi import APIRouter, Depends
from app.services.clothes_service import ClothesService

router = APIRouter(prefix="/clothes", tags=["clothes"])

@router.get("/")
async def list_clothes(
    service: ClothesService = Depends()
):
    return await service.list_items()

@router.post("/", status_code=201)
async def create_clothes(
    item: ClothesCreateSchema,
    service: ClothesService = Depends()
):
    return await service.create_item(item)
```

### Error Handling

```python
from fastapi import HTTPException

@router.get("/{item_id}")
async def get_clothes(item_id: int, service: ClothesService = Depends()):
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

---

## Testing Patterns

### Unit Test Example

```python
import pytest
from app.services.ai_stylist import AIStylistService

@pytest.mark.asyncio
async def test_ai_stylist_generates_outfit():
    service = AIStylistService()
    wardrobe = [{"id": 1, "category": "top"}, {"id": 2, "category": "bottom"}]
    
    result = await service.generate_outfit(wardrobe, occasion="work")
    
    assert len(result["outfits"]) > 0
    assert all("items" in outfit for outfit in result["outfits"])
```

### Integration Test Example

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_clothes_endpoint():
    response = client.post(
        "/clothes",
        json={"name": "Test Shirt", "category": "top"},
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test Shirt"
```

### QRT Test Example

```python
import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_qr001_response_time():
    """API must respond within 3 seconds for standard queries."""
    start = time.time()
    response = client.get("/clothes")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 3.0, f"Response took {elapsed:.2f}s, expected < 3s"
```

---

## Documentation Links

### This Repository

- [CONTRIBUTING.md](CONTRIBUTING.md) — Human contributor workflow
- [README.md](README.md) — Project overview and quick start
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — Full API reference
- [DEPLOYMENT.md](DEPLOYMENT.md) — Production deployment guide
- [TELEGRAM_AUTH_GUIDE.md](TELEGRAM_AUTH_GUIDE.md) — Telegram auth flow
- [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md) — Bot configuration
- [CICD_SETUP.md](CICD_SETUP.md) — CI/CD pipeline setup

### Coordination Repository

- [Architecture Decision Records](https://github.com/veronika1977/digital_wardrobe_team_44/tree/main/docs/architecture/adr)
- [Customer Handover](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/customer-handover.md)
- [Testing Strategy](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/testing.md)
- [Quality Requirement Tests](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/quality-requirement-tests.md)
- [Definition of Done](https://github.com/veronika1977/digital_wardrobe_team_44/blob/main/docs/definition-of-done.md)

### Frontend Repository

- [Frontend Setup](https://github.com/veronika1977/digital_wardrobe_777) — React + TypeScript frontend

---

## Deployment

- Development: `uvicorn app.main:app --reload` (from `backend/`)
- Staging/Production: Docker Compose on VPS (from repo root)

### Docker Commands

```bash
# From repository root (NOT backend/)
docker-compose up -d
docker-compose logs -f backend
docker-compose restart backend
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## Course-Specific Reminders

- All work must be traceable to an issue or PBI in the coordination repo
- Maintain documentation: Update ADRs and testing docs in coordination repo when relevant changes are made
- Weekly reports are graded artifacts in the coordination repo
- Demo Day preparation is mandatory — ensure generated code supports the final presentation

---

## When in Doubt

1. Ask a human team member before making architectural changes
2. Prefer small, incremental changes over large refactors
3. When generating tests, prioritize critical modules and user-facing flows
4. If acceptance criteria are unclear, request clarification before proceeding
5. If unsure which repository to modify, check the issue labels or ask the team

---

*This document is a maintained artifact. It is updated when agent workflow, commands, safety constraints, or linked documentation change.*

*Last updated: 2026-07-07*
*Maintained by: Team 44 — Digital Wardrobe*