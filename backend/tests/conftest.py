"""
Pytest configuration and fixtures for API Centrum Backend tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import app and models
from app.main import app
from app.db import get_db, Base
from app.models import User, Role, AuditLog
from app.crud import CRUDUser
from app.auth_local import LocalAuthService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
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


@pytest.fixture
def authenticated_client(client, db_session, test_user_data):
    """Create authenticated test client"""
    # Create test user
    user = CRUDUser.create(
        db_session, 
        test_user_data["email"], 
        test_user_data["password"]
    )
    
    # Get access token
    auth_result = LocalAuthService.authenticate_user(
        test_user_data["email"], 
        test_user_data["password"], 
        db_session
    )
    
    access_token = auth_result["access_token"]
    
    # Create authenticated client
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client
    # Cleanup
    client.headers.pop("Authorization", None)


@pytest.fixture
def multiple_test_users(db_session):
    """Create multiple test users for testing user isolation"""
    users = []
    for i in range(3):
        user_data = {
            "email": f"user{i}@example.com",
            "password": "password123"
        }
        user = CRUDUser.create(
            db_session, 
            user_data["email"], 
            user_data["password"]
        )
        users.append(user)
    
    return users


@pytest.fixture
def test_domains_data():
    """Test domain data for domain management tests"""
    return [
        {
            "name": "example.com",
            "description": "Test domain 1"
        },
        {
            "name": "test.com", 
            "description": "Test domain 2"
        },
        {
            "name": "demo.com",
            "description": "Test domain 3"
        }
    ]


@pytest.fixture
def test_ssl_data():
    """Test SSL certificate data"""
    return {
        "domain": "example.com",
        "email": "admin@example.com"
    }


@pytest.fixture
def audit_logs_data(db_session, multiple_test_users):
    """Create test audit logs for dashboard testing"""
    from app.models import AuditLog
    
    logs = []
    for user in multiple_test_users:
        for i in range(3):
            log = AuditLog(
                user_id=user.id,
                action=f"action_{i}",
                detail=f"Test action {i} for user {user.email}"
            )
            logs.append(log)
            db_session.add(log)
    
    db_session.commit()
    return logs


# Override the dependency for testing
def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Test configuration
TEST_CONFIG = {
    "WEBSUPPORT_API_KEY": "test_key",
    "WEBSUPPORT_SECRET": "test_secret",
    "DATABASE_URL": SQLALCHEMY_DATABASE_URL,
    "JWT_SECRET": "test_jwt_secret_key_for_testing",
    "JWT_EXPIRE_MINUTES": 60,
    "ENV": "testing"
}


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return TEST_CONFIG


# Mock fixtures for external services
@pytest.fixture
def mock_websupport_service():
    """Mock WebsupportService for testing"""
    with patch('app.websupport.WebsupportService') as mock:
        yield mock


@pytest.fixture
def mock_neon_auth_service():
    """Mock NeonAuthService for testing"""
    with patch('app.neon_auth.NeonAuthService') as mock:
        yield mock


@pytest.fixture
def mock_ssl_service():
    """Mock SSLService for testing"""
    with patch('app.ssl.services.SSLService') as mock:
        yield mock


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_database():
    """Auto-cleanup database after each test"""
    yield
    # Database cleanup is handled by db_session fixture
    pass


# Test data factories
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_user_data(index=0):
        """Create test user data"""
        return {
            "email": f"testuser{index}@example.com",
            "password": "testpassword123"
        }
    
    @staticmethod
    def create_domain_data(index=0):
        """Create test domain data"""
        return {
            "name": f"testdomain{index}.com",
            "description": f"Test domain {index}"
        }
    
    @staticmethod
    def create_ssl_data(domain="example.com"):
        """Create test SSL data"""
        return {
            "domain": domain,
            "email": f"admin@{domain}"
        }


@pytest.fixture
def test_data_factory():
    """Test data factory fixture"""
    return TestDataFactory


# Error simulation fixtures
@pytest.fixture
def simulate_network_error():
    """Simulate network errors for testing"""
    from requests.exceptions import ConnectionError
    
    def _simulate_error():
        raise ConnectionError("Simulated network error")
    
    return _simulate_error


@pytest.fixture
def simulate_database_error():
    """Simulate database errors for testing"""
    from sqlalchemy.exc import SQLAlchemyError
    
    def _simulate_error():
        raise SQLAlchemyError("Simulated database error")
    
    return _simulate_error