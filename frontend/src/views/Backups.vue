<template>
  <div class="flex-1 p-6 lg:p-10 overflow-y-auto custom-scrollbar relative">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-primary-indigo shadow-[0_0_8px_rgba(79,70,229,0.6)] animate-pulse"></span>
            <span class="text-[9px] uppercase font-black text-white/50 tracking-[0.2em]">Storage Integrity: Secured</span>
          </div>
          <span v-if="backups.length" class="text-white/20 text-[9px] uppercase tracking-widest font-bold">
            Matrix Vault: {{ backups.length }} Archives
          </span>
        </div>
        <h1 class="text-4xl lg:text-7xl font-black text-white tracking-tighter leading-none">Záloha Systému</h1>
        <p class="text-white/40 text-lg font-medium tracking-tight">Správa archivovaných stavov a binárnych záloh infraštruktúry.</p>
      </div>

      <div class="mt-8 md:mt-0 flex gap-4">
        <button 
          @click="createBackup" 
          class="flex items-center justify-center h-14 px-10 rounded-2xl bg-white text-slate-950 transition-all shadow-2xl hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 group overflow-hidden font-black text-[10px] uppercase tracking-[0.2em] gap-3"
          :disabled="creating"
        >
          <div v-if="creating" class="w-4 h-4 border-2 border-slate-950/20 border-t-slate-950 rounded-full animate-spin"></div>
          <Database v-else class="w-4 h-4 group-hover:rotate-12 transition-transform" />
          <span>{{ creating ? 'Vytváram...' : 'Nová Záloha' }}</span>
        </button>
      </div>
    </header>

    <!-- Toast Notification -->
    <transition name="toast-fade">
      <div v-if="toast" 
        class="fixed bottom-10 right-10 z-[100] p-5 px-8 rounded-2xl border shadow-2xl backdrop-blur-3xl animate-in slide-in-from-right-10 duration-500 flex items-center gap-4"
        :class="toast.type === 'success' ? 'bg-accent-green/10 border-accent-green/20 text-accent-green' : 'bg-accent-rose/10 border-accent-rose/20 text-accent-rose'"
      >
        <div class="w-8 h-8 rounded-xl bg-white/10 flex items-center justify-center">
          <component :is="toast.type === 'success' ? CheckCircle2 : AlertTriangle" class="w-4 h-4" />
        </div>
        <span class="text-xs font-black uppercase tracking-widest">{{ toast.msg }}</span>
      </div>
    </transition>

    <!-- Stats Grid -->
    <div class="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 mb-16" v-if="backups.length > 0">
      <div v-for="(stat, sIdx) in [
        { label: 'Total Archives', value: backups.length, icon: Archive, color: 'primary-indigo' },
        { label: 'Vault Footprint', value: formatSize(totalSize), icon: HardDrive, color: 'primary-cyan' },
        { label: 'Latest Sync', value: lastBackupDate, icon: Clock, color: 'accent-green' }
      ]" :key="sIdx"
        class="group glass-panel p-8 rounded-[32px] cursor-default transition-all duration-500 hover:translate-y-[-4px] hover:shadow-2xl overflow-hidden relative"
      >
        <div class="flex items-center gap-5 mb-6 relative z-10">
          <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-white/10 transition-all duration-500 shadow-xl">
            <component :is="stat.icon" class="w-5 h-5 opacity-70" :class="`text-${stat.color}`" />
          </div>
          <h3 class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] leading-none">{{ stat.label }}</h3>
        </div>
        <div class="relative z-10">
          <p class="text-3xl font-black text-white tracking-tighter truncate">{{ stat.value }}</p>
        </div>
        <div class="absolute -right-8 -bottom-8 w-32 h-32 blur-[60px] rounded-full opacity-10 pointer-events-none transition-opacity group-hover:opacity-20" :class="`bg-${stat.color}`"></div>
      </div>
    </div>

    <!-- Main Content Panel -->
    <div class="relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-200">
      
      <!-- Empty State -->
      <div v-if="backups.length === 0 && !loading" class="glass-panel rounded-[40px] p-32 flex flex-col items-center justify-center gap-8 shadow-2xl relative overflow-hidden">
        <div class="w-24 h-24 rounded-[32px] bg-white/5 border border-white/10 flex items-center justify-center text-5xl shadow-2xl group-hover:rotate-12 transition-transform">
           📄
        </div>
        <div class="text-center relative z-10">
          <h3 class="text-3xl font-black text-white tracking-tight mb-3">No State Archives Found</h3>
          <p class="text-white/40 font-medium max-w-sm">Prvotná záloha databázy je nevyhnutná pre bezpečný rollback systému.</p>
        </div>
        <button 
          @click="createBackup" 
          class="px-12 py-5 bg-primary-indigo text-white rounded-2xl font-black text-[10px] uppercase tracking-[0.3em] hover:scale-105 active:scale-95 transition-all shadow-2xl relative z-10"
        >
          Initialize First Sync
        </button>
      </div>

      <!-- Backup List Panel -->
      <div v-else-if="backups.length > 0" class="glass-panel rounded-[40px] overflow-hidden shadow-2xl">
        <div class="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
          <div>
            <h2 class="text-3xl font-black text-white tracking-tighter line-height-none">Archive Matrix</h2>
            <p class="text-white/30 text-sm font-medium mt-1 tracking-tight">Prehľad dostupných snapshotov databázy</p>
          </div>
          <div class="flex items-center gap-3">
             <span class="px-5 py-2 glass-card rounded-2xl text-white/70 text-[10px] font-black uppercase tracking-[0.2em] border border-white/5">
              SECURE VAULT
            </span>
          </div>
        </div>

        <div class="table-wrap custom-scrollbar overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-white/[0.02]">
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] first:pl-12">Archive Node</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Payload Size</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Timestamp</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Engine</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] last:pr-12 text-right">Synchronization</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/[0.03]">
              <tr v-for="b in backups" :key="b.filename" class="group hover:bg-white/[0.02] transition-colors duration-300">
                <td class="p-10 py-8 first:pl-12">
                  <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-lg group-hover:scale-110 transition-transform shadow-lg">📦</div>
                    <div class="flex flex-col gap-1">
                      <span class="text-base font-bold text-white tracking-tight group-hover:text-primary-cyan transition-colors">{{ b.filename }}</span>
                      <span class="text-[9px] font-black text-white/10 uppercase tracking-widest whitespace-nowrap">Immutable Record</span>
                    </div>
                  </div>
                </td>
                <td class="p-10 py-8">
                  <span class="text-base font-black tracking-tighter text-white/70">{{ formatSize(b.size) }}</span>
                </td>
                <td class="p-10 py-8">
                  <span class="text-[10px] font-black text-white/30 uppercase tracking-[0.2em] whitespace-nowrap">{{ formatDate(b.modified) }}</span>
                </td>
                <td class="p-10 py-8">
                  <span 
                    class="px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest border"
                    :class="b.filename.endsWith('.sql') ? 'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/20' : 'bg-primary-cyan/10 text-primary-cyan border-primary-cyan/20'"
                  >
                    {{ b.filename.endsWith('.sql') ? 'PostgreSQL' : 'SQLite' }}
                  </span>
                </td>
                <td class="p-10 py-8 last:pr-12">
                  <div class="flex items-center justify-end gap-3">
                    <button 
                      @click="downloadBackup(b.filename)" 
                      class="flex items-center gap-2 px-5 py-2 rounded-xl bg-white/5 border border-white/10 text-white/70 hover:bg-white hover:text-slate-950 hover:scale-105 active:scale-95 transition-all font-black text-[9px] uppercase tracking-widest shadow-xl"
                    >
                      <Download class="w-3 h-3" />
                      Download
                    </button>
                    <button 
                      @click="deleteBackup(b.filename)" 
                      class="w-10 h-10 flex items-center justify-center rounded-xl bg-accent-rose/10 border border-accent-rose/20 text-accent-rose hover:bg-accent-rose hover:text-white transition-all shadow-xl"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  Database, HardDrive, Clock, Archive, Download, 
  Trash2, CheckCircle2, AlertTriangle, FileBox, RefreshCcw
} from 'lucide-vue-next';
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
    showToast(`Snapshot ${res.data.filename} generovaný.`, 'success');
  } catch (err) {
    const detail = err.response?.data?.detail || 'Neznáma chyba';
    showToast(`Záloha zlyhala: ${detail}`, 'error');
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
    if (!res.ok) { showToast('Sync error (404/Access Denied).', 'error'); return; }
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
    showToast('Download stream interrupted.', 'error');
  }
};

const deleteBackup = async (filename) => {
  if (!confirm(`Naozaj chcete zmazať snapshot ${filename}?`)) return;
  try {
    await api.delete(`/backups/${filename}`);
    await fetchBackups();
    showToast(`Archív ${filename} vymazaný.`, 'success');
  } catch (err) {
    showToast('Delete operation failed.', 'error');
  }
};

const formatSize = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateStr) => new Date(dateStr).toLocaleString('sk-SK', {
  day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
});

const totalSize = computed(() => backups.value.reduce((s, b) => s + b.size, 0));
const lastBackupDate = computed(() => {
  if (!backups.value.length) return '—';
  return formatDate(backups.value[0].modified);
});

onMounted(fetchBackups);
</script>

<style scoped>
.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateX(40px) scale(0.9); }

table th, table td {
  white-space: nowrap;
}
</style>
