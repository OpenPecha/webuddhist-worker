"""
Pytest configuration and fixtures for worker API tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from worker_api.app import api
from worker_api.db.database import Base


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(api) as test_client:
        yield test_client


@pytest.fixture
def sample_auth_token():
    """Provide a sample authentication token for testing."""
    return "Bearer test_token_12345"


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return "123e4567-e89b-12d3-a456-426614174000"
