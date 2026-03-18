import json
import logging
from fastapi import APIRouter, WebSocket, Query

from ..auth import decode_access_token
from ..config import settings
from ..deps import _verify_ws_token
from .ssh_handler import bridge

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Terminal"])




@router.websocket("/terminal/ws")
async def terminal_ws(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    Authenticated WebSocket endpoint for SSH terminal access.

    Protocol:
      1. Client connects: ws://host/api/terminal/ws?token=<JWT>
      2. Server accepts; waits for first text frame:
         {"type":"connect","host":"...","user":"...","password":"...","cols":80,"rows":24}
      3. SSH session established; subsequent binary frames = raw keystrokes
      4. Server sends binary frames = raw SSH output (xterm renders directly)
      5. Client may send: {"type":"resize","cols":N,"rows":M}
      6. Either side closing ends the session cleanly
    """
    if not _verify_ws_token(token):
        await websocket.close(code=4001)
        return

    await websocket.accept()

    # Wait for the connect handshake
    try:
        raw = await websocket.receive_text()
        msg = json.loads(raw)
    except Exception as exc:
        logger.warning("Terminal: bad connect handshake: %s", exc)
        await websocket.close(code=4002)
        return

    if msg.get("type") != "connect":
        await websocket.send_text(
            json.dumps({"type": "error", "message": "Expected connect message"})
        )
        await websocket.close(code=4002)
        return

    host = msg.get("host", "")
    user = msg.get("user", "")
    password = msg.get("password", "")
    cols = int(msg.get("cols", 80))
    rows = int(msg.get("rows", 24))

    if not (host and user and password):
        await websocket.send_text(
            json.dumps({"type": "error", "message": "host, user, password required"})
        )
        await websocket.close(code=4002)
        return

    await websocket.send_text(json.dumps({"type": "status", "message": "Connecting..."}))

    try:
        await bridge(websocket, host, user, password, cols, rows)
    except Exception as exc:
        logger.exception("SSH bridge error for %s@%s: %s", user, host, exc)
        try:
            await websocket.send_bytes(
                f"\r\n\x1b[31mSSH Error: {exc}\x1b[0m\r\n".encode()
            )
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
