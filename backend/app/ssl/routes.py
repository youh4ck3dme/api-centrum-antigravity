# backend/app/ssl/routes.py

from fastapi import APIRouter, HTTPException, Depends
from ..schemas import SSLCertRequest
from .services import SSLService
from ..auth_neon import get_current_user_or_neon
from ..models import User

router = APIRouter()

@router.post("/ssl/generate")
async def generate_ssl_certificate(req: SSLCertRequest, current_user: User = Depends(get_current_user_or_neon)):
    """Generate SSL certificate for domain"""
    try:
        result = SSLService.generate_ssl_certificate(req.domain, req.email)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))