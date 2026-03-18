import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(str(Path.cwd() / "app"))

try:
    from app.websupport import WebsupportService
    from app.config import settings
    
    print(f"Checking Websupport API with key: {settings.WEBSUPPORT_API_KEY[:8]}...")
    
    domains = WebsupportService.get_domains()
    print("Domains found in Websupport:")
    for item in domains.get("items", []):
        print(f" - {item.get('name')} (ID: {item.get('id')})")
        
except Exception as e:
    print(f"Error: {e}")
