# backend/tests/test_ai_autopilot.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

# Mocked AI response
MOCK_AUDIT_RESPONSE = {
    "score": 45,
    "issues": ["Missing DMARC", "Incomplete SPF"],
    "recommendations": [
        {
            "type": "TXT",
            "name": "_dmarc",
            "content": "v=DMARC1; p=none;",
            "reason": "Crucial for anti-spoofing",
            "is_fixable": True
        }
    ]
}

@pytest.fixture
def mock_user():
    with patch("app.deps.get_current_user", return_value={"id": 1, "is_unlimited": True}):
        yield

@pytest.mark.asyncio
async def test_ai_audit_endpoint(mock_user):
    """Test the AI audit endpoint with mocked OpenAI call."""
    with patch("app.ai_service.AIService.generate_dns_audit", new_callable=AsyncMock) as mock_audit:
        mock_audit.return_value = MOCK_AUDIT_RESPONSE
        
        # We need a domain that might be in the snapshot or we mock the snapshot
        with patch("app.ai_routes.dns_snapshot", {"test.com": []}):
            response = client.post("/api/ai/audit/test.com", headers={"Authorization": "Bearer mock_token"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["score"] == 45
            assert "Missing DMARC" in data["issues"]

@pytest.mark.asyncio
async def test_ai_chat_endpoint(mock_user):
    """Test the AI chat endpoint."""
    with patch("app.ai_service.AIService.dns_chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "I recommend checking your SPF record."
        
        payload = {
            "query": "How are my emails doing?",
            "domain": "test.com",
            "history": []
        }
        
        response = client.post("/api/ai/chat", json=payload)
        
        assert response.status_code == 200
        assert response.json()["response"] == "I recommend checking your SPF record."

@pytest.mark.asyncio
async def test_apply_fix_endpoint(mock_user):
    """Test applying a fix (Websupport call)."""
    with patch("app.websupport.WebsupportService.create_dns_record") as mock_ws:
        mock_ws.return_value = {"status": "success", "id": 12345}
        
        payload = {
            "domain": "test.com",
            "record": {
                "type": "TXT",
                "name": "_dmarc",
                "content": "v=DMARC1; p=none;",
                "ttl": 3600
            }
        }
        
        response = client.post("/api/ai/fix", json=payload)
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_ws.assert_called_once()
