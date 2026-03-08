// frontend/src/composables/useWebSocket.js
import { ref } from 'vue';

export default function useWebSocket({ url, onMessage, onStatusChange }) {
  const status = ref('disconnected');
  let ws = null;
  let reconnectTimer = null;
  let destroyed = false;

  function connect() {
    if (destroyed) return;
    status.value = 'connecting';
    onStatusChange?.(status.value);

    ws = new WebSocket(url);

    ws.onopen = () => {
      status.value = 'connected';
      onStatusChange?.(status.value);
    };

    ws.onmessage = (ev) => {
      try {
        onMessage?.(JSON.parse(ev.data));
      } catch {}
    };

    ws.onclose = () => {
      if (destroyed) return;
      status.value = 'disconnected';
      onStatusChange?.(status.value);
      // Auto-reconnect after 3s
      reconnectTimer = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      try { ws.close(); } catch {}
    };
  }

  function disconnect() {
    destroyed = true;
    clearTimeout(reconnectTimer);
    try { ws?.close(); } catch {}
    ws = null;
    status.value = 'disconnected';
  }

  return { connect, disconnect, status };
}
