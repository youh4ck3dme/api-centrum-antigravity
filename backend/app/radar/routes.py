from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db import get_db
from .models import ObservedEndpoint, DocumentedEndpoint
from .scanner import scan_from_metrics
from ..metrics import performance_metrics

router = APIRouter(tags=["Radar"])

# Officially documented API routes — used for initial seed
KNOWN_ROUTES = [
    ("GET",    "/api/domains"),
    ("POST",   "/api/domains"),
    ("DELETE", "/api/domains/{name}"),
    ("GET",    "/api/domains/{name}/dns"),
    ("POST",   "/api/domains/{name}/dns"),
    ("DELETE", "/api/domains/{name}/dns/{record_id}"),
    ("GET",    "/api/ssl/check"),
    ("GET",    "/api/dashboard/stats"),
    ("POST",   "/api/auth/login"),
    ("POST",   "/api/auth/refresh"),
    ("GET",    "/api/users/me"),
    ("GET",    "/api/performance/stats"),
    ("GET",    "/api/monitoring/health"),
    ("GET",    "/api/backups"),
    ("POST",   "/api/backups"),
    ("GET",    "/api/vps/status"),
    ("GET",    "/api/radar/endpoints"),
    ("POST",   "/api/radar/scan"),
    ("GET",    "/api/radar/documented"),
    ("POST",   "/api/radar/documented"),
]


class DocumentedEndpointCreate(BaseModel):
    method: str
    endpoint: str


@router.get("/radar/endpoints")
def get_endpoints(db: Session = Depends(get_db)):
    observed = (
        db.query(ObservedEndpoint).order_by(ObservedEndpoint.count.desc()).all()
    )
    return {
        "endpoints": [
            {
                "id": e.id,
                "method": e.method,
                "endpoint": e.endpoint,
                "count": e.count,
                "is_shadow": e.is_shadow,
                "last_seen": e.last_seen.isoformat() if e.last_seen else None,
            }
            for e in observed
        ],
        "shadow_count": sum(1 for e in observed if e.is_shadow),
        "known_count": sum(1 for e in observed if not e.is_shadow),
        "total": len(observed),
    }


@router.post("/radar/scan")
def trigger_scan(db: Session = Depends(get_db)):
    count = scan_from_metrics(performance_metrics)
    return {"scanned": count, "message": f"Processed {count} unique endpoints"}


@router.post("/radar/seed")
def seed_documented(db: Session = Depends(get_db)):
    added = 0
    for method, endpoint in KNOWN_ROUTES:
        exists = (
            db.query(DocumentedEndpoint)
            .filter(
                DocumentedEndpoint.method == method,
                DocumentedEndpoint.endpoint == endpoint,
            )
            .first()
        )
        if not exists:
            db.add(DocumentedEndpoint(method=method, endpoint=endpoint))
            added += 1
    db.commit()
    return {"added": added, "total": len(KNOWN_ROUTES)}


@router.get("/radar/documented")
def get_documented(db: Session = Depends(get_db)):
    docs = db.query(DocumentedEndpoint).all()
    return {
        "endpoints": [
            {"id": d.id, "method": d.method, "endpoint": d.endpoint} for d in docs
        ]
    }


@router.post("/radar/documented")
def add_documented(body: DocumentedEndpointCreate, db: Session = Depends(get_db)):
    doc = DocumentedEndpoint(method=body.method.upper(), endpoint=body.endpoint)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "method": doc.method, "endpoint": doc.endpoint}


@router.delete("/radar/documented/{doc_id}")
def delete_documented(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(DocumentedEndpoint).filter(DocumentedEndpoint.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(doc)
    db.commit()
    return {"deleted": True}
