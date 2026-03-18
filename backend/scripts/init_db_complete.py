# backend/scripts/init_db_complete.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db import engine, Base

# Import ONLY verified models
from app import models
from app.domains import models as domain_models
from app.radar import models as radar_models
# ssl, monitoring, performance, vps, terminal, users don't seem to have models.py in the list_dir I saw

def init_db():
    print("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    print("Database schema initialized successfully.")

if __name__ == "__main__":
    init_db()
