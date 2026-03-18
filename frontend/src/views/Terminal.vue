<template>
  <div class="term-root">

    <!-- Page header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">
          <span class="status-dot" :class="connState"></span>
          SSH Console
        </h2>
        <p class="page-sub">{{ statusLabel }}</p>
      </div>
      <button v-if="connState === 'connected'" class="btn-disconnect" @click="doDisconnect">
        Odpojiť
      </button>
    </div>

    <!-- Connect form (shown when not connected) -->
    <div v-if="connState !== 'connected'" class="connect-card glass-card">
      <h3 class="connect-title">Pripojiť sa cez SSH</h3>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">Host / IP</label>
          <input v-model="form.host" class="field-input" placeholder="194.182.87.6" @keyup.enter="doConnect" />
        </div>
        <div class="field">
          <label class="field-label">Používateľ</label>
          <input v-model="form.user" class="field-input" placeholder="root" @keyup.enter="doConnect" />
        </div>
        <div class="field field-full">
          <label class="field-label">Heslo</label>
          <input v-model="form.password" class="field-input" type="password" placeholder="••••••••" @keyup.enter="doConnect" />
        </div>
      </div>
      <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>
      <button class="btn-connect" :disabled="connecting" @click="doConnect">
        {{ connecting ? 'Pripájam...' : 'Pripojiť' }}
      </button>
    </div>

    <!-- Terminal panel (always rendered so xterm mounts once; hidden until connected) -->
    <div class="term-panel" :class="{ hidden: connState !== 'connected' }">
      <div class="term-header">
        <span class="term-label">{{ form.user }}@{{ form.host }}</span>
        <span class="term-hint">Ctrl+C ukončí proces · Ctrl+D odhlási</span>
      </div>
      <div class="term-wrap" ref="termWrap"></div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import useTerminal from '../composables/useTerminal.js';

// ── State ────────────────────────────────────────────────────────────────────
const termWrap = ref(null);
const connState = ref('disconnected'); // 'disconnected' | 'connecting' | 'connected'
const connecting = ref(false);
const errorMsg = ref('');
const statusLabel = ref('Odpojený');
const form = ref({ host: '194.182.87.6', user: 'root', password: '' });

// ── xterm.js setup ────────────────────────────────────────────────────────────
const xterm = new Terminal({
  theme: {
    background:          '#020c02',
    foreground:          '#00e040',
    cursor:              '#00ff41',
    cursorAccent:        '#020c02',
    selectionBackground: 'rgba(0,255,65,0.25)',
    black:               '#011a01',
    red:                 '#ff4444',
    green:               '#00e040',
    yellow:              '#aaff00',
    blue:                '#00cfff',
    magenta:             '#ff79c6',
    cyan:                '#00ffcc',
    white:               '#aaffaa',
    brightBlack:         '#1a4d1a',
    brightRed:           '#ff6e6e',
    brightGreen:         '#00ff41',
    brightYellow:        '#ccff33',
    brightBlue:          '#33ddff',
    brightMagenta:       '#ff92d0',
    brightCyan:          '#80ffdd',
    brightWhite:         '#ccffcc',
  },
  fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, 'Courier New', monospace",
  fontSize: 13,
  lineHeight: 1.4,
  cursorBlink: true,
  cursorStyle: 'block',
  scrollback: 5000,
  allowTransparency: true,
  rendererType: 'canvas', // Canvas renderer — avoids web worker CSP issues
});

const fitAddon = new FitAddon();
xterm.loadAddon(fitAddon);

// ── Terminal composable ───────────────────────────────────────────────────────
const { connect, sendConnect, sendResize, sendInput, disconnect } = useTerminal({
  onData(bytes) {
    xterm.write(bytes);
  },
  onStatus(msg) {
    if (msg === 'connected') {
      // WS open — send SSH handshake immediately
      sendConnect({
        host: form.value.host,
        user: form.value.user,
        password: form.value.password,
        cols: xterm.cols,
        rows: xterm.rows,
      });
      statusLabel.value = 'Nadväzujem SSH spojenie...';
    } else if (msg.toLowerCase().includes('connecting')) {
      statusLabel.value = 'Nadväzujem SSH spojenie...';
    } else {
      statusLabel.value = msg;
    }
  },
  onClose(code, reason) {
    connState.value = 'disconnected';
    connecting.value = false;
    if (code === 4001) {
      errorMsg.value = 'Autentifikácia zlyhala — neplatný token.';
      statusLabel.value = 'Chyba autentifikácie';
    } else if (code === 4002) {
      errorMsg.value = 'Chybný protokol pripojenia.';
      statusLabel.value = 'Chyba protokolu';
    } else if (code !== 1000 && code !== 1001) {
      errorMsg.value = reason || 'Spojenie bolo prerušené.';
      statusLabel.value = `Odpojený (kód ${code})`;
    } else {
      statusLabel.value = 'Odpojený';
    }
    xterm.write('\r\n\x1b[33m[Spojenie ukončené]\x1b[0m\r\n');
  },
});

