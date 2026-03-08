"""
Shadow API Radar scanner — processes API metrics and detects undocumented endpoints.
No external push notification dependency.
"""

import re
from sqlalchemy.orm import Session
from .models import ObservedEndpoint, DocumentedEndpoint
from ..db import SessionLocal


def parse_nginx_log_line(line: str):
    """Extract (method, path) from a nginx combined log line."""
    match = re.search(r'"([A-Z]+)\s+([^\s?]+)', line)
    if match:
        return match.group(1), match.group(2)
    return None, None


def update_endpoint(method: str, endpoint: str):
    """Upsert an observed endpoint and mark it shadow if not documented."""
    db: Session = SessionLocal()
    try:
        is_documented = (
            db.query(DocumentedEndpoint)
            .filter(
                DocumentedEndpoint.method == method,
                DocumentedEndpoint.endpoint == endpoint,
            )
            .first()
            is not None
        )
        is_shadow = not is_documented

        obs = (
            db.query(ObservedEndpoint)
            .filter(
                ObservedEndpoint.method == method,
                ObservedEndpoint.endpoint == endpoint,
            )
            .first()
        )
        if obs:
            obs.count += 1
            obs.is_shadow = is_shadow
        else:
            obs = ObservedEndpoint(
                method=method, endpoint=endpoint, count=1, is_shadow=is_shadow
            )
            db.add(obs)

        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def scan_from_metrics(metrics: list) -> int:
    """Process a performance_metrics list, upsert unique endpoints. Returns count."""
    seen: set = set()
    for m in metrics:
        key = (m["method"], m["path"])
        if key not in seen:
            seen.add(key)
            update_endpoint(m["method"], m["path"])
    return len(seen)
