"""
Test suite for Websupport API v1 integration
Tests authentication, DNS operations, and error handling
"""

import hmac
import hashlib
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from requests.exceptions import RequestException, HTTPError

from tests import TEST_CONFIG
from app.websupport import (
    _sign,
    make_websupport_request,
    WebsupportService,
)


class TestWebsupportSignature:
    """Test Websupport API v1 signature generation"""

    def test_sign_returns_tuple(self):
        """_sign returns (signature_hex, date_header, timestamp)"""
        sig, date_hdr, ts = _sign("test_secret", "GET", "/v1/user/self")
        assert isinstance(sig, str)
        assert len(sig) == 40          # SHA1 hex
        assert isinstance(date_hdr, str)
        assert isinstance(ts, int)

    def test_sign_hmac_correctness(self):
        """Signature matches manually computed HMAC-SHA1"""
        import time
        secret = "test_secret"
        method = "GET"
        path = "/v1/user/self"

        with patch("app.websupport.time.time", return_value=1700000000):
            sig, _, ts = _sign(secret, method, path)

        canonical = f"{method} {path} 1700000000"
        expected = hmac.new(
            secret.encode("UTF-8"),
            canonical.encode("UTF-8"),
            hashlib.sha1,
        ).hexdigest()
        assert sig == expected

    def test_sign_different_methods_produce_different_sigs(self):
        """Each HTTP method produces a unique signature"""
        with patch("app.websupport.time.time", return_value=1700000000):
            sigs = [_sign("secret", m, "/v1/user/self")[0] for m in ["GET", "POST", "PUT", "DELETE"]]
        assert len(set(sigs)) == 4

    def test_sign_different_paths_produce_different_sigs(self):
        """Each path produces a unique signature"""
        paths = ["/v1/user/self", "/v1/user/self/service", "/v1/user/self/zone/example.sk/record"]
        with patch("app.websupport.time.time", return_value=1700000000):
            sigs = [_sign("secret", "GET", p)[0] for p in paths]
        assert len(set(sigs)) == 3

    def test_sign_date_header_format(self):
        """Date header must be RFC 2822 (e.g. 'Sun, 01 Jan 2023 12:00:00 GMT')"""
        _, date_hdr, _ = _sign("secret", "GET", "/v1/user/self")
        # Must contain GMT and have a comma (RFC 2822)
        assert "GMT" in date_hdr
        assert "," in date_hdr


