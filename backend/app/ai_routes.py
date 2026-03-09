# backend/app/ai_routes.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel

from .deps import get_current_user
from .ai_service import AIService
from .dns_monitor.monitor import dns_snapshot
from .websupport import WebsupportService

router = APIRouter(tags=["AI Autopilot"])

class ChatRequest(BaseModel):
    query: str
    domain: str
    history: List[Dict[str, str]] = []

class FixRequest(BaseModel):
    domain: str
    record: Dict[str, Any] # {type, name, content, ttl}

@router.post("/ai/audit/{domain}")
async def audit_domain(domain: str, user=Depends(get_current_user)):
    """Trigger AI DNS security audit."""
    records = dns_snapshot.get(domain, [])
    if not records:
        # Try to fetch if not in snapshot
        try:
            records = await WebsupportService.get_dns_records(domain)
        except:
            raise HTTPException(status_code=404, detail="Domain records not found")
    
    try:
        audit = await AIService.generate_dns_audit(domain, records)
        return audit
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/chat")
async def chat_dns(req: ChatRequest, user=Depends(get_current_user)):
    """Troubleshoot DNS via AI chat."""
    records = dns_snapshot.get(req.domain, [])
    context = f"Domain: {req.domain}\nRecords: {str(records)}"
    
    try:
        response = await AIService.dns_chat(req.query, context, req.history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/fix")
async def apply_fix(req: FixRequest, user=Depends(get_current_user)):
    """Apply an AI-recommended DNS fix to Websupport."""
    if not user.get("is_unlimited"):
        # We might want to restrict this to PRO users in the future, 
        # but for now let's just proceed or check a flag.
        pass

    try:
        result = WebsupportService.create_dns_record(req.domain, req.record)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply fix: {str(e)}")
