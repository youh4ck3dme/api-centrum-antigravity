# backend/app/dns_monitor/routes.py

import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import JSONResponse

from ..auth import decode_access_token
from .monitor import manager, dns_snapshot, recent_threats, last_scan_ts

router = APIRouter(tags=["DNS Monitor"])


def _verify_ws_token(token: str | None) -> bool:
    """Validate JWT token passed as query param for WebSocket auth."""
    if not token:
        return False
    try:
        payload = decode_access_token(token)
        return bool(payload.get("sub"))
    except Exception:
        return False


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
