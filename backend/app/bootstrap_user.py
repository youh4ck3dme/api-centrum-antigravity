# backend/app/bootstrap_user.py

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, create_engine
from app.models import User
from app.auth import get_password_hash
from app.config import settings

def bootstrap():
    # Use sync engine since our db.py is sync (for now)
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    import os
    email = os.environ.get("BOOTSTRAP_EMAIL", "admin@example.com")
    password = os.environ.get("BOOTSTRAP_PASSWORD", "changeme")
    
    stmt = select(User).where(User.email == email)
    user = session.execute(stmt).scalars().first()
    
    if not user:
        print(f"Creating user {email}...")
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True
        )
        session.add(user)
        session.commit()
        print("User created successfully!")
    else:
        print(f"User {email} already exists.")
    
    session.close()

if __name__ == "__main__":
    bootstrap()
