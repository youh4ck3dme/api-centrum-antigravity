# backend/app/dns_monitor/persistence.py

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .threat_model import Threat

logger = logging.getLogger(__name__)


def save_threat(threat: dict) -> None:
    """Persist a single threat dict to the database (sync)."""
    db: Session = SessionLocal()
    try:
        t = Threat(
            domain=threat["domain"],
            record_type=threat.get("record_type"),
            severity=threat.get("severity", "MEDIUM"),
            message=threat.get("message"),
            old_value=threat.get("old_value"),
            new_value=threat.get("new_value"),
            timestamp=threat.get("timestamp", 0),
        )
        db.add(t)
        db.commit()
    except Exception as e:
        logger.error("Failed to persist threat: %s", e)
        db.rollback()
    finally:
        db.close()


def get_threats(
    limit: int = 100,
    domain: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[dict]:
    """Query persisted threats with optional filters (sync)."""
    db: Session = SessionLocal()
    try:
        q = db.query(Threat).order_by(Threat.timestamp.desc())
        if domain:
            q = q.filter(Threat.domain == domain)
        if severity:
            q = q.filter(Threat.severity == severity)
        rows = q.limit(limit).all()
        return [
            {
                "id": r.id,
                "domain": r.domain,
                "record_type": r.record_type,
                "severity": r.severity,
                "message": r.message,
                "old_value": r.old_value,
                "new_value": r.new_value,
                "timestamp": r.timestamp,
            }
            for r in rows
        ]
    finally:
        db.close()
