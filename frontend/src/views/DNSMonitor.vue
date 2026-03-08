<template>
  <div class="dns-root">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">
          <span class="live-dot" :class="wsStatus"></span>
          Live DNS Monitor
        </h2>
        <p class="page-sub">{{ statusLabel }} · {{ domainCount }} domén monitorovaných</p>
      </div>
      <button class="btn-provision" @click="showProvision = true">🖥️ Nový server</button>
    </div>

    <!-- Provision Modal -->
    <div v-if="showProvision" class="modal-overlay" @click.self="showProvision = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">🚀 One-Click VPS Provisioning</h3>
          <button class="modal-close" @click="showProvision = false">✕</button>
        </div>
        <div class="modal-body">
          <label class="field-label">Názov servera</label>
          <input v-model="prov.name" class="field-input" placeholder="napr. production-01" />
          <label class="field-label">Provider</label>
          <select v-model="prov.provider" class="field-input">
            <option value="hetzner">Hetzner</option>
            <option value="digitalocean">DigitalOcean</option>
          </select>
          <label class="field-label">Región</label>
          <input v-model="prov.region" class="field-input" placeholder="napr. nbg1 alebo fra1" />
          <label class="field-label">Doména pre A záznam</label>
          <input v-model="prov.domain" class="field-input" placeholder="napr. app.example.com" />
          <div v-if="provStatus" class="prov-status" :class="provStatusClass">
            {{ provStatus }}
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showProvision = false">Zrušiť</button>
          <button class="btn-create-vps" @click="startProvision" :disabled="provLoading">
            {{ provLoading ? 'Vytvára sa...' : 'Vytvoriť' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">🌐</div>
        <div class="stat-body">
          <p class="stat-label">Monitorované domény</p>
          <p class="stat-value">{{ domainCount }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-body">
          <p class="stat-label">Hrozby dnes</p>
          <p class="stat-value" :class="threatsToday > 0 ? 'val-red' : 'val-green'">{{ threatsToday }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🕐</div>
        <div class="stat-body">
          <p class="stat-label">Posledný scan</p>
          <p class="stat-value stat-small">{{ lastScanLabel }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📡</div>
        <div class="stat-body">
          <p class="stat-label">Udalosti v logu</p>
          <p class="stat-value">{{ feed.length }}</p>
        </div>
      </div>
    </div>

    <!-- Live feed -->
    <div class="panel">
      <div class="panel-header">
        <div style="display:flex;align-items:center;gap:0.6rem">
          <span class="live-indicator" :class="wsStatus === 'connected' ? 'pulse' : ''">●</span>
          <span class="panel-title">Live Feed</span>
        </div>
        <button @click="feed = []" class="btn-clear">Vymazať</button>
      </div>

      <div v-if="feed.length === 0" class="empty-feed">
        <span>Čakám na udalosti... (scan každých 60s)</span>
      </div>

      <div v-else class="feed-list">
        <div
          v-for="(item, i) in feed"
          :key="i"
          class="feed-item"
          :class="feedClass(item)"
        >
          <span class="feed-time">{{ formatTime(item.timestamp) }}</span>
          <span class="feed-sev" v-if="item.severity" :style="{ color: sevColor(item.severity) }">
            {{ item.severity }}
          </span>
          <span class="feed-sev feed-hb" v-else-if="item.type === 'heartbeat'">HEARTBEAT</span>
          <span class="feed-sev feed-snap" v-else-if="item.type === 'snapshot'">SNAPSHOT</span>
          <div class="feed-body">
            <span class="feed-domain" v-if="item.domain">{{ item.domain }}</span>
            <span class="feed-msg">{{ feedMessage(item) }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import useWebSocket from '../composables/useWebSocket';

const feed = ref([]);
const wsStatus = ref('disconnected');
const domainCount = ref(0);
const threatsToday = ref(0);
const lastScan = ref(0);

const token = localStorage.getItem('access_token');
const proto = location.protocol === 'https:' ? 'wss' : 'ws';
const wsUrl = `${proto}://${location.host}/api/dns-monitor/ws?token=${token}`;

const { connect, disconnect } = useWebSocket({
  url: wsUrl,
  onMessage(msg) {
    feed.value.unshift(msg);
    if (feed.value.length > 300) feed.value.splice(300);

    if (msg.type === 'snapshot') {
      domainCount.value = msg.domain_count ?? 0;
      threatsToday.value = msg.threats_today ?? 0;
      lastScan.value = msg.last_scan ?? 0;
    } else if (msg.type === 'heartbeat') {
      domainCount.value = msg.domains_checked ?? domainCount.value;
      threatsToday.value = msg.threats_today ?? threatsToday.value;
      lastScan.value = msg.timestamp ?? lastScan.value;
    } else if (msg.type === 'threat') {
      threatsToday.value += 1;
    }
  },
  onStatusChange(s) {
    wsStatus.value = s;
  },
});

onMounted(connect);
onBeforeUnmount(disconnect);

const statusLabel = computed(() => ({
  connected: 'Pripojený',
  connecting: 'Pripájam...',
  disconnected: 'Odpojený',
}[wsStatus.value] ?? 'Odpojený'));

const lastScanLabel = computed(() => {
  if (!lastScan.value) return 'čakám...';
  const diff = Math.floor(Date.now() / 1000 - lastScan.value);
  if (diff < 5) return 'práve teraz';
  if (diff < 60) return `pred ${diff}s`;
  if (diff < 3600) return `pred ${Math.floor(diff / 60)}m`;
  return `pred ${Math.floor(diff / 3600)}h`;
});

const formatTime = (ts) => ts
  ? new Date(ts * 1000).toLocaleTimeString('sk-SK')
  : '';

const sevColor = (s) => ({
  CRITICAL: '#f87171',
  HIGH: '#fb923c',
  MEDIUM: '#facc15',
}[s] ?? '#94a3b8');

const feedClass = (item) => {
  if (item.severity === 'CRITICAL') return 'item-critical';
  if (item.severity === 'HIGH') return 'item-high';
  if (item.severity === 'MEDIUM') return 'item-medium';
  if (item.type === 'heartbeat') return 'item-hb';
  return '';
};

const feedMessage = (item) => {
  if (item.type === 'heartbeat')
    return `${item.domains_checked} domén skontrolovaných · ${item.threats_today} hrozieb dnes`;
  if (item.type === 'snapshot')
    return `Pripojený · ${item.domain_count} domén · ${item.threats_today} hrozieb dnes`;
  return item.message ?? '';
};

// ── VPS Provisioning ─────────────────────────────────────────────────────
const showProvision = ref(false);
const provLoading = ref(false);
const provStatus = ref('');
const provStatusClass = ref('');
const prov = ref({ name: '', provider: 'hetzner', region: '', domain: '' });

async function startProvision() {
  provLoading.value = true;
  provStatus.value = 'Vytvára sa server...';
  provStatusClass.value = 'status-info';
  try {
    const res = await fetch('/api/dns-monitor/provision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(prov.value),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Chyba pri vytváraní');
    provStatus.value = `Job spustený: ${data.job_id}`;
    provStatusClass.value = 'status-ok';
    // Poll status
    pollJobStatus(data.job_id);
  } catch (e) {
    provStatus.value = `Chyba: ${e.message}`;
    provStatusClass.value = 'status-err';
  } finally {
    provLoading.value = false;
  }
}

async function pollJobStatus(jobId) {
  let attempts = 0;
  const poll = setInterval(async () => {
    attempts++;
    if (attempts > 60) {
      clearInterval(poll);
      provStatus.value = 'Timeout — skontrolujte stav manuálne';
      provStatusClass.value = 'status-err';
      return;
    }
    try {
      const res = await fetch(`/api/dns-monitor/provision/${jobId}`);
      const data = await res.json();
      provStatus.value = `[${data.progress ?? 0}%] ${data.step ?? 'neznámy krok'}`;
      if (data.status === 'completed') {
        clearInterval(poll);
        provStatus.value = `✅ Server vytvorený! IP: ${data.server_ip ?? 'neznáme'}`;
        provStatusClass.value = 'status-ok';
      } else if (data.status === 'failed') {
        clearInterval(poll);
        provStatus.value = `❌ Zlyhalo: ${data.error ?? 'neznáma chyba'}`;
        provStatusClass.value = 'status-err';
      } else {
        provStatusClass.value = 'status-info';
      }
    } catch {
      // ignore poll errors
    }
  }, 3000);
}
</script>

<style scoped>
.dns-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }
@media (max-width: 480px) { .dns-root { padding: 1rem 0.5rem; gap: 1rem; } }

.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; }
.page-title  { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin: 0; display: flex; align-items: center; gap: 0.6rem; }
.page-sub    { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }
@media (max-width: 480px) { .page-title { font-size: 1.2rem; } }

/* Connection dot */
.live-dot {
  width: 10px; height: 10px; border-radius: 50%; display: inline-block;
  flex-shrink: 0;
}
.live-dot.connected    { background: #4ade80; box-shadow: 0 0 6px #4ade80; animation: pulse-dot 2s infinite; }
.live-dot.connecting   { background: #fb923c; }
.live-dot.disconnected { background: #f87171; }
@keyframes pulse-dot {
  0%   { box-shadow: 0 0 0 0 rgba(74,222,128,.7); }
  70%  { box-shadow: 0 0 0 8px rgba(74,222,128,0); }
  100% { box-shadow: 0 0 0 0 rgba(74,222,128,0); }
}

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
@media (max-width: 1023px) { .stats-row { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .stats-row { grid-template-columns: 1fr; } }
.stat-card {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09);
  backdrop-filter: blur(12px); border-radius: 14px; padding: 1rem 1.1rem;
  display: flex; align-items: center; gap: 0.9rem;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.06);
  background: rgba(255,255,255,0.07);
}
.stat-icon  { font-size: 1.6rem; }
.stat-label { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; margin: 0; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: #f1f5f9; margin: 0.1rem 0 0; }
.stat-small { font-size: 0.85rem; }
.val-red    { color: #f87171; }
.val-green  { color: #4ade80; }

/* Panel */
.panel { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; overflow: hidden; }
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.85rem 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.07);
}
.panel-title { font-weight: 600; color: #f1f5f9; }
.btn-clear {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
  color: #94a3b8; padding: 0.25rem 0.7rem; border-radius: 6px;
  cursor: pointer; font-size: 0.75rem; transition: background .15s;
}
.btn-clear:hover { background: rgba(255,255,255,0.1); }

/* Live indicator */
.live-indicator { font-size: 0.65rem; color: #64748b; }
.live-indicator.pulse { color: #4ade80; animation: blink 1.5s ease infinite; }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:.3; } }

/* Empty */
.empty-feed { padding: 2rem; text-align: center; color: #475569; font-size: 0.85rem; }

/* Feed */
.feed-list { max-height: 500px; overflow-y: auto; }
.feed-item {
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 0.55rem 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: 0.8rem; transition: background .1s;
}
.feed-item:hover { background: rgba(255,255,255,0.02); }
.item-critical { border-left: 3px solid #f87171; }
.item-high     { border-left: 3px solid #fb923c; }
.item-medium   { border-left: 3px solid #facc15; }
.item-hb       { opacity: 0.5; }

.feed-time   { color: #475569; min-width: 70px; font-size: 0.75rem; padding-top: 1px; }
.feed-sev    { min-width: 82px; font-weight: 700; font-size: 0.72rem; padding-top: 2px; }
.feed-hb     { color: #4ade80; }
.feed-snap   { color: #60a5fa; }
.feed-body   { display: flex; flex-direction: column; gap: 0.1rem; }
.feed-domain { color: #a5b4fc; font-weight: 600; }
.feed-msg    { color: #cbd5e1; }

/* Provision button */
.btn-provision {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
  color: #a5b4fc; padding: 0.5rem 1rem; border-radius: 10px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s ease;
}
.btn-provision:hover {
  background: rgba(99,102,241,0.25); transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(99,102,241,0.15);
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.modal-card {
  width: 100%; max-width: 440px;
  background: rgba(20,20,26,0.95); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06);
  backdrop-filter: blur(24px);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.06);
}
.modal-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.modal-close {
  background: none; border: none; color: #64748b; font-size: 1.1rem;
  cursor: pointer; padding: 0.25rem;
}
.modal-close:hover { color: #f1f5f9; }
.modal-body { padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 0.75rem; }
.field-label { font-size: 0.75rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.field-input {
  padding: 0.6rem 0.85rem; border-radius: 10px;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
  color: #f1f5f9; font-size: 0.85rem; outline: none;
  transition: border-color 0.2s;
}
.field-input:focus { border-color: rgba(99,102,241,0.5); }
.field-input option { background: #1e1e2a; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 0.5rem;
  padding: 1rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.06);
}
.btn-cancel {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
  color: #94a3b8; padding: 0.5rem 1rem; border-radius: 10px;
  font-size: 0.82rem; cursor: pointer; transition: background 0.15s;
}
.btn-cancel:hover { background: rgba(255,255,255,0.1); }
.btn-create-vps {
  background: rgba(99,102,241,0.2); border: 1px solid rgba(99,102,241,0.4);
  color: #c7d2fe; padding: 0.5rem 1.25rem; border-radius: 10px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s ease;
}
.btn-create-vps:hover:not(:disabled) {
  background: rgba(99,102,241,0.3); transform: translateY(-1px);
}
.btn-create-vps:disabled { opacity: 0.4; cursor: not-allowed; }
.prov-status {
  font-size: 0.8rem; padding: 0.6rem 0.85rem; border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.08);
}
.status-info { background: rgba(99,102,241,0.1); color: #a5b4fc; }
.status-ok   { background: rgba(74,222,128,0.1); color: #4ade80; }
.status-err  { background: rgba(248,113,113,0.1); color: #f87171; }
</style>
