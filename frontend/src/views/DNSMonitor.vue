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
</script>

<style scoped>
.dns-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title  { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin: 0; display: flex; align-items: center; gap: 0.6rem; }
.page-sub    { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }

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
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 1rem; }
.stat-card {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09);
  backdrop-filter: blur(12px); border-radius: 14px; padding: 1rem 1.1rem;
  display: flex; align-items: center; gap: 0.9rem;
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
</style>
