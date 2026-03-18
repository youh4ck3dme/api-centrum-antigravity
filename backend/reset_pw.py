
import sys
import os
import secrets
import string

# Add backend to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.auth import hash_password
from app.config import settings

def reset_password(email):
    # Try different connection strings
    base_url = settings.DATABASE_URL
    hosts_to_try = [None, "localhost", "127.0.0.1"]
    
    for host in hosts_to_try:
        db_url = base_url
        if host and "@postgres:" in db_url:
            db_url = db_url.replace("@postgres:", f"@{host}:")
        
        print(f"Attempting to connect to {db_url}...")
        try:
            engine = create_engine(db_url, connect_args={'connect_timeout': 5})
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Test connection
            session.execute(select(1))
            print("Connection successful!")
            
            stmt = select(User).where(User.email == email)
            user = session.execute(stmt).scalars().first()
            
            if not user:
                print(f"User {email} not found in this database.")
                session.close()
                continue
                
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
            user.hashed_password = hash_password(new_password)
            session.commit()
            print(f"Password reset for {email} successful.")
            session.close()
            return new_password
        except Exception as e:
            print(f"Connection to {host or 'default'} failed: {e}")
            continue
            
    return None

if __name__ == "__main__":
    email = "larsenevans@proton.me"
    new_pw = reset_password(email)
    if new_pw:
        print(f"\nSUCCESS\nNEW_PASSWORD:{new_pw}")
    else:
        print("\nFAILED: Could not connect to database or user not found.")
