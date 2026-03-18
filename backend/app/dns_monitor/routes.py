# backend/app/dns_monitor/routes.py

import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import JSONResponse

from ..auth import decode_access_token
from ..config import settings
from ..deps import _verify_ws_token
from .monitor import manager, dns_snapshot, recent_threats, last_scan_ts
from .persistence import get_threats

router = APIRouter(tags=["DNS Monitor"])




@router.websocket("/dns-monitor/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    if not _verify_ws_token(token):
        await websocket.close(code=4001)
        return

    await manager.connect(websocket)
    try:
        # Send initial snapshot so client has data immediately
        today = int(time.time()) - 86400
        await websocket.send_json({
            "type": "snapshot",
            "domains": list(dns_snapshot.keys()),
            "domain_count": len(dns_snapshot),
            "recent_threats": recent_threats[:50],
            "threats_today": sum(1 for t in recent_threats if t["timestamp"] > today),
            "last_scan": last_scan_ts,
        })

        # Keep connection alive
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        manager.disconnect(websocket)


@router.get("/dns-monitor/snapshot")
def get_snapshot():
    today = int(time.time()) - 86400
    return JSONResponse({
        "domain_count": len(dns_snapshot),
        "domains": list(dns_snapshot.keys()),
        "recent_threats": recent_threats[:50],
        "threats_today": sum(1 for t in recent_threats if t["timestamp"] > today),
        "last_scan": last_scan_ts,
    })


@router.get("/dns-monitor/threats")
def get_threat_history(
    limit: int = Query(default=100, le=500),
    domain: str | None = Query(default=None),
    severity: str | None = Query(default=None),
):
    """Query persisted threat history from the database."""
    try:
        threats = get_threats(limit=limit, domain=domain, severity=severity)
        return JSONResponse({"threats": threats, "count": len(threats)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query threats: {e}")
