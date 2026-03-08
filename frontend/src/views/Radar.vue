<template>
  <div class="radar-root">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">Shadow API Radar</h2>
        <p class="page-sub">
          <span v-if="data">{{ data.shadow_count }} tieňových / {{ data.total }} celkovo</span>
          <span v-else>Detekcia nezdokumentovaných endpointov</span>
        </p>
      </div>
      <div class="header-actions">
        <button @click="seed" class="btn-ghost" :disabled="seeding">
          {{ seeding ? '⏳ Seedujem...' : '🌱 Seed Known' }}
        </button>
        <button @click="scan" class="btn-ghost" :disabled="scanning">
          {{ scanning ? '⏳ Skenujem...' : '🔍 Skenovať' }}
        </button>
        <button @click="fetchEndpoints" class="btn-ghost" :disabled="loading">
          <span :style="loading ? 'display:inline-block;animation:spin .7s linear infinite' : ''">🔄</span>
          {{ loading ? '...' : 'Obnoviť' }}
        </button>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stats-row" v-if="data">
      <div class="stat-card">
        <div class="stat-icon">📡</div>
        <div class="stat-body">
          <p class="stat-label">Celkovo pozorovaných</p>
          <p class="stat-value">{{ data.total }}</p>
        </div>
      </div>
      <div class="stat-card shadow-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-body">
          <p class="stat-label">Tieňové endpointy</p>
          <p class="stat-value shadow-val">{{ data.shadow_count }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-body">
          <p class="stat-label">Zdokumentované</p>
          <p class="stat-value known-val">{{ data.known_count }}</p>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast" class="toast">{{ toast }}</div>

    <!-- Loading -->
    <div v-if="loading && !data" class="empty-state">
      <div class="spinner"></div>
      <span>Načítavam radar...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!data || !data.endpoints?.length" class="empty-state">
      <span style="font-size:2rem">📭</span>
      <span>Žiadne dáta — klikni „Skenovať" a potom „Obnoviť"</span>
    </div>

    <!-- Table -->
    <div v-else class="panel">
      <div class="panel-header">
        <span class="panel-title">Pozorované endpointy</span>
        <div style="display:flex;gap:0.5rem;align-items:center">
          <label class="filter-label">
            <input type="checkbox" v-model="showShadowOnly" />
            Len tieňové
          </label>
          <span class="count-badge">{{ filteredEndpoints.length }}</span>
        </div>
      </div>
      <div class="table-wrap">
        <table class="radar-table">
          <thead>
            <tr>
              <th>Metóda</th>
              <th>Endpoint</th>
              <th>Volania</th>
              <th>Posledné</th>
              <th>Typ</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="e in filteredEndpoints"
              :key="e.id"
              :class="e.is_shadow ? 'row-shadow' : ''"
            >
              <td>
                <span class="method-badge" :class="methodClass(e.method)">{{ e.method }}</span>
              </td>
              <td class="mono">{{ e.endpoint }}</td>
              <td class="fw">{{ e.count }}</td>
              <td class="ts">{{ e.last_seen ? formatTime(e.last_seen) : '—' }}</td>
              <td>
                <span v-if="e.is_shadow" class="badge-shadow">⚠ SHADOW</span>
                <span v-else class="badge-known">✅ KNOWN</span>
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
const scanning = ref(false);
const seeding = ref(false);
const showShadowOnly = ref(false);
const toast = ref('');

let toastTimer = null;
const showToast = (msg) => {
  toast.value = msg;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.value = ''; }, 3000);
};

const fetchEndpoints = async () => {
  loading.value = true;
  try {
    const res = await api.get('/radar/endpoints');
    data.value = res.data;
  } catch {
    showToast('Chyba pri načítaní');
  } finally {
    loading.value = false;
  }
};

const scan = async () => {
  scanning.value = true;
  try {
    const res = await api.post('/radar/scan');
    showToast(`Skenovanie hotové — ${res.data.scanned} endpointov spracovaných`);
    await fetchEndpoints();
  } catch {
    showToast('Chyba pri skenovaní');
  } finally {
    scanning.value = false;
  }
};

const seed = async () => {
  seeding.value = true;
  try {
    const res = await api.post('/radar/seed');
    showToast(`Seed hotový — ${res.data.added} endpointov pridaných`);
    await fetchEndpoints();
  } catch {
    showToast('Chyba pri seedovaní');
  } finally {
    seeding.value = false;
  }
};

const filteredEndpoints = computed(() => {
  if (!data.value?.endpoints) return [];
  if (showShadowOnly.value) return data.value.endpoints.filter(e => e.is_shadow);
  return data.value.endpoints;
});

const methodClass = (method) => ({
  GET:    'method-get',
  POST:   'method-post',
  DELETE: 'method-delete',
  PUT:    'method-put',
  PATCH:  'method-patch',
}[method] || 'method-other');

const formatTime = (ts) => new Date(ts).toLocaleString('sk-SK');

onMounted(fetchEndpoints);
</script>

<style scoped>
.radar-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; }
.page-title  { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.page-sub    { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }
.header-actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }

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
.shadow-card { border-color: rgba(248,113,113,0.3); }
.stat-icon  { font-size: 1.8rem; }
.stat-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; margin: 0; }
.stat-value { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; margin: 0.1rem 0 0; }
.shadow-val { color: #f87171; }
.known-val  { color: #4ade80; }

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

.filter-label {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.78rem; color: #94a3b8; cursor: pointer;
}
.filter-label input { cursor: pointer; accent-color: #f87171; }

.table-wrap { overflow-x: auto; }
.radar-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.radar-table thead tr { background: rgba(255,255,255,0.04); }
.radar-table th {
  padding: 0.6rem 0.9rem; text-align: left;
  color: #64748b; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.radar-table tbody tr { transition: background 0.15s; }
.radar-table tbody tr:hover { background: rgba(255,255,255,0.03); }
.radar-table tbody tr.row-shadow { background: rgba(248,113,113,0.04); }
.radar-table tbody tr.row-shadow:hover { background: rgba(248,113,113,0.08); }
.radar-table td {
  padding: 0.6rem 0.9rem; color: #cbd5e1;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.mono { font-family: monospace; font-size: 0.78rem; color: #94a3b8; }
.fw   { font-weight: 700; }
.ts   { color: #64748b; font-size: 0.78rem; }

.method-badge { font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 5px; }
.method-get    { background: rgba(59,130,246,0.2);  color: #93c5fd; }
.method-post   { background: rgba(34,197,94,0.2);   color: #86efac; }
.method-delete { background: rgba(239,68,68,0.2);   color: #fca5a5; }
.method-put    { background: rgba(234,179,8,0.2);   color: #fde047; }
.method-patch  { background: rgba(168,85,247,0.2);  color: #d8b4fe; }
.method-other  { background: rgba(100,116,139,0.2); color: #94a3b8; }

.badge-shadow { color: #f87171; font-weight: 700; font-size: 0.75rem; }
.badge-known  { color: #4ade80; font-weight: 700; font-size: 0.75rem; }

.toast {
  position: fixed; bottom: 5rem; left: 50%; transform: translateX(-50%);
  background: rgba(30,30,30,0.95); border: 1px solid rgba(255,255,255,0.15);
  color: #f1f5f9; padding: 0.6rem 1.2rem;
  border-radius: 10px; font-size: 0.85rem; z-index: 999;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.75rem; padding: 3rem; color: #64748b; font-size: 0.9rem;
}
.spinner {
  width: 28px; height: 28px; border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #6366f1; border-radius: 50%; animation: spin .7s linear infinite;
}
</style>
