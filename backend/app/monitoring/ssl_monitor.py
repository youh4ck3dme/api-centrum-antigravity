# backend/app/monitoring/ssl_monitor.py

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import List

from ..websupport import WebsupportService
from ..config import settings
from .tasks import check_ssl_expiry
from ..ssl.services import SSLService

logger = logging.getLogger(__name__)

# In-memory storage for SSL status
ssl_status_cache = {}

async def ssl_poll_loop():
    """
    Background loop to check SSL certificates for all domains.
    Runs once every 24 hours by default.
    """
    logger.info("SSL Monitor loop started")
    
    interval = getattr(settings, "SSL_CHECK_INTERVAL", 86400) # 24 hours
    
    while True:
        try:
            logger.info("Starting SSL check cycle")
            
            # 1. Fetch domain list
            ws_result = await asyncio.get_event_loop().run_in_executor(None, WebsupportService.get_domains)
            items = ws_result.get("items", [])
            domains = [
                x.get("name") for x in items
                if x.get("serviceName") == "domain" and x.get("name")
            ]
            
            # 2. Check each domain
            for domain in domains:
                try:
                    res = check_ssl_expiry(domain)
                    ssl_status_cache[domain] = res
                    
                    if res["status"] == "success":
                        days = res["days_remaining"]
                        logger.info(f"SSL for {domain}: {days} days remaining")
                        
                        # 3. Auto-renewal if < 30 days
                        if days < 30:
                            logger.warning(f"SSL for {domain} is expiring in {days} days! Triggering auto-renewal.")
                            email = settings.CERTBOT_EMAIL or "admin@mojadomena.sk"
                            renewal_res = await asyncio.get_event_loop().run_in_executor(
                                None, lambda: SSLService.generate_ssl_certificate(domain, email)
                            )
                            logger.info(f"Renewal result for {domain}: {renewal_res}")
                    else:
                        logger.error(f"Failed to check SSL for {domain}: {res.get('message')}")
                        
                except Exception as e:
                    logger.error(f"Error checking SSL for {domain}: {e}")
            
            logger.info("SSL check cycle completed")
            
        except Exception as e:
            logger.error(f"General error in SSL monitor loop: {e}")
            
        await asyncio.sleep(interval)
