/**
 * Composable for SSH terminal WebSocket connection.
 *
 * Unlike useWebSocket.js, this composable:
 *  - Does NOT auto-reconnect (a closed SSH session is intentionally final)
 *  - Does NOT JSON-parse incoming binary frames (raw bytes go straight to xterm)
 *  - Sends binary frames for keystrokes and text frames for JSON control messages
 */
export default function useTerminal({ onData, onStatus, onClose }) {
  let ws = null;

  function connect(token) {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${proto}://${location.host}/api/terminal/ws?token=${token}`;

    ws = new WebSocket(url);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => onStatus?.('connected');

    ws.onmessage = (ev) => {
      if (ev.data instanceof ArrayBuffer) {
        // Binary = raw terminal output → pass to xterm as Uint8Array
        onData?.(new Uint8Array(ev.data));
      } else if (typeof ev.data === 'string') {
        // Text = JSON control message (status, error) from backend
        try {
          const msg = JSON.parse(ev.data);
          onStatus?.(msg.message ?? msg.type ?? 'info');
        } catch {
          // Plain text fallback — treat as terminal data
          onData?.(new TextEncoder().encode(ev.data));
        }
      }
    };

    ws.onclose = (ev) => {
      onClose?.(ev.code, ev.reason);
    };

    ws.onerror = () => {
      try { ws.close(); } catch {}
    };
  }

  /** Send SSH connect handshake — call right after WS opens (onStatus === 'connected') */
  function sendConnect({ host, user, password, cols, rows }) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'connect', host, user, password, cols, rows }));
    }
  }

  /** Notify server of terminal resize */
  function sendResize(cols, rows) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'resize', cols, rows }));
    }
  }

  /** Forward xterm keystrokes as binary frames */
  function sendInput(data) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(new TextEncoder().encode(data));
    }
  }

  function disconnect() {
    try { ws?.close(); } catch {}
    ws = null;
  }

  return { connect, sendConnect, sendResize, sendInput, disconnect };
}
