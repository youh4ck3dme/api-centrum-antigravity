# backend/app/domains/routes.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from ..schemas import DomainCreate
from .services import DomainService
from ..auth_neon import get_current_user_or_neon
from ..auth_neon import get_current_user_or_neon
from ..models import User
from .scanner import AISentinel
router = APIRouter()

@router.get("/domains")
async def get_domains(current_user: User = Depends(get_current_user_or_neon)):
    """Get list of domains from Websupport API"""
    try:
        result = DomainService.list_domains()
        # Filter only domain-type services and normalize to frontend-expected shape
        items = result.get("items", [])
        domains = [
            {
                "id": x["id"],
                "name": x["name"],
                "status": x.get("status", "active"),
                "expireTime": x.get("expireTime"),
                "autoExtend": x.get("autoExtend"),
                "serviceName": x.get("serviceName", "domain"),
            }
            for x in items
            if x.get("serviceName") == "domain" and x.get("name")
        ]
        return {"domains": domains, "total": len(domains)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/domains")
async def create_domain(domain: DomainCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """Create new domain via Websupport API"""
    try:
        res = DomainService.create_domain(domain.model_dump())
        
        # Audit log
        new_log = models.AuditLog(user_id=current_user.id, action="create_domain", detail=f"Created domain {domain.name}")
        db.add(new_log)
        db.commit()
        
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains/{domain_name}/dns")
async def get_domain_dns(domain_name: str, current_user: User = Depends(get_current_user_or_neon)):
    """Get DNS records for a domain"""
    try:
        from ..websupport import WebsupportService
        result = WebsupportService.get_dns_records(domain_name)
        return {"records": result.get("items", []), "domain": domain_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/domains/{domain_name}/dns")
async def create_domain_dns(domain_name: str, record: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """Create DNS record for a domain"""
    try:
        from ..websupport import WebsupportService
        result = WebsupportService.create_dns_record(domain_name, record)
        new_log = models.AuditLog(user_id=current_user.id, action="create_dns_record", detail=f"Created {record.get('type')} record {record.get('name')} for {domain_name}")
        db.add(new_log)
        db.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/domains/{domain_name}/dns/{record_id}")
async def delete_domain_dns(domain_name: str, record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """Delete DNS record"""
    try:
        from ..websupport import WebsupportService
        result = WebsupportService.delete_dns_record(domain_name, record_id)
        new_log = models.AuditLog(user_id=current_user.id, action="delete_dns_record", detail=f"Deleted DNS record {record_id} from {domain_name}")
        db.add(new_log)
        db.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains/{domain_id}")
async def get_domain_details(domain_id: int, current_user: User = Depends(get_current_user_or_neon)):
    """Get domain details from Websupport API"""
    try:
        return DomainService.get_domain_details(domain_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/domains/{domain_id}")
async def delete_domain(domain_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """Delete domain via Websupport API"""
    try:
        DomainService.delete_domain(domain_id)
        
        # Audit log
        new_log = models.AuditLog(user_id=current_user.id, action="delete_domain", detail=f"Deleted domain ID {domain_id}")
        db.add(new_log)
        db.commit()
        
        return {"success": True, "message": "Domain deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains/{domain_name}/audit")
async def audit_domain_security(domain_name: str, current_user: User = Depends(get_current_user_or_neon)):
    """AI Sentinel: Audit domain DNS records for email security (SPF, DKIM, DMARC)"""
    try:
        from ..websupport import WebsupportService
        result = WebsupportService.get_dns_records(domain_name)
        records = result.get("items", [])
        
        audit_result = AISentinel.audit_domain(domain_name, records)
        return audit_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/domains/{domain_name}/autofix")
async def autofix_domain_security(domain_name: str, fixes: list[dict], db: Session = Depends(get_db), current_user: User = Depends(get_current_user_or_neon)):
    """AI Sentinel: Apply recommended DNS fixes automatically via Websupport"""
    try:
        from ..websupport import WebsupportService
        results = []
        for fix in fixes:
            # We assume the frontend passes the required fields: type, name, content, ttl
            # Remove any extra UI fields like 'note' before sending to API
            api_payload = {
                "type": fix.get("type"),
                "name": fix.get("name"),
                "content": fix.get("content"),
                "ttl": fix.get("ttl", 3600)
            }
            res = WebsupportService.create_dns_record(domain_name, api_payload)
            results.append(res)
            
            # Log the action
            new_log = models.AuditLog(user_id=current_user.id, action="ai_sentinel_autofix", detail=f"Auto-fixed {api_payload['type']} record for {domain_name}")
            db.add(new_log)
        
        db.commit()
        return {"success": True, "applied_fixes": len(results), "results": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
