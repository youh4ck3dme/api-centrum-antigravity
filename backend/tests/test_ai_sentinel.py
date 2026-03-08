import pytest
from app.domains.scanner import AISentinel

def test_perfect_domain_score():
    records = [
        {"type": "TXT", "name": "", "content": "v=spf1 include:_spf.websupport.sk ~all"},
        {"type": "TXT", "name": "_dmarc", "content": "v=DMARC1; p=reject; rua=mailto:admin@example.com"},
        {"type": "TXT", "name": "google._domainkey", "content": "v=DKIM1; k=rsa; p=..."}
    ]
    result = AISentinel.audit_domain("example.com", records)
    
    assert result["security_score"] == 100
    assert result["status"] == "Excellent"
    assert result["details"]["spf_active"] is True
    assert result["details"]["dmarc_active"] is True
    assert result["details"]["dkim_active"] is True
    assert len(result["fixes_available"]) == 0

def test_missing_dmarc_and_dkim():
    records = [
        {"type": "TXT", "name": "@", "content": "v=spf1 include:spf.protection.outlook.com -all"}
    ]
    result = AISentinel.audit_domain("example.com", records)
    
    # Base 10 + 40 for SPF = 50
    assert result["security_score"] == 50
    assert result["status"] == "Good"
    assert result["details"]["spf_active"] is True
    assert result["details"]["dmarc_active"] is False
    assert result["details"]["dkim_active"] is False
    assert len(result["fixes_available"]) == 1 # _dmarc fix
    
    fix = result["fixes_available"][0]
    assert fix["name"] == "_dmarc"
    assert "v=DMARC1" in fix["content"]

def test_critical_vulnerability_no_records():
    records = [
        {"type": "A", "name": "@", "content": "1.2.3.4"},
        {"type": "MX", "name": "@", "content": "mail.example.com"}
    ]
    result = AISentinel.audit_domain("example.com", records)
    
    assert result["security_score"] == 10
    assert result["status"] == "Critical"
    assert result["details"]["spf_active"] is False
    assert result["details"]["dmarc_active"] is False
    assert result["details"]["dkim_active"] is False
    assert len(result["fixes_available"]) == 2 # SPF and DMARC fixes

def test_dkim_cname_detection():
    records = [
        {"type": "TXT", "name": "", "content": "v=spf1 ~all"},
        {"type": "CNAME", "name": "selector1._domainkey", "content": "selector1.example.com.dkim.custom.net"}
    ]
    result = AISentinel.audit_domain("example.com", records)
    
    assert result["details"]["dkim_active"] is True
    # Base 10 + 40 (SPF) + 20 (DKIM) = 70
    assert result["security_score"] == 70

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@patch("app.websupport.WebsupportService.get_dns_records")
def test_audit_endpoint_success(mock_get_dns_records):
    # Mocking the Websupport API response
    mock_get_dns_records.return_value = {
        "items": [
            {"type": "TXT", "name": "", "content": "v=spf1 include:_spf.websupport.sk ~all"}
        ]
    }
    
    # We must mock get_current_user_or_neon dependency to bypass auth
    from app.auth_neon import get_current_user_or_neon
    from app.models import User
    
    def override_get_user():
        return User(id=1, email="test@test.com", username="tester")
        
    app.dependency_overrides[get_current_user_or_neon] = override_get_user
    
    response = client.get("/api/domains/testdomain.com/audit")
    assert response.status_code == 200
    data = response.json()
    assert data["security_score"] == 50
    assert data["details"]["spf_active"] is True
    assert data["details"]["dmarc_active"] is False
    assert len(data["fixes_available"]) == 1
    
    app.dependency_overrides.clear()

@patch("app.websupport.WebsupportService.create_dns_record")
def test_autofix_endpoint_success(mock_create_dns, mock_session):
    mock_create_dns.return_value = {"status": "success", "id": 12345}
    
    from app.auth_neon import get_current_user_or_neon
    from app.db import get_db
    from app.models import User
    
    def override_get_user():
        return User(id=1, email="test@test.com", username="tester")
        
    def override_get_db():
        yield mock_session
        
    app.dependency_overrides[get_current_user_or_neon] = override_get_user
    app.dependency_overrides[get_db] = override_get_db
    
    payload = [
        {"type": "TXT", "name": "_dmarc", "content": "v=DMARC1; p=none;", "ttl": 3600, "note": "UI extra field"}
    ]
    
    response = client.post("/api/domains/testdomain.com/autofix", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["applied_fixes"] == 1
    
    # Verify the API was called without the UI 'note' field
    mock_create_dns.assert_called_once_with(
        "testdomain.com", 
        {"type": "TXT", "name": "_dmarc", "content": "v=DMARC1; p=none;", "ttl": 3600}
    )
    
    app.dependency_overrides.clear()