class TestWebsupportRequest:
    """Test make_websupport_request — low-level HTTP helper"""

    @patch("app.websupport.requests.request")
    def test_successful_get(self, mock_req):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = '{"id": 1}'
        mock_resp.json.return_value = {"id": 1}
        mock_req.return_value = mock_resp

        result = make_websupport_request("key", "secret", "GET", "/v1/user/self")
        assert result == {"id": 1}
        mock_req.assert_called_once()

    @patch("app.websupport.requests.request")
    def test_empty_response_returns_empty_dict(self, mock_req):
        mock_resp = Mock()
        mock_resp.status_code = 204
        mock_resp.text = ""
        mock_req.return_value = mock_resp

        result = make_websupport_request("key", "secret", "DELETE", "/v1/user/self/zone/x/record/1")
        assert result == {}

    @patch("app.websupport.requests.request")
    def test_uses_date_header_not_x_date(self, mock_req):
        """v1 must send 'Date' header, NOT 'X-Date'"""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = "{}"
        mock_resp.json.return_value = {}
        mock_req.return_value = mock_resp

        make_websupport_request("key", "secret", "GET", "/v1/user/self")

        headers = mock_req.call_args[1]["headers"]
        assert "Date" in headers
        assert "X-Date" not in headers

    @patch("app.websupport.requests.request")
    def test_auth_tuple_is_key_and_hmac(self, mock_req):
        """auth=(api_key, hmac_signature)"""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = "{}"
        mock_resp.json.return_value = {}
        mock_req.return_value = mock_resp

        make_websupport_request("my_key", "my_secret", "GET", "/v1/user/self")

        auth = mock_req.call_args[1]["auth"]
        assert auth[0] == "my_key"
        assert isinstance(auth[1], str) and len(auth[1]) == 40  # HMAC hex

    @patch("app.websupport.requests.request")
    def test_401_raises_http_exception(self, mock_req):
        mock_resp = Mock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_resp.raise_for_status.side_effect = HTTPError(response=mock_resp)
        mock_req.return_value = mock_resp

        with pytest.raises(HTTPException) as exc:
            make_websupport_request("k", "s", "GET", "/v1/user/self")
        assert exc.value.status_code == 401
        assert "Invalid Websupport API credentials" in exc.value.detail

    @patch("app.websupport.requests.request")
    def test_403_raises_http_exception(self, mock_req):
        mock_resp = Mock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_resp.raise_for_status.side_effect = HTTPError(response=mock_resp)
        mock_req.return_value = mock_resp

        with pytest.raises(HTTPException) as exc:
            make_websupport_request("k", "s", "GET", "/v1/user/self")
        assert exc.value.status_code == 403

    @patch("app.websupport.requests.request")
    def test_429_raises_http_exception(self, mock_req):
        mock_resp = Mock()
        mock_resp.status_code = 429
        mock_resp.text = "Rate limit"
        mock_resp.raise_for_status.side_effect = HTTPError(response=mock_resp)
        mock_req.return_value = mock_resp

        with pytest.raises(HTTPException) as exc:
            make_websupport_request("k", "s", "GET", "/v1/user/self")
        assert exc.value.status_code == 429

    @patch("app.websupport.requests.request")
    def test_network_error_raises_500(self, mock_req):
        mock_req.side_effect = RequestException("Connection refused")

        with pytest.raises(HTTPException) as exc:
            make_websupport_request("k", "s", "GET", "/v1/user/self")
        assert exc.value.status_code == 500
        assert "Network error" in exc.value.detail

    @patch("app.websupport.requests.request")
    def test_500_server_error(self, mock_req):
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_resp.text = "Server Error"
        mock_resp.raise_for_status.side_effect = HTTPError(response=mock_resp)
        mock_req.return_value = mock_resp

        with pytest.raises(HTTPException) as exc:
            make_websupport_request("k", "s", "GET", "/v1/user/self")
        assert exc.value.status_code == 500
        assert "Websupport API error" in exc.value.detail


