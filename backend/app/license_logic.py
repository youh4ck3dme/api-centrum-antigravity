import hashlib
import hmac
from datetime import datetime
from sqlalchemy.orm import Session
from .models import License, User, AuditLog

def hash_license_key(key: str) -> str:
    """Hash a license key using SHA-256."""
    return hashlib.sha256(key.encode()).hexdigest()

def verify_license_key(key: str, db_hash: str) -> bool:
    """Verify if a plain key matches the stored hash."""
    return hmac.compare_digest(hash_license_key(key), db_hash)

def activate_license(db: Session, user_id: int, key: str) -> dict:
    """
    Validate a license key and associate it with a user.
    Returns status and message.
    """
    hashed_key = hash_license_key(key)
    
    # 1. Check if key exists and is available
    license_record = db.query(License).filter(License.hash == hashed_key).first()
    
    if not license_record:
        return {"success": False, "detail": "Neplatný licenčný kľúč."}
    
    if not license_record.is_active or license_record.revoked:
        return {"success": False, "detail": "Tento kľúč bol zneplatnený."}
    
    if license_record.user_id is not None:
        if license_record.user_id == user_id:
            return {"success": True, "detail": "Licencia je už aktívna pre tento účet."}
        else:
            return {"success": False, "detail": "Tento kľúč je už priradený inému používateľovi."}

    # 2. Check if user already has an unlimited plan
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "detail": "Používateľ nebol nájdený."}

    # 3. Activate
    try:
        license_record.user_id = user_id
        license_record.activated_at = datetime.utcnow()
        user.is_unlimited = True
        
        # Log action
        log = AuditLog(
            user_id=user_id,
            action="LICENSE_ACTIVATION",
            detail=f"License {license_record.key_id} activated."
        )
        db.add(log)
        db.commit()
        return {"success": True, "detail": "Licencia úspešne aktivovaná! Váš účet je teraz UNLIMITED."}
    except Exception as e:
        db.rollback()
        return {"success": False, "detail": f"Chyba pri aktivácii: {str(e)}"}
