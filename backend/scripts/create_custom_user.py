# backend/scripts/create_custom_user.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db import SessionLocal, engine, Base
from app import crud, models, auth

def create_user(email: str, password: str):
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        existing = crud.CRUDUser.get_by_email(db, email)
        if existing:
            print(f"Uživatel {email} už existuje. Aktualizujem heslo...")
            existing.hashed_password = auth.hash_password(password)
            db.commit()
            return
        user = crud.CRUDUser.create(db, email, password)
        user.is_superuser = True
        db.add(user)
        db.commit()
        print("Uživatel vytvorený:", email)
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Použitie: python create_custom_user.py <email> <password>")
    else:
        create_user(sys.argv[1], sys.argv[2])
