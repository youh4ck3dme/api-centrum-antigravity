from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict

from .db import get_db
from .auth_neon import get_current_user_or_neon
from .models import User
from .license_logic import activate_license

router = APIRouter(tags=["License System"])

@router.post("/license/activate")
async def api_activate_license(
    payload: Dict[str, str] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_neon)
):
    """
    Activate a license key for the current user.
    """
    key = payload.get("key")
    if not key:
        raise HTTPException(status_code=400, detail="Chýba licenčný kľúč.")
        
    result = activate_license(db, current_user.id, key)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["detail"])
        
    return result

@router.get("/license/status")
async def get_license_status(
    current_user: User = Depends(get_current_user_or_neon)
):
    """
    Check current user's license status.
    """
    return {
        "is_unlimited": current_user.is_unlimited,
        "user_email": current_user.email
    }
