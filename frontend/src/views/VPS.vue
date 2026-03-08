<template>
  <div class="vps-root">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">VPS Monitor</h2>
        <p class="page-sub">{{ data ? `${data.total} domén — ${data.server.ip}` : 'Načítavam...' }}</p>
      </div>
      <button @click="fetchStatus" class="btn-ghost" :disabled="loading">
        <span :style="loading ? 'display:inline-block;animation:spin .7s linear infinite' : ''">🔄</span>
        {{ loading ? 'Načítavam...' : 'Obnoviť' }}
      </button>
    </div>

    <!-- Server card -->
    <div class="stats-row" v-if="data">
      <div class="stat-card">
        <div class="stat-icon">🖥️</div>
        <div class="stat-body">
          <p class="stat-label">VPS IP</p>
          <p class="stat-value mono">{{ data.server.ip }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🌍</div>
        <div class="stat-body">
          <p class="stat-label">Hostname</p>
          <p class="stat-value mono">{{ data.server.hostname }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📡</div>
        <div class="stat-body">
          <p class="stat-label">API volania (24h)</p>
          <p class="stat-value">{{ data.api_calls_24h }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🌐</div>
        <div class="stat-body">
          <p class="stat-label">Aktívne domény</p>
          <p class="stat-value">{{ onlineCount }} / {{ data.total }}</p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading && !data" class="empty-state">
      <div class="spinner"></div>
      <span>Pingujeme domény...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="empty-state">
      <span style="font-size:2rem">⚠️</span>
      <span>{{ error }}</span>
    </div>

    <!-- Domain table -->
    <div v-else-if="data" class="panel">
      <div class="panel-header">
        <span class="panel-title">Stav domén</span>
        <span class="count-badge">{{ data.total }}</span>
      </div>
      <div class="table-wrap">
        <table class="vps-table">
          <thead>
            <tr>
              <th>Doména</th>
              <th>HTTP status</th>
              <th>HTTPS</th>
              <th>SSL expiry</th>
              <th>Stav</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in data.domains" :key="d.name">
              <td class="mono">{{ d.name }}</td>
              <td>
                <span v-if="d.http_status" :class="d.http_status < 400 ? 'badge-green' : 'badge-red'">
                  {{ d.http_status }}
                </span>
                <span v-else class="badge-gray">—</span>
              </td>
              <td>
                <span v-if="d.https_reachable" class="badge-green">✅ HTTPS</span>
                <span v-else class="badge-red">❌ HTTP</span>
              </td>
              <td>
                <span
                  v-if="d.ssl_expiry_days !== null"
                  :class="sslClass(d.ssl_expiry_days)"
                >
                  {{ d.ssl_expiry_days }}d
                </span>
                <span v-else class="badge-gray">N/A</span>
              </td>
              <td>
                <span :class="isOnline(d) ? 'status-online' : 'status-offline'">
                  {{ isOnline(d) ? '● Online' : '● Offline' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api/api';

const data = ref(null);
const loading = ref(false);
const error = ref(null);

const fetchStatus = async () => {
  loading.value = true;
  error.value = null;
  try {
    const res = await api.get('/vps/status');
    data.value = res.data;
  } catch (err) {
    error.value = 'Chyba pri načítaní VPS statusu';
  } finally {
    loading.value = false;
  }
};

const isOnline = (d) => d.http_status !== null && d.http_status < 500;
const onlineCount = computed(() => data.value?.domains.filter(isOnline).length ?? 0);

const sslClass = (days) => {
  if (days > 30) return 'badge-green';
  if (days > 7)  return 'badge-yellow';
  return 'badge-red';
};

onMounted(fetchStatus);
</script>

<style scoped>
.vps-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title  { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.page-sub    { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }

.btn-ghost {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
  color: #cbd5e1; padding: 0.45rem 0.9rem; border-radius: 8px;
  cursor: pointer; font-size: 0.85rem; transition: background 0.2s;
}
.btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.12); }
.btn-ghost:disabled { opacity: 0.5; cursor: default; }

@keyframes spin { to { transform: rotate(360deg); } }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 1rem; }
.stat-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  backdrop-filter: blur(12px);
  border-radius: 14px; padding: 1.1rem 1.25rem;
  display: flex; align-items: center; gap: 1rem;
}
.stat-icon  { font-size: 1.8rem; }
.stat-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; margin: 0; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: #f1f5f9; margin: 0.1rem 0 0; }

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
.vps-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.vps-table thead tr { background: rgba(255,255,255,0.04); }
.vps-table th {
  padding: 0.6rem 0.9rem; text-align: left;
  color: #64748b; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.vps-table tbody tr { transition: background 0.15s; }
.vps-table tbody tr:hover { background: rgba(255,255,255,0.03); }
.vps-table td {
  padding: 0.6rem 0.9rem; color: #cbd5e1;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.mono { font-family: monospace; font-size: 0.78rem; color: #94a3b8; }

.badge-green  { color: #4ade80; font-weight: 700; font-size: 0.8rem; }
.badge-yellow { color: #facc15; font-weight: 700; font-size: 0.8rem; }
.badge-red    { color: #f87171; font-weight: 700; font-size: 0.8rem; }
.badge-gray   { color: #64748b; font-size: 0.8rem; }

.status-online  { color: #4ade80; font-weight: 700; font-size: 0.8rem; }
.status-offline { color: #f87171; font-weight: 700; font-size: 0.8rem; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.75rem; padding: 3rem; color: #64748b; font-size: 0.9rem;
}
.spinner {
  width: 28px; height: 28px; border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #6366f1; border-radius: 50%; animation: spin .7s linear infinite;
}
</style>
