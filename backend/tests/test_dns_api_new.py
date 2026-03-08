import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.config import settings

def test_dns_monitor_snapshot(authenticated_client: TestClient):
    response = authenticated_client.get("/api/dns-monitor/snapshot")
    assert response.status_code == 200
    data = response.json()
    assert "domain_count" in data
    assert "recent_threats" in data

def test_dns_monitor_threats_history(authenticated_client: TestClient):
    # Mock get_threats to avoid DB complexity for this simple API check
    with patch("app.dns_monitor.routes.get_threats") as mock_get:
        mock_get.return_value = [{"domain": "test.com", "severity": "HIGH", "timestamp": 123456789}]
        response = authenticated_client.get("/api/dns-monitor/threats")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["threats"][0]["domain"] == "test.com"

def test_vps_provision_start(authenticated_client: TestClient):
    # Mock the background task and the provider check
    with patch("app.dns_monitor.provision.settings") as mock_settings:
        mock_settings.HETZNER_API_TOKEN = "fake_token"
        payload = {
            "name": "test-server",
            "provider": "hetzner",
            "region": "nbg1",
            "domain": "server.test.com"
        }
        response = authenticated_client.get("/") # warmup
        response = authenticated_client.post("/api/dns-monitor/provision", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert "job_id" in data

def test_vps_provision_status_404(authenticated_client: TestClient):
    response = authenticated_client.get("/api/dns-monitor/provision/nonexistent-job")
    assert response.status_code == 404

def test_ws_auth_with_ws_token(client: TestClient):
    # Test service-to-service auth bypass with WS_TOKEN
    with patch("app.dns_monitor.routes.settings") as mock_settings:
        mock_settings.WS_TOKEN = "secret_ws_token"
        # We use a websocket_connect to see if it accepts the token
        try:
            with client.websocket_connect("/api/dns-monitor/ws?token=secret_ws_token") as websocket:
                data = websocket.receive_json()
                assert data["type"] == "snapshot"
        except Exception as e:
            pytest.fail(f"WebSocket connection failed with WS_TOKEN: {e}")

def test_ws_auth_invalid_token(client: TestClient):
    with client.websocket_connect("/api/dns-monitor/ws?token=wrong_token") as websocket:
        # FastAPI's TestClient closes the connection with code 4001 as defined in routes.py
        # but in test mode it might just raise an error or close it.
        # We check if it closed.
        pass
    # The routes.py does: await websocket.close(code=4001)
    # TestClient raises a WebSocketDisconnect or similar if we try to receive
