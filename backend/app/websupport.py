"""
Websupport API integration module
Handles authentication and API requests to Websupport REST API
"""

import hmac
import hashlib
import time
from datetime import datetime, timezone
import requests
from fastapi import HTTPException
from .config import settings

def generate_websupport_signature(api_key: str, secret: str, method: str, path: str) -> tuple:
    """
    Generate Websupport API signature according to their documentation
    """
    timestamp = int(time.time())
    canonical_request = f"{method} {path} {timestamp}"
    signature = hmac.new(
        bytes(secret, 'UTF-8'),
        bytes(canonical_request, 'UTF-8'),
        hashlib.sha1
    ).hexdigest()
    x_date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return signature, x_date, timestamp

def make_websupport_request(api_key: str, secret: str, method: str, path: str, query: str = "", data: dict = None):
    """
    Make authenticated request to Websupport API
    """
    signature, x_date, timestamp = generate_websupport_signature(api_key, secret, method, path)
    api_url = f"https://rest.websupport.sk{path}{query}"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Date": x_date,
    }
    
    auth = (api_key, signature)
    
    try:
        response = requests.request(
            method, 
            api_url, 
            headers=headers, 
            auth=auth, 
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        if response.text:
            return response.json()
        return {}
        
    except requests.exceptions.RequestException as e:
        # Log the error for debugging
        print(f"Websupport API Error: {str(e)}")
        
        # Provide more specific error messages
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            if status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid Websupport API credentials")
            elif status_code == 403:
                raise HTTPException(status_code=403, detail="Access forbidden to Websupport API")
            elif status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded for Websupport API")
            else:
                raise HTTPException(status_code=status_code, detail=f"Websupport API error: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")

class WebsupportService:
    """Service class for Websupport API operations"""
    
    @staticmethod
    def get_domains():
        """Get list of domains from Websupport"""
        return make_websupport_request(
            settings.WEBSUPPORT_API_KEY, 
            settings.WEBSUPPORT_SECRET, 
            "GET", 
            "/v2/service/domains"
        )
    
    @staticmethod
    def create_domain(payload: dict):
        """Create new domain via Websupport API"""
        return make_websupport_request(
            settings.WEBSUPPORT_API_KEY, 
            settings.WEBSUPPORT_SECRET, 
            "POST", 
            "/v2/service/domains",
            data=payload
        )
    
    @staticmethod
    def get_domain_details(domain_id: int):
        """Get domain details from Websupport"""
        return make_websupport_request(
            settings.WEBSUPPORT_API_KEY, 
            settings.WEBSUPPORT_SECRET, 
            "GET", 
            f"/v2/service/domains/{domain_id}"
        )
    
    @staticmethod
    def delete_domain(domain_id: int):
        """Delete domain via Websupport API"""
        return make_websupport_request(
            settings.WEBSUPPORT_API_KEY, 
            settings.WEBSUPPORT_SECRET, 
            "DELETE", 
            f"/v2/service/domains/{domain_id}"
        )
    
    @staticmethod
    def get_user_info():
        """Get user information from Websupport"""
        return make_websupport_request(
            settings.WEBSUPPORT_API_KEY, 
            settings.WEBSUPPORT_SECRET, 
            "GET", 
            "/v2/user/me"
        )