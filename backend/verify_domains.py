import sys
from pathlib import Path

# Add backend and app to sys.path
backend_path = Path.cwd()
sys.path.append(str(backend_path))

try:
    from app.config import settings
    # Force reload of settings if possible or just check manually
    print(f"FORPSI_DOMAINS from settings: {settings.FORPSI_DOMAINS}")
    
    # Simulate the logic from backend/app/domains/routes.py
    ws_names = set() # Mock Websupport results for now
    domains = []
    
    if settings.FORPSI_DOMAINS:
        for name in [n.strip() for n in settings.FORPSI_DOMAINS.split(",") if n.strip()]:
            if name not in ws_names:
                domains.append({
                    "name": name,
                    "registrar": "forpsi",
                    "readonly": True,
                })

    print("Resulting domain list (Forpsi portion):")
    for d in domains:
        print(f" - {d['name']} ({d['registrar']})")
        
    if any(d['name'] == 'api-rest.nexify-studio.tech' for d in domains):
        print("\nSUCCESS: api-rest.nexify-studio.tech found in the list!")
    else:
        print("\nFAILURE: api-rest.nexify-studio.tech NOT found in the list.")

except Exception as e:
    print(f"Error: {e}")
