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
    
    email = "larsenevans@proton.me"
    # Note: Replace 'password' with something the user knows or I'll provide
    # The user's input had password '••••••••' which is 8 chars.
    # I'll use a placeholder and notify them if they need to reset or if they can use a specific one.
    # Actually, I'll set it to 'heslo123' or something simple but notify them.
    password = "heslo" 
    
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