class TestWebsupportService:
    """Test WebsupportService — v1 endpoints"""

    @patch("app.websupport.make_websupport_request")
    def test_verify_connection_calls_user_self(self, mock_req):
        mock_req.return_value = {"id": 123, "login": "test@example.com"}
        result = WebsupportService.verify_connection()
        assert result["id"] == 123
        mock_req.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET", "/v1/user/self", "", None,
        )

    @patch("app.websupport.make_websupport_request")
    def test_get_domains_calls_service_endpoint(self, mock_req):
        mock_req.return_value = {"items": [{"id": 8539136, "name": "h4ck3d.me", "serviceName": "domain"}]}
        result = WebsupportService.get_domains()
        assert "items" in result
        assert result["items"][0]["name"] == "h4ck3d.me"
        mock_req.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET", "/v1/user/self/service", "", None,
        )

    @patch("app.websupport.make_websupport_request")
    def test_get_dns_records(self, mock_req):
        mock_req.return_value = {
            "items": [
                {"type": "A", "id": 1, "name": "api", "content": "194.182.87.6", "ttl": 600}
            ]
        }
        result = WebsupportService.get_dns_records("h4ck3d.me")
        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "api"
        mock_req.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET", "/v1/user/self/zone/h4ck3d.me/record", "", None,
        )

    @patch("app.websupport.make_websupport_request")
    def test_create_dns_record(self, mock_req):
        record = {"type": "A", "name": "test", "content": "1.2.3.4", "ttl": 600}
        mock_req.return_value = {"status": "success", "item": record}

        result = WebsupportService.create_dns_record("h4ck3d.me", record)

        assert result["status"] == "success"
        mock_req.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "POST", "/v1/user/self/zone/h4ck3d.me/record", "", record,
        )

    @patch("app.websupport.make_websupport_request")
    def test_update_dns_record(self, mock_req):
        update = {"content": "5.6.7.8"}
        mock_req.return_value = {}
        WebsupportService.update_dns_record("h4ck3d.me", 42, update)
        mock_req.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "PUT", "/v1/user/self/zone/h4ck3d.me/record/42", "", update,
        )

    @patch("app.websupport.make_websupport_request")
    def test_delete_dns_record(self, mock_req):
        mock_req.return_value = {}
        WebsupportService.delete_dns_record("h4ck3d.me", 42)
        mock_req.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "DELETE", "/v1/user/self/zone/h4ck3d.me/record/42", "", None,
        )

    @patch("app.websupport.make_websupport_request")
    def test_get_user_info_calls_user_self(self, mock_req):
        mock_req.return_value = {"id": 1}
        WebsupportService.get_user_info()
        mock_req.assert_called_once_with(
            TEST_CONFIG["WEBSUPPORT_API_KEY"],
            TEST_CONFIG["WEBSUPPORT_SECRET"],
            "GET", "/v1/user/self", "", None,
        )

    def test_create_domain_returns_error_note(self):
        """Domain registration not supported via API — returns error dict"""
        result = WebsupportService.create_domain({"name": "new.sk"})
        assert result["status"] == "error"

    def test_delete_domain_returns_error_note(self):
        result = WebsupportService.delete_domain(123)
        assert result["status"] == "error"

    @patch("app.websupport.requests.get")
    def test_dyndns_update_uses_plain_basic_auth(self, mock_get):
        """DynDNS must NOT use HMAC — plain DYNDNS_KEY:DYNDNS_SECRET"""
        mock_resp = Mock()
        mock_resp.text = "good"
        mock_get.return_value = mock_resp

        result = WebsupportService.dyndns_update("api.h4ck3d.me", "1.2.3.4")

        assert result == "good"
        call_kwargs = mock_get.call_args[1]
        auth = call_kwargs["auth"]
        assert auth[0] == TEST_CONFIG["WEBSUPPORT_DYNDNS_KEY"]
        assert auth[1] == TEST_CONFIG["WEBSUPPORT_DYNDNS_SECRET"]
        # URL must point to dyndns.websupport.sk
        call_url = mock_get.call_args[0][0]
        assert "dyndns.websupport.sk" in call_url
        assert "api.h4ck3d.me" in call_url

    @patch("app.websupport.requests.get")
    def test_dyndns_network_error_raises_500(self, mock_get):
        mock_get.side_effect = RequestException("timeout")
        with pytest.raises(HTTPException) as exc:
            WebsupportService.dyndns_update("api.h4ck3d.me", "1.2.3.4")
        assert exc.value.status_code == 500


class TestWebsupportIntegration:
    """Integration-style tests using mock at requests level"""

    @patch("app.websupport.make_websupport_request")
    def test_full_dns_lifecycle(self, mock_req):
        mock_req.side_effect = [
            {"items": []},                              # get_dns_records
            {"status": "success", "item": {"id": 99}}, # create_dns_record
            {},                                          # update_dns_record
            {},                                          # delete_dns_record
        ]

        records = WebsupportService.get_dns_records("h4ck3d.me")
        assert records["items"] == []

        WebsupportService.create_dns_record("h4ck3d.me", {"type": "A", "name": "x", "content": "1.1.1.1", "ttl": 600})
        WebsupportService.update_dns_record("h4ck3d.me", 99, {"content": "2.2.2.2"})
        WebsupportService.delete_dns_record("h4ck3d.me", 99)

        assert mock_req.call_count == 4

    @patch("app.websupport.make_websupport_request")
    def test_error_propagation_across_methods(self, mock_req):
        mock_req.side_effect = HTTPException(status_code=401, detail="Unauthorized")

        for fn in [
            lambda: WebsupportService.verify_connection(),
            lambda: WebsupportService.get_domains(),
            lambda: WebsupportService.get_dns_records("h4ck3d.me"),
            lambda: WebsupportService.create_dns_record("h4ck3d.me", {}),
            lambda: WebsupportService.delete_dns_record("h4ck3d.me", 1),
        ]:
            with pytest.raises(HTTPException) as exc:
                fn()
            assert exc.value.status_code == 401
