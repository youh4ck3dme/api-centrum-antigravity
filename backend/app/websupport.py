"""
Websupport REST API v1 integration module
Docs: https://rest.websupport.sk/docs/intro

Auth: HTTP Basic with HMAC-SHA1 signature
  - Username: API key
  - Password: HMAC-SHA1(secret, "{METHOD} {path} {unix_timestamp}")
  - Date:     RFC 2822 UTC timestamp (e.g. "Sun, 01 Jan 2023 12:00:00 GMT")
"""

import hmac
import hashlib
import logging
import time

import requests
from email.utils import formatdate
from fastapi import HTTPException

from .config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://rest.websupport.sk"
DYNDNS_BASE_URL = "https://dyndns.websupport.sk"


# ---------------------------------------------------------------------------
# Signature
# ---------------------------------------------------------------------------

def _sign(secret: str, method: str, path: str) -> tuple[str, str, int]:
    """
    Compute HMAC-SHA1 signature for Websupport REST API v1.
    Canonical: "{METHOD} {path} {unix_timestamp}"
    Returns: (signature_hex, Date_header, unix_timestamp)
    """
    timestamp = int(time.time())
    canonical = f"{method} {path} {timestamp}"
    signature = hmac.new(
        secret.encode("UTF-8"),
        canonical.encode("UTF-8"),
        hashlib.sha1,
    ).hexdigest()
    date_hdr = formatdate(timestamp, usegmt=True)
    return signature, date_hdr, timestamp


# ---------------------------------------------------------------------------
# Low-level request helper
# ---------------------------------------------------------------------------

def make_websupport_request(
    api_key: str,
    secret: str,
    method: str,
    path: str,
    query: str = "",
    data: dict = None,
) -> dict:
    """
    Make an authenticated request to Websupport REST API v1.
    Raises HTTPException on errors. Returns parsed JSON dict.
    """
    signature, date_hdr, _ = _sign(secret, method, path)
    url = f"{BASE_URL}{path}{query}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Date": date_hdr,
    }

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            auth=(api_key, signature),
            json=data,
            timeout=30,
        )
        response.raise_for_status()

        if response.text:
            return response.json()
        return {}

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 500
        body = e.response.text if e.response is not None else ""
        logger.error("Websupport HTTP %s on %s %s: %s", status, method, path, body)
        if status == 401:
            raise HTTPException(status_code=401, detail="Invalid Websupport API credentials")
        if status == 403:
            raise HTTPException(status_code=403, detail="Access forbidden to Websupport API")
        if status == 429:
            raise HTTPException(status_code=429, detail="Rate limit exceeded for Websupport API")
        raise HTTPException(status_code=status, detail=f"Websupport API error {status}: {body}")

    except requests.exceptions.RequestException as e:
        logger.error("Websupport network error on %s %s: %s", method, path, e)
        raise HTTPException(status_code=500, detail=f"Network error contacting Websupport: {e}")


# ---------------------------------------------------------------------------
# Service class — maps to actual v1 endpoints
# ---------------------------------------------------------------------------

class WebsupportService:
    """
    Wrapper around Websupport REST API v1.

    Endpoints:
      GET    /v1/user/self                         – user info + auth verify
      GET    /v1/user/self/service                 – list all services/domains
      GET    /v1/user/self/zone/{domain}/record    – list DNS records
      POST   /v1/user/self/zone/{domain}/record    – create DNS record
      PUT    /v1/user/self/zone/{domain}/record/{id} – update DNS record
      DELETE /v1/user/self/zone/{domain}/record/{id} – delete DNS record
    """

    @staticmethod
    def _call(method: str, path: str, query: str = "", data: dict = None) -> dict:
        return make_websupport_request(
            settings.WEBSUPPORT_API_KEY,
            settings.WEBSUPPORT_SECRET,
            method,
            path,
            query,
            data,
        )

    # -- Auth ----------------------------------------------------------------

    @staticmethod
    def verify_connection() -> dict:
        """Verify API credentials. Returns user info on success."""
        return WebsupportService._call("GET", "/v1/user/self")

    # -- Domains / services --------------------------------------------------

    @staticmethod
    def get_domains() -> dict:
        """List all services (domains, hosting, etc.) for the account."""
        return WebsupportService._call("GET", "/v1/user/self/service")

    # -- DNS records ---------------------------------------------------------

    @staticmethod
    def get_dns_records(domain: str) -> dict:
        """List DNS records for a domain (e.g. 'h4ck3d.me')."""
        return WebsupportService._call("GET", f"/v1/user/self/zone/{domain}/record")

    @staticmethod
    def create_dns_record(domain: str, record: dict) -> dict:
        """
        Create a DNS record.
        record = {type, name, content, ttl, prio?}
        """
        return WebsupportService._call("POST", f"/v1/user/self/zone/{domain}/record", data=record)

    @staticmethod
    def update_dns_record(domain: str, record_id: int, record: dict) -> dict:
        """Update an existing DNS record by its numeric ID."""
        return WebsupportService._call(
            "PUT", f"/v1/user/self/zone/{domain}/record/{record_id}", data=record
        )

    @staticmethod
    def delete_dns_record(domain: str, record_id: int) -> dict:
        """Delete a DNS record by its numeric ID."""
        return WebsupportService._call(
            "DELETE", f"/v1/user/self/zone/{domain}/record/{record_id}"
        )

    # -- User info -----------------------------------------------------------

    @staticmethod
    def get_user_info() -> dict:
        """Return account info."""
        return WebsupportService._call("GET", "/v1/user/self")

    # -- DynDNS -------------------------------------------------------------

    @staticmethod
    def dyndns_update(hostname: str, ip: str) -> str:
        """
        Update a DynDNS record via dyndns.websupport.sk (DynDNS2 protocol).
        Uses plain HTTP Basic auth: DYNDNS_KEY:DYNDNS_SECRET (no HMAC).
        Returns the raw response text (e.g. "good", "nochg", "nohost").
        """
        url = f"{DYNDNS_BASE_URL}/nic/update?hostname={hostname}&myip={ip}"
        try:
            response = requests.get(
                url,
                headers={"Accept": "text/plain"},
                auth=(settings.WEBSUPPORT_DYNDNS_KEY, settings.WEBSUPPORT_DYNDNS_SECRET),
                timeout=15,
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error("DynDNS update error for %s: %s", hostname, e)
            raise HTTPException(status_code=500, detail=f"DynDNS update failed: {e}")

    # -- Legacy shims --------------------------------------------------------

    @staticmethod
    def get_domain_details(domain_id) -> dict:
        return WebsupportService._call("GET", "/v1/user/self/service")

    @staticmethod
    def create_domain(payload: dict) -> dict:
        return {"status": "error", "note": "Domain registration not supported via API"}

    @staticmethod
    def delete_domain(domain_id) -> dict:
        return {"status": "error", "note": "Domain deletion not supported via API"}
