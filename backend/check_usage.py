import sys
from pathlib import Path

# Add backend and app to sys.path
backend_path = Path.cwd()
sys.path.append(str(backend_path))
sys.path.append(str(backend_path / "app"))

try:
    from app.domains.services import DomainService
    from app.config import settings
    
    # Mock settings if needed or ensure they are loaded
    print("Testing DomainService.list_domains()...")
    
    # The service calls Websupport API, but the prompt mentioned adding it to the list.
    # The route /api/domains in backend/app/domains/routes.py uses DomainService.list_domains()
    # AND appends Forpsi domains from settings.
    
    # Let's check the routes logic.
    import asyncio
    
    # Mocking dependencies for a direct call
    class MockUser:
        id = 1

    # We can't easily run the FastAPI app here without a full environment, 
    # but we can check if the domain listing logic (DomainService or routes) works.
    
    # Actually, the user asked to add it to the list. 
    # If the list is domains.csv, let's see where that's used.
    
    import os
    print(f"Current Directory: {os.getcwd()}")
    
    # Search for domains.csv usage in code
    import glob
    found = False
    for filename in glob.iglob('**/*.py', recursive=True):
        if 'domains.csv' in open(filename, 'r', encoding='utf-8', errors='ignore').read():
            print(f"Found domains.csv usage in: {filename}")
            found = True
    
    if not found:
        print("domains.csv not found in any .py file. Checking if it's meant for manual tracker.")

except Exception as e:
    print(f"Error: {e}")
