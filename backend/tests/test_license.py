import pytest
from sqlalchemy.orm import Session
from app.models import License, User
from app.license_logic import hash_license_key, activate_license

def test_hash_license_key():
    key = "TEST-KEY-1234"
    h1 = hash_license_key(key)
    h2 = hash_license_key(key)
    assert h1 == h2
    assert h1 != key

def test_activate_license_success(db_session: Session):
    # 1. Setup - Create a user and a license key
    user = User(email="test_license@example.com", hashed_password="pw", is_unlimited=False)
    db_session.add(user)
    db_session.commit()
    
    plain_key = "PRO-TEST-VALID-KEY"
    hashed = hash_license_key(plain_key)
    license_rec = License(key_id="TEST01", hash=hashed, is_active=True)
    db_session.add(license_rec)
    db_session.commit()
    
    # 2. Act - Activate
    result = activate_license(db_session, user.id, plain_key)
    
    # 3. Assert
    assert result["success"] is True
    assert "úspešne aktivovaná" in result["detail"]
    
    # Refresh from DB
    db_session.refresh(user)
    db_session.refresh(license_rec)
    assert user.is_unlimited is True
    assert license_rec.user_id == user.id

def test_activate_license_invalid_key(db_session: Session):
    user = User(email="test_fail@example.com", hashed_password="pw")
    db_session.add(user)
    db_session.commit()
    
    result = activate_license(db_session, user.id, "NON-EXISTENT-KEY")
    assert result["success"] is False
    assert "Neplatný" in result["detail"]

def test_activate_license_already_used(db_session: Session):
    # Setup two users and one key
    u1 = User(email="u1@ex.com", hashed_password="p")
    u2 = User(email="u2@ex.com", hashed_password="p")
    db_session.add_all([u1, u2])
    db_session.commit()
    
    key = "SHARED-KEY"
    h = hash_license_key(key)
    license_rec = License(key_id="SH01", hash=h, user_id=u1.id, is_active=True)
    db_session.add(license_rec)
    db_session.commit()
    
    # Try to activate for u2
    result = activate_license(db_session, u2.id, key)
    assert result["success"] is False
    assert "už priradený inému" in result["detail"]
