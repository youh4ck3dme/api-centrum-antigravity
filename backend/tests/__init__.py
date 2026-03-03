"""
API Centrum Backend Tests Package
Comprehensive test suite for all backend functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Import app and models
from app.main import app
from app.db import get_db, Base
from app.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

@pytest.fixture
def db_session() -> Generator:
    """Create clean database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data():
    """Test user data for registration and login"""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def admin_user_data():
    """Admin user data for testing admin functions"""
    return {
        "email": "admin@example.com", 
        "password": "adminpassword123"
    }

# Test configuration
TEST_CONFIG = {
    "WEBSUPPORT_API_KEY": "test_key",
    "WEBSUPPORT_SECRET": "test_secret",
    "DATABASE_URL": SQLALCHEMY_DATABASE_URL,
    "JWT_SECRET": "test_jwt_secret_key_for_testing",
    "JWT_EXPIRE_MINUTES": 60,
    "ENV": "testing"
}

__all__ = [
    "client",
    "db_session", 
    "test_user_data",
    "admin_user_data",
    "TEST_CONFIG",
    "override_get_db"
]