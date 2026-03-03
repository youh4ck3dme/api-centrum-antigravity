"""
Test suite for Websupport API integration
Tests API authentication, domain operations, and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from requests.exceptions import RequestException

from app.websupport import (
    generate_websupport_signature,
    make_websupport_request,
    WebsupportService
)
from tests import TEST_CONFIG


class TestWebsupportSignature:
    """Test Websupport API signature generation"""
    
    def test_signature_generation(self):
        """Test signature generation according to Websupport spec"""
        api_key = "test_api_key"
        secret = "test_secret"
        method = "GET"
        path = "/v2/service/domains"
        
        signature, x_date, timestamp = generate_websupport_signature(api_key, secret, method, path)
        
        assert isinstance(signature, str)
        assert len(signature) > 0
        assert isinstance(x_date, str)
        assert isinstance(timestamp, int)
        
        # Verify signature format (SHA1 hex digest)
        assert len(signature) == 40  # SHA1 hex is 40 characters
    
    def test_signature_with_query(self):
        """Test signature generation with query parameters"""
        api_key = "test_api_key"
        secret = "test_secret"
        method = "GET"
        path = "/v2/service/domains"
        query = "?page=1&limit=10"
        
        # Note: query is not included in canonical request for signature
        signature, x_date, timestamp = generate_websupport_signature(api_key, secret, method, path)
        
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_signature_different_methods(self):
        """Test signature generation with different HTTP methods"""
        api_key = "test_api_key"
        secret = "test_secret"
        path = "/v2/service/domains"
        
        methods = ["GET", "POST", "PUT", "DELETE"]
        signatures = []
        
        for method in methods:
            signature, _, _ = generate_websupport_signature(api_key, secret, method, path)
            signatures.append(signature)
        
        # Each method should produce different signature
        assert len(set(signatures)) == len(methods)
    
    def test_signature_different_paths(self):
        """Test signature generation with different paths"""
        api_key = "test_api_key"
        secret = "test_secret"
        method = "GET"
        
        paths = ["/v2/service/domains", "/v2/user/me", "/v2/service/domains/123"]
        signatures = []
        
        for path in paths:
            signature, _, _ = generate_websupport_signature(api_key, secret, method, path)
            signatures.append(signature)
        
        # Each path should produce different signature
        assert len(set(signatures)) == len(paths)


class TestWebsupportRequest:
    """Test Websupport API request handling"""
    
    @patch('app.websupport.requests.request')
    def test_successful_request(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true, "data": []}'
        mock_response.json.return_value = {"success": true, "data": []}
        mock_request.return_value = mock_response
        
        result = make_websupport_request(
            "test_key", "test_secret", "GET", "/v2/service/domains"
        )
        
        assert result == {"success": true, "data": []}
        mock_request.assert_called_once()
    
    @patch('app.websupport.requests.request')
    def test_empty_response(self, mock_request):
        """Test request with empty response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_request.return_value = mock_response
        
        result = make_websupport_request(
            "test_key", "test_secret", "GET", "/v2/service/domains"
        )
        
        assert result == {}
    
    @patch('app.websupport.requests.request')
    def test_401_error(self, mock_request):
        """Test 401 Unauthorized error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_request.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )
        
        assert exc_info.value.status_code == 401
        assert "Invalid Websupport API credentials" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_403_error(self, mock_request):
        """Test 403 Forbidden error"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_request.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )
        
        assert exc_info.value.status_code == 403
        assert "Access forbidden to Websupport API" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_429_error(self, mock_request):
        """Test 429 Too Many Requests error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_request.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded for Websupport API" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_network_error(self, mock_request):
        """Test network error handling"""
        mock_request.side_effect = RequestException("Connection failed")
        
        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )
        
        assert exc_info.value.status_code == 500
        assert "Network error" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_other_http_error(self, mock_request):
        """Test other HTTP errors"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_request.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            make_websupport_request(
                "test_key", "test_secret", "GET", "/v2/service/domains"
            )
        
        assert exc_info.value.status_code == 500
        assert "Websupport API error" in str(exc_info.value.detail)
    
    @patch('app.websupport.requests.request')
    def test_request_parameters(self, mock_request):
        """Test that request is called with correct parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_response.json.return_value = {"success": true}
        mock_request.return_value = mock_response
        
        make_websupport_request(
            "test_key", "test_secret", "GET", "/v2/service/domains"
        )
        
        # Verify request parameters
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://rest.websupport.sk/v2/service/domains"
        assert "Content-Type" in call_args[1]["headers"]
        assert "Accept" in call_args[1]["headers"]
        assert "X-Date" in call_args[1]["headers"]
        assert call_args[1]["auth"] == ("test_key", call_args[1]["headers"]["X-Date"])
        assert call_args[1]["timeout"] == 30


class TestWebsupportService:
    """Test WebsupportService class methods"""
    
    @patch('app.websupport.make_websupport_request')
    def test_get_domains(self, mock_request):
        """Test get_domains method"""
        mock_request.return_value = {"domains": [{"id": 1, "name": "example.com"}]}
        
        result = WebsupportService.get_domains()
        
        assert "domains" in result
        assert len(result["domains"]) == 1
        assert result["domains"][0]["name"] == "example.com"
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            "/v2/service/domains"
        )
    
    @patch('app.websupport.make_websupport_request')
    def test_create_domain(self, mock_request):
        """Test create_domain method"""
        domain_data = {"name": "example.com", "description": "Test domain"}
        mock_request.return_value = {"id": 123, "name": "example.com"}
        
        result = WebsupportService.create_domain(domain_data)
        
        assert result["id"] == 123
        assert result["name"] == "example.com"
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "POST",
            "/v2/service/domains",
            data=domain_data
        )
    
    @patch('app.websupport.make_websupport_request')
    def test_get_domain_details(self, mock_request):
        """Test get_domain_details method"""
        domain_id = 123
        mock_request.return_value = {"id": 123, "name": "example.com", "status": "active"}
        
        result = WebsupportService.get_domain_details(domain_id)
        
        assert result["id"] == 123
        assert result["name"] == "example.com"
        assert result["status"] == "active"
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            f"/v2/service/domains/{domain_id}"
        )
    
    @patch('app.websupport.make_websupport_request')
    def test_delete_domain(self, mock_request):
        """Test delete_domain method"""
        domain_id = 123
        mock_request.return_value = {"success": true}
        
        result = WebsupportService.delete_domain(domain_id)
        
        assert result["success"] is True
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "DELETE",
            f"/v2/service/domains/{domain_id}"
        )
    
    @patch('app.websupport.make_websupport_request')
    def test_get_user_info(self, mock_request):
        """Test get_user_info method"""
        mock_request.return_value = {"id": 1, "email": "user@example.com", "name": "Test User"}
        
        result = WebsupportService.get_user_info()
        
        assert result["id"] == 1
        assert result["email"] == "user@example.com"
        assert result["name"] == "Test User"
        mock_request.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            "/v2/user/me"
        )


class TestWebsupportIntegration:
    """Integration tests for Websupport API"""
    
    @patch('app.websupport.make_websupport_request')
    def test_full_domain_lifecycle(self, mock_request):
        """Test complete domain lifecycle"""
        # Mock responses for different operations
        mock_request.side_effect = [
            {"domains": []},  # get_domains
            {"id": 123, "name": "test.com"},  # create_domain
            {"id": 123, "name": "test.com", "status": "active"},  # get_domain_details
            {"success": true}  # delete_domain
        ]
        
        # Test domain operations
        domains = WebsupportService.get_domains()
        assert len(domains["domains"]) == 0
        
        new_domain = WebsupportService.create_domain({"name": "test.com"})
        assert new_domain["id"] == 123
        assert new_domain["name"] == "test.com"
        
        details = WebsupportService.get_domain_details(123)
        assert details["status"] == "active"
        
        delete_result = WebsupportService.delete_domain(123)
        assert delete_result["success"] is True
        
        # Verify all calls were made
        assert mock_request.call_count == 4
    
    @patch('app.websupport.make_websupport_request')
    def test_error_handling_consistency(self, mock_request):
        """Test consistent error handling across all methods"""
        mock_request.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        
        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.get_domains()
        assert exc_info.value.status_code == 401
        
        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.create_domain({"name": "test.com"})
        assert exc_info.value.status_code == 401
        
        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.get_domain_details(123)
        assert exc_info.value.status_code == 401
        
        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.delete_domain(123)
        assert exc_info.value.status_code == 401
        
        with pytest.raises(HTTPException) as exc_info:
            WebsupportService.get_user_info()
        assert exc_info.value.status_code == 401
    
    @patch('app.websupport.generate_websupport_signature')
    @patch('app.websupport.requests.request')
    def test_signature_in_request_headers(self, mock_request, mock_signature):
        """Test that signature is properly included in request headers"""
        mock_signature.return_value = ("test_signature", "20230101T120000Z", 1234567890)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"success": true}'
        mock_response.json.return_value = {"success": true}
        mock_request.return_value = mock_response
        
        WebsupportService.get_domains()
        
        # Verify signature was called
        mock_signature.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET",
            "/v2/service/domains"
        )
        
        # Verify request was called with signature in auth
        call_args = mock_request.call_args
        assert call_args[1]["auth"] == ("test_signature", "20230101T120000Z")