// ── Resize observer ───────────────────────────────────────────────────────────
let resizeObs = null;

function setupResize() {
  resizeObs = new ResizeObserver(() => {
    try {
      fitAddon.fit();
      if (connState.value === 'connected') {
        sendResize(xterm.cols, xterm.rows);
      }
    } catch {}
  });
  if (termWrap.value) resizeObs.observe(termWrap.value);
}

// ── Connect / disconnect ──────────────────────────────────────────────────────
async function doConnect() {
  if (!form.value.host || !form.value.user || !form.value.password) {
    errorMsg.value = 'Vyplňte všetky polia.';
    return;
  }
  errorMsg.value = '';
  connecting.value = true;
  connState.value = 'connecting';
  statusLabel.value = 'Pripájam WebSocket...';

  const token = localStorage.getItem('access_token');

  // Switch to connected view so terminal container is visible for measuring
  connState.value = 'connected';
  await nextTick();

  // Fit the terminal to the now-visible container
  try { fitAddon.fit(); } catch {}

  connect(token);
  connecting.value = false;
  xterm.focus();
}

function doDisconnect() {
  disconnect();
  connState.value = 'disconnected';
  statusLabel.value = 'Odpojený';
  xterm.write('\r\n\x1b[33m[Spojenie ukončené používateľom]\x1b[0m\r\n');
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(() => {
  xterm.open(termWrap.value);
  xterm.onData(sendInput); // keystrokes → WS binary frames
  fitAddon.fit();
  setupResize();
  xterm.write(
    '\x1b[1;32mAPI Centrum — SSH Console\x1b[0m\r\n' +
    '\x1b[90mVyplňte formulár a kliknite na Pripojiť.\x1b[0m\r\n\n'
  );
});

onBeforeUnmount(() => {
  resizeObs?.disconnect();
  disconnect();
  xterm.dispose();
});
</script>

<style scoped>
.term-root {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  height: 100%;
  box-sizing: border-box;
}

/* Status dot */
.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.connected {
  background: var(--color-secondary);
  box-shadow: 0 0 6px var(--color-secondary);
  animation: pulse-dot 2s infinite;
}
.status-dot.connecting { background: #fb923c; }
.status-dot.disconnected { background: #64748b; }

@keyframes pulse-dot {
  0%   { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7); }
  70%  { box-shadow: 0 0 0 8px rgba(74, 222, 128, 0); }
  100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
}

/* Header */
@media (max-width: 480px) {
  .page-title { font-size: 1.2rem; }
}

/* Connect card */
.connect-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.connect-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
@media (max-width: 480px) {
  .form-grid { grid-template-columns: 1fr; }
  .field-input { font-size: 16px; }
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field-full { grid-column: 1 / -1; }
.field-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.field-input {
  padding: 0.6rem 0.85rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
}
.field-input:focus { border-color: rgba(0,255,65,0.5); }

.error-banner {
  padding: 0.6rem 0.85rem;
  border-radius: 8px;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: var(--color-danger);
  font-size: 0.82rem;
}

.btn-connect {
  align-self: flex-start;
  background: rgba(0,255,65,0.2);
}
@media (max-width: 480px) {
  .btn-connect { align-self: stretch; width: 100%; justify-content: center; }
}
.btn-connect {
  background: rgba(0,255,65,0.2);
  border: 1px solid rgba(0,255,65,0.4);
  color: #c7d2fe;
  padding: 0.6rem 1.4rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-connect:hover:not(:disabled) {
  background: rgba(0,255,65,0.3);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0,255,65,0.2);
}
.btn-connect:disabled { opacity: 0.45; cursor: not-allowed; }

.btn-disconnect {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: var(--color-danger);
  padding: 0.5rem 1rem;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-disconnect:hover { background: rgba(248, 113, 113, 0.2); }

/* Terminal panel */
.term-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(10, 10, 10, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  min-height: 400px;
}
@media (max-width: 480px) { .term-panel { min-height: 280px; border-radius: 12px; } }
.term-panel.hidden { display: none; }

.term-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}
.term-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--color-secondary);
  font-family: 'JetBrains Mono', Consolas, monospace;
}
.term-hint {
  font-size: 0.7rem;
  color: #475569;
}

.term-wrap {
  flex: 1;
  padding: 0.5rem;
  overflow: hidden;
}

/* xterm.js overrides */
:deep(.xterm) { height: 100%; }
:deep(.xterm-viewport) { background: transparent !important; }
:deep(.xterm-screen) { height: 100% !important; }
</style>
