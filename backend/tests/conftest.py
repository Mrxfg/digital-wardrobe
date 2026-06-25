"""
Pytest configuration and shared fixtures for Digital Wardrobe tests.

Overrides the production database with a temporary SQLite database and
mocks the Telegram authentication dependency so that endpoints requiring
a logged-in user work without an actual token.
"""

import os
from collections.abc import Generator

# ---------------------------------------------------------------------------
# Override environment variables BEFORE any application code is imported.
# load_dotenv() respects already-set variables so the .env file values
# will NOT override these.
# ---------------------------------------------------------------------------
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-tests"
os.environ["ALGORITHM"] = "HS256"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.dependencies.auth import get_current_user
from app.main import app

# ---------------------------------------------------------------------------
# SQLite test engine (separate connection args for thread safety)
# ---------------------------------------------------------------------------
test_engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a clean database session for each test.

    Creates all tables before the test and drops them afterwards to
    guarantee full isolation between test cases.
    """
    Base.metadata.create_all(bind=test_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden database and auth dependencies.

    *   ``get_db`` → yields the same session created by ``db_session``.
    *   ``get_current_user`` → returns a fixed test-user payload.
    """

    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": 1,
        "telegram_id": "123456789",
    }

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def sample_item_data() -> dict:
    """Standard payload for creating a clothing item via POST /clothes/."""
    return {
        "name": "Test Shirt",
        "category": "top",
        "color": "blue",
        "season": "summer",
        "material": "cotton",
    }
