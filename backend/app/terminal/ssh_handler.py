import asyncio
import asyncssh
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class _TerminalSession(asyncssh.SSHClientSession):
    """asyncssh session that forwards SSH stdout/stderr to a WebSocket."""

    def __init__(self, ws: WebSocket, loop: asyncio.AbstractEventLoop):
        self._ws = ws
        self._loop = loop

    def data_received(self, data, datatype) -> None:
        # data may be str (when encoding set) or bytes — normalize to bytes for xterm
        if isinstance(data, str):
            raw = data.encode("utf-8", errors="replace")
        else:
            raw = data
        asyncio.run_coroutine_threadsafe(
            self._ws.send_bytes(raw),
            self._loop,
        )

    def connection_lost(self, exc) -> None:
        logger.info("SSH session closed: %s", exc)


async def bridge(
    websocket: WebSocket,
    host: str,
    username: str,
    password: str,
    cols: int = 80,
    rows: int = 24,
) -> None:
    """
    Open an SSH connection with PTY and relay bytes between the WebSocket
    and the SSH channel until either side closes.
    """
    loop = asyncio.get_event_loop()

    async with asyncssh.connect(
        host,
        username=username,
        password=password,
        known_hosts=None,   # Internal VPS — skip host-key verification
        encoding=None,      # Raw bytes at transport; session layer handles encoding
    ) as conn:
        channel, _ = await conn.create_session(
            lambda: _TerminalSession(websocket, loop),
            term_type="xterm-256color",
            term_size=(cols, rows),
            encoding="utf-8",  # data_received gets str; we encode back to bytes above
        )

        try:
            while True:
                data = await websocket.receive()

                if data["type"] == "websocket.disconnect":
                    break

                if "bytes" in data and data["bytes"]:
                    # Raw keystroke bytes from xterm → SSH stdin
                    channel.write(data["bytes"].decode("utf-8", errors="replace"))

                elif "text" in data and data["text"]:
                    # JSON control message (e.g. resize) or plain text fallback
                    try:
                        msg = json.loads(data["text"])
                        if msg.get("type") == "resize":
                            channel.change_terminal_size(
                                msg.get("cols", cols),
                                msg.get("rows", rows),
                            )
                    except json.JSONDecodeError:
                        channel.write(data["text"])

        except Exception as exc:
            logger.warning("WebSocket relay ended: %s", exc)
        finally:
            channel.close()
