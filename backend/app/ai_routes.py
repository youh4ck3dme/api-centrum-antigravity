# backend/app/ai_routes.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel

from .deps import get_current_user
from .ai_service import AIService, VPSContext
from .dns_monitor.monitor import dns_snapshot
from .websupport import WebsupportService

router = APIRouter(tags=["AI Autopilot"])

VPS_KEYWORDS = {
    "docker", "kontajner", "server", "disk", "pamäť", "pamat", "memory",
    "cpu", "load", "uptime", "free", "df", "log", "process", "restart",
    "reštart", "vps", "ram", "port", "container", "stats", "status",
    "running", "stopped", "exit", "bezi", "beži", "kontajnery", "procesy",
    "volne", "voľné", "využitie", "vyuzitie",
}

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
    """Troubleshoot DNS/VPS via AI chat."""
    records = dns_snapshot.get(req.domain, [])
    context = f"Domain: {req.domain}\nRecords: {str(records)}"

    # Fetch VPS context only when query contains relevant keywords
    vps_data = ""
    query_lower = req.query.lower()
    if any(kw in query_lower for kw in VPS_KEYWORDS):
        vps_data = await VPSContext.gather()

    try:
        response = await AIService.dns_chat(req.query, context, req.history, vps_data)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/fix")
async def apply_fix(req: FixRequest, user=Depends(get_current_user)):
    """Apply an AI-recommended DNS fix to Websupport."""
    try:
        result = WebsupportService.create_dns_record(req.domain, req.record)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply fix: {str(e)}")
