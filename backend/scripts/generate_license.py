import hashlib
import uuid
import sys
import os

# Add parent dir to path to import app modules if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_key_pair(key_id: str = None):
    """
    Generate a plain license key and its SHA-256 hash.
    """
    if not key_id:
        key_id = str(uuid.uuid4())[:8].upper()
    
    # Generate a random 16-character key
    plain_key = (str(uuid.uuid4()).replace("-", "")[:16]).upper()
    
    # Prepend key_id for easier identification (e.g. ABCD-1234-5678-...)
    full_key = f"{key_id}-{plain_key[:4]}-{plain_key[4:8]}-{plain_key[8:12]}-{plain_key[12:]}"
    
    hashed = hashlib.sha256(full_key.encode()).hexdigest()
    
    print("-" * 40)
    print(f"IDENTIFIER (key_id): {key_id}")
    print(f"PLAIN KEY (Send to user): {full_key}")
    print(f"HASH (Store in DB): {hashed}")
    print("-" * 40)
    print(f"\nSQL INSERT EXAMPLE:")
    print(f"INSERT INTO licenses (key_id, hash, is_active, revoked) ")
    print(f"VALUES ('{key_id}', '{hashed}', true, false);")
    print("-" * 40)

if __name__ == "__main__":
    kid = sys.argv[1] if len(sys.argv) > 1 else None
    generate_key_pair(kid)
