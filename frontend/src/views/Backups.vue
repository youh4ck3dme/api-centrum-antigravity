<template>
  <div class="backup-root">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">Záloha systému</h2>
        <p class="page-sub">{{ backups.length ? `${backups.length} zálo${backups.length === 1 ? 'ha' : 'hy'}` : 'Žiadne zálohy' }}</p>
      </div>
      <button @click="createBackup" class="btn-create" :disabled="creating">
        <span v-if="creating" class="spin-icon">⏳</span>
        <span v-else>💾</span>
        {{ creating ? 'Vytváram...' : 'Vytvoriť zálohu' }}
      </button>
    </div>

    <!-- Toast -->
    <transition name="toast-fade">
      <div v-if="toast" :class="['toast', toast.type]">{{ toast.msg }}</div>
    </transition>

    <!-- Stats cards -->
    <div class="stats-row" v-if="backups.length > 0">
      <div class="stat-card">
        <div class="stat-icon">💾</div>
        <div class="stat-body">
          <p class="stat-label">Počet záloh</p>
          <p class="stat-value">{{ backups.length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-body">
          <p class="stat-label">Celková veľkosť</p>
          <p class="stat-value">{{ formatSize(totalSize) }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🕐</div>
        <div class="stat-body">
          <p class="stat-label">Posledná záloha</p>
          <p class="stat-value">{{ lastBackupDate }}</p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="empty-state">
      <div class="spinner"></div>
      <span>Načítavam zálohy...</span>
    </div>

    <!-- Empty state -->
    <div v-else-if="backups.length === 0" class="empty-state">
      <span style="font-size:2.5rem">💾</span>
      <span>Žiadne zálohy</span>
      <span style="font-size:0.8rem;color:#64748b">Kliknite na "Vytvoriť zálohu" pre prvú zálohu databázy.</span>
    </div>

    <!-- Backup table -->
    <div v-else class="panel">
      <div class="panel-header">
        <span class="panel-title">Zoznam záloh</span>
        <span class="count-badge">{{ backups.length }}</span>
      </div>
      <div class="table-wrap">
        <table class="backup-table">
          <thead>
            <tr>
              <th>Súbor</th>
              <th>Veľkosť</th>
              <th>Dátum</th>
              <th>Typ</th>
              <th>Akcie</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in backups" :key="b.filename">
              <td class="mono">{{ b.filename }}</td>
              <td>{{ formatSize(b.size) }}</td>
              <td class="date-col">{{ formatDate(b.modified) }}</td>
              <td>
                <span :class="b.filename.endsWith('.sql') ? 'badge-sql' : 'badge-db'">
                  {{ b.filename.endsWith('.sql') ? 'PostgreSQL' : 'SQLite' }}
                </span>
              </td>
              <td class="actions-col">
                <button @click="downloadBackup(b.filename)" class="btn-dl" title="Stiahnuť">
                  ⬇ Stiahnuť
                </button>
                <button @click="deleteBackup(b.filename)" class="btn-del" title="Zmazať">
                  🗑
                </button>
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

const backups = ref([]);
const loading = ref(false);
const creating = ref(false);
const toast = ref(null);

let toastTimer = null;
const showToast = (msg, type = 'success') => {
  clearTimeout(toastTimer);
  toast.value = { msg, type };
  toastTimer = setTimeout(() => { toast.value = null; }, 3000);
};

const fetchBackups = async () => {
  loading.value = true;
  try {
    const res = await api.get('/backups');
    backups.value = res.data;
  } catch (err) {
    showToast('Nepodarilo sa načítať zálohy.', 'error');
  } finally {
    loading.value = false;
  }
};

const createBackup = async () => {
  creating.value = true;
  try {
    const res = await api.post('/backups/create');
    await fetchBackups();
    showToast(`Záloha ${res.data.filename} vytvorená úspešne.`, 'success');
  } catch (err) {
    const detail = err.response?.data?.detail || 'Neznáma chyba';
    showToast(`Vytvorenie zálohy zlyhalo: ${detail}`, 'error');
  } finally {
    creating.value = false;
  }
};

const downloadBackup = async (filename) => {
  const token = localStorage.getItem('access_token');
  try {
    const res = await fetch(`/api/backups/${encodeURIComponent(filename)}/download`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) { showToast('Stiahnutie zlyhalo (401/404).', 'error'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch {
    showToast('Stiahnutie zlyhalo.', 'error');
  }
};

const deleteBackup = async (filename) => {
  if (!confirm(`Naozaj chcete zmazať zálohu ${filename}?`)) return;
  try {
    await api.delete(`/backups/${filename}`);
    await fetchBackups();
    showToast(`Záloha ${filename} bola zmazaná.`, 'success');
  } catch (err) {
    showToast('Zmazanie zálohy zlyhalo.', 'error');
  }
};

const formatSize = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateStr) => new Date(dateStr).toLocaleString('sk-SK');

const totalSize = computed(() => backups.value.reduce((s, b) => s + b.size, 0));
const lastBackupDate = computed(() => {
  if (!backups.value.length) return '—';
  return formatDate(backups.value[0].modified);
});

onMounted(fetchBackups);
</script>

<style scoped>
.backup-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-title  { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.page-sub    { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }

.btn-create {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(99,102,241,0.25); border: 1px solid rgba(99,102,241,0.4);
  color: #a5b4fc; padding: 0.5rem 1.1rem; border-radius: 8px;
  cursor: pointer; font-size: 0.85rem; font-weight: 600;
  transition: background 0.2s;
}
.btn-create:hover:not(:disabled) { background: rgba(99,102,241,0.4); }
.btn-create:disabled { opacity: 0.5; cursor: default; }
.spin-icon { display: inline-block; animation: spin .7s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }

/* Toast */
.toast {
  padding: 0.75rem 1.2rem; border-radius: 10px; font-size: 0.85rem; font-weight: 500;
  position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9999;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.toast.success { background: rgba(34,197,94,0.2); border: 1px solid rgba(34,197,94,0.4); color: #4ade80; }
.toast.error   { background: rgba(239,68,68,0.2); border: 1px solid rgba(239,68,68,0.4); color: #f87171; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 0.3s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; }

/* Stats cards */
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

/* Panel & table */
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
.backup-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.backup-table thead tr { background: rgba(255,255,255,0.04); }
.backup-table th {
  padding: 0.6rem 0.9rem; text-align: left;
  color: #64748b; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.backup-table tbody tr { transition: background 0.15s; }
.backup-table tbody tr:hover { background: rgba(255,255,255,0.03); }
.backup-table td {
  padding: 0.6rem 0.9rem; color: #cbd5e1;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.mono { font-family: monospace; font-size: 0.78rem; color: #94a3b8; }
.date-col { font-size: 0.78rem; color: #94a3b8; }
.actions-col { white-space: nowrap; display: flex; gap: 0.5rem; align-items: center; padding: 0.5rem 0.9rem; }

.badge-sql { color: #c084fc; font-size: 0.72rem; font-weight: 700; }
.badge-db  { color: #60a5fa; font-size: 0.72rem; font-weight: 700; }

.btn-dl {
  background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
  color: #a5b4fc; padding: 0.3rem 0.7rem; border-radius: 6px;
  cursor: pointer; font-size: 0.75rem; transition: background 0.15s;
}
.btn-dl:hover { background: rgba(99,102,241,0.3); }

.btn-del {
  background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.25);
  color: #f87171; padding: 0.3rem 0.6rem; border-radius: 6px;
  cursor: pointer; font-size: 0.85rem; transition: background 0.15s;
}
.btn-del:hover { background: rgba(239,68,68,0.25); }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.75rem; padding: 3rem; color: #64748b; font-size: 0.9rem;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
}
.spinner {
  width: 28px; height: 28px; border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #6366f1; border-radius: 50%; animation: spin .7s linear infinite;
}
</style>
