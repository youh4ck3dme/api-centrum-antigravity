<template>
  <div class="perf-root">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">Výkon</h2>
        <p class="page-sub">API metriky — posledných {{ stats?.count ?? 0 }} volaní</p>
      </div>
      <div class="header-actions">
        <button class="btn-ghost auto-btn" :class="{ active: autoRefresh }" @click="toggleAuto">
          <span class="pulse-dot" v-if="autoRefresh"></span>
          {{ autoRefresh ? 'Auto ON' : 'Auto OFF' }}
        </button>
        <button @click="fetchPerformance" class="btn-ghost" :disabled="loading">
          <span :style="loading ? 'display:inline-block;animation:spin .7s linear infinite' : ''">🔄</span>
          {{ loading ? 'Načítavam...' : 'Obnoviť' }}
        </button>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stats-row" v-if="stats">
      <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-body">
          <p class="stat-label">Celkový počet volaní</p>
          <p class="stat-value">{{ stats.count }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🕐</div>
        <div class="stat-body">
          <p class="stat-label">Priemerná latencia</p>
          <p class="stat-value" :class="latencyClass(stats.average_latency_ms)">
            {{ stats.average_latency_ms }} ms
          </p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-body">
          <p class="stat-label">Stavové kódy</p>
          <div class="code-chips">
            <span
              v-for="(count, code) in stats.status_distribution"
              :key="code"
              class="chip"
              :class="String(code).startsWith('2') ? 'chip-green' : 'chip-red'"
            >{{ code }}: {{ count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading && !stats" class="empty-state">
      <div class="spinner"></div>
      <span>Načítavam metriky...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!stats || !stats.recent_metrics?.length" class="empty-state">
      <span style="font-size:2rem">📭</span>
      <span>Žiadne dáta — použi aplikáciu a obnov stránku</span>
    </div>

    <!-- Table -->
    <div v-else class="panel">
      <div class="panel-header">
        <span class="panel-title">Posledné záznamy</span>
        <span class="count-badge">{{ stats.recent_metrics.length }}</span>
      </div>
      <div class="table-wrap">
        <table class="perf-table">
          <thead>
            <tr>
              <th>Endpoint</th>
              <th>Metóda</th>
              <th>Čas (ms)</th>
              <th style="width:120px">Latencia</th>
              <th>Status</th>
              <th>Kedy</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, idx) in [...stats.recent_metrics].reverse()" :key="idx">
              <td class="mono">{{ m.path }}</td>
              <td>
                <span class="method-badge" :class="methodClass(m.method)">{{ m.method }}</span>
              </td>
              <td :class="latencyClass(m.latency * 1000)" class="fw">
                {{ (m.latency * 1000).toFixed(0) }}
              </td>
              <td>
                <div class="lat-bar-bg">
                  <div
                    class="lat-bar-fill"
                    :class="latencyClass(m.latency * 1000)"
                    :style="{ width: Math.min((m.latency * 1000) / 10, 100) + '%' }"
                  ></div>
                </div>
              </td>
              <td>
                <span :class="m.status < 400 ? 'ok' : 'err'">{{ m.status }}</span>
              </td>
              <td class="ts">{{ formatTime(m.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import api from "../api/api";

const stats = ref(null);
const loading = ref(false);
const autoRefresh = ref(false);
let timer = null;

const fetchPerformance = async () => {
  loading.value = true;
  try {
    const res = await api.get("/performance/stats");
    stats.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const toggleAuto = () => {
  autoRefresh.value = !autoRefresh.value;
  if (autoRefresh.value) {
    timer = setInterval(fetchPerformance, 30000);
  } else {
    clearInterval(timer);
    timer = null;
  }
};

const latencyClass = (ms) => {
  if (ms < 300) return 'lat-green';
  if (ms < 600) return 'lat-yellow';
  return 'lat-red';
};

const methodClass = (method) => ({
  'GET':    'method-get',
  'POST':   'method-post',
  'DELETE': 'method-delete',
  'PUT':    'method-put',
  'PATCH':  'method-patch',
}[method] || 'method-other');

const formatTime = (ts) => new Date(ts * 1000).toLocaleTimeString('sk-SK');

onMounted(fetchPerformance);
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.perf-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

/* Header */
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title  { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.page-sub    { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }
.header-actions { display: flex; gap: 0.6rem; }

.btn-ghost {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: #cbd5e1; padding: 0.45rem 0.9rem; border-radius: 8px;
  cursor: pointer; font-size: 0.85rem; transition: background 0.2s;
}
.btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.12); }
.btn-ghost:disabled { opacity: 0.5; cursor: default; }
.btn-ghost.active { border-color: rgba(99,255,160,0.5); color: #6bffaa; }

.pulse-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #6bffaa; display: inline-block;
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(0.7)} }
@keyframes spin  { to { transform: rotate(360deg); } }

/* Stat cards */
.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 1rem; }

.stat-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  backdrop-filter: blur(12px);
  border-radius: 14px; padding: 1.1rem 1.25rem;
  display: flex; align-items: center; gap: 1rem;
}
.stat-icon  { font-size: 1.8rem; }
.stat-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; margin: 0; }
.stat-value { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; margin: 0.1rem 0 0; }

.code-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.35rem; }
.chip       { font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
.chip-green { background: rgba(74,222,128,0.15); color: #4ade80; }
.chip-red   { background: rgba(248,113,113,0.15); color: #f87171; }

/* Panel / table */
.panel {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px; overflow: hidden;
}
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.panel-title { font-weight: 600; color: #f1f5f9; }
.count-badge {
  background: rgba(99,102,241,0.25); color: #a5b4fc;
  font-size: 0.75rem; font-weight: 700;
  padding: 2px 10px; border-radius: 999px;
}

.table-wrap { overflow-x: auto; }
.perf-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.perf-table thead tr { background: rgba(255,255,255,0.04); }
.perf-table th {
  padding: 0.6rem 0.9rem; text-align: left;
  color: #64748b; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.perf-table tbody tr { transition: background 0.15s; }
.perf-table tbody tr:hover { background: rgba(255,255,255,0.03); }
.perf-table td {
  padding: 0.6rem 0.9rem; color: #cbd5e1;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.mono { font-family: monospace; font-size: 0.78rem; color: #94a3b8; }
.fw   { font-weight: 700; }
.ts   { color: #64748b; font-size: 0.78rem; }

/* Method badges */
.method-badge { font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 5px; }
.method-get    { background: rgba(59,130,246,0.2);  color: #93c5fd; }
.method-post   { background: rgba(34,197,94,0.2);   color: #86efac; }
.method-delete { background: rgba(239,68,68,0.2);   color: #fca5a5; }
.method-put    { background: rgba(234,179,8,0.2);   color: #fde047; }
.method-patch  { background: rgba(168,85,247,0.2);  color: #d8b4fe; }
.method-other  { background: rgba(100,116,139,0.2); color: #94a3b8; }

/* Status */
.ok  { color: #4ade80; font-weight: 700; }
.err { color: #f87171; font-weight: 700; }

/* Latency colours */
.lat-green { color: #4ade80; }
.lat-yellow { color: #facc15; }
.lat-red    { color: #f87171; }

/* Latency bar */
.lat-bar-bg   { background: rgba(255,255,255,0.07); border-radius: 999px; height: 6px; width: 100%; }
.lat-bar-fill { height: 100%; border-radius: 999px; transition: width 0.3s; }
.lat-bar-fill.lat-green  { background: #4ade80; }
.lat-bar-fill.lat-yellow { background: #facc15; }
.lat-bar-fill.lat-red    { background: #f87171; }

/* Empty state */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.75rem; padding: 3rem; color: #64748b; font-size: 0.9rem;
}
.spinner {
  width: 28px; height: 28px; border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #6366f1; border-radius: 50%; animation: spin .7s linear infinite;
}
</style>
