<template>
  <div class="flex-1 p-6 lg:p-10 overflow-y-auto custom-scrollbar relative">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-accent-rose shadow-[0_0_8px_rgba(244,63,94,0.6)] animate-pulse"></span>
            <span class="text-[9px] uppercase font-black text-white/50 tracking-[0.2em]">Threat Detection: Active</span>
          </div>
          <span v-if="data" class="text-white/20 text-[9px] uppercase tracking-widest font-bold">
            Frequency: {{ data.shadow_count }} Shadow Targets Detected
          </span>
        </div>
        <h1 class="text-4xl lg:text-7xl font-black text-white tracking-tighter leading-none">Shadow Radar</h1>
        <p class="text-white/40 text-lg font-medium tracking-tight">Detekcia a analýza nezdokumentovaných API endpointov.</p>
      </div>

      <div class="mt-8 md:mt-0 flex flex-wrap gap-4">
        <button 
          @click="seed" 
          class="flex items-center justify-center h-14 px-8 rounded-2xl glass-card text-white/30 hover:text-white transition-all shadow-xl hover:scale-105 active:scale-95 group overflow-hidden border border-white/5 font-black text-xs uppercase tracking-widest gap-3"
          :disabled="seeding"
        >
          <Database class="w-4 h-4" :class="{ 'animate-pulse text-accent-green': seeding }" />
          <span>{{ seeding ? 'Seeding...' : 'Seed Known' }}</span>
        </button>

        <button 
          @click="scan" 
          class="flex items-center justify-center h-14 px-8 rounded-2xl glass-card text-white/30 hover:text-white transition-all shadow-xl hover:scale-105 active:scale-95 group overflow-hidden border border-white/5 font-black text-xs uppercase tracking-widest gap-3"
          :disabled="scanning"
        >
          <Search class="w-4 h-4" :class="{ 'animate-spin text-primary-cyan': scanning }" />
          <span>{{ scanning ? 'Scanning...' : 'Scan Node' }}</span>
        </button>

        <button 
          @click="fetchEndpoints" 
          class="flex items-center justify-center w-14 h-14 rounded-2xl glass-card text-white/50 hover:text-white transition-all shadow-xl hover:scale-105 active:scale-95 group overflow-hidden border border-white/5"
          :disabled="loading"
        >
          <RefreshCcw class="w-5 h-5 relative z-10" :class="{ 'animate-spin': loading }" />
          <div class="absolute inset-0 bg-white/5 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
        </button>
      </div>
    </header>

    <!-- Toast Notification -->
    <transition name="toast-fade">
      <div v-if="toast" 
        class="fixed bottom-10 left-1/2 -translate-x-1/2 z-[100] p-5 px-10 rounded-full border shadow-2xl backdrop-blur-3xl animate-in slide-in-from-bottom-10 duration-500 flex items-center gap-4 bg-white/5 border-white/10"
      >
        <div class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-accent-green">
           <Zap class="w-4 h-4" />
        </div>
        <span class="text-xs font-black uppercase tracking-widest text-white/80">{{ toast }}</span>
      </div>
    </transition>

    <!-- Stats Grid -->
    <div class="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 mb-16" v-if="data">
      <div v-for="(stat, sIdx) in [
        { label: 'Total Observed', value: data.total, icon: Radio, color: 'primary-indigo' },
        { label: 'Shadow Endpoints', value: data.shadow_count, icon: ShieldAlert, color: 'accent-rose', isShadow: true },
        { label: 'Documented Base', value: data.known_count, icon: ShieldCheck, color: 'accent-green' }
      ]" :key="sIdx"
        class="group glass-panel p-8 rounded-[32px] cursor-default transition-all duration-500 hover:translate-y-[-4px] hover:shadow-2xl overflow-hidden relative"
        :class="stat.isShadow ? 'border-accent-rose/30 bg-accent-rose/[0.02]' : ''"
      >
        <div class="flex items-center gap-5 mb-6 relative z-10">
          <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-white/10 transition-all duration-500 shadow-xl">
            <component :is="stat.icon" class="w-5 h-5 opacity-70" :class="`text-${stat.color}`" />
          </div>
          <h3 class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] leading-none">{{ stat.label }}</h3>
        </div>
        <div class="relative z-10">
          <p class="text-5xl font-black text-white tracking-tighter" :class="stat.isShadow ? 'text-accent-rose animate-pulse' : ''">
            {{ stat.value }}
          </p>
        </div>
        <div class="absolute -right-8 -bottom-8 w-32 h-32 blur-[60px] rounded-full opacity-10 pointer-events-none transition-opacity group-hover:opacity-20" :class="`bg-${stat.color}`"></div>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      
      <!-- Empty State -->
      <div v-if="!data || !data.endpoints?.length" class="glass-panel rounded-[40px] p-32 flex flex-col items-center justify-center gap-8 shadow-2xl relative overflow-hidden">
        <div class="w-24 h-24 rounded-[32px] bg-white/5 border border-white/10 flex items-center justify-center text-5xl shadow-2xl animate-bounce">
           🛸
        </div>
        <div class="text-center relative z-10">
          <h3 class="text-3xl font-black text-white tracking-tight mb-3">No Signals Intercepted</h3>
          <p class="text-white/40 font-medium max-w-sm mx-auto">Click Scan Node to interrogate the system for undocumented traffic.</p>
        </div>
      </div>

      <!-- Radar List Panel -->
      <div v-else class="glass-panel rounded-[40px] overflow-hidden shadow-2xl">
        <div class="p-10 border-b border-white/5 flex flex-col sm:flex-row sm:items-center justify-between bg-white/[0.01] gap-6">
          <div>
            <h2 class="text-3xl font-black text-white tracking-tighter line-height-none">Signal Stream</h2>
            <p class="text-white/30 text-sm font-medium mt-1 tracking-tight">Monitorované sieťové interfazy v reálnom čase</p>
          </div>
          <div class="flex items-center gap-6">
             <label class="flex items-center gap-3 cursor-pointer group">
               <input type="checkbox" v-model="showShadowOnly" class="w-5 h-5 rounded-lg bg-white/5 border-white/10 text-accent-rose focus:ring-accent-rose transition-all" />
               <span class="text-[10px] font-black uppercase tracking-[0.2em] transition-colors" :class="showShadowOnly ? 'text-accent-rose' : 'text-white/30'">Shadow Only</span>
             </label>
             <span class="px-5 py-2 glass-card rounded-2xl text-white/70 text-[10px] font-black uppercase tracking-[0.2em] border border-white/5">
              {{ filteredEndpoints.length }} SIGNALS
            </span>
          </div>
        </div>

        <div class="table-wrap custom-scrollbar overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-white/[0.02]">
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] first:pl-12">Method</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Resource Path</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Frequency</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Last Intercept</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] last:pr-12">Encryption / State</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/[0.03]">
              <tr v-for="e in filteredEndpoints" :key="e.id" 
                class="group transition-colors duration-300"
                :class="e.is_shadow ? 'bg-accent-rose/[0.02] hover:bg-accent-rose/[0.04]' : 'hover:bg-white/[0.02]'"
              >
                <td class="p-10 py-8 first:pl-12">
                   <span 
                    class="px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-[0.2em] shadow-lg border"
                    :class="methodStyle(e.method)"
                  >
                    {{ e.method }}
                  </span>
                </td>
                <td class="p-10 py-8">
                  <div class="flex flex-col gap-1">
                    <span class="text-base font-bold text-white tracking-tight group-hover:text-primary-cyan transition-colors">{{ e.endpoint }}</span>
                    <span v-if="e.is_shadow" class="text-[8px] font-black text-accent-rose uppercase tracking-[0.2em] animate-pulse">Unauthorized Access Pattern</span>
                  </div>
                </td>
                <td class="p-10 py-8">
                  <div class="flex items-center gap-3">
                    <div class="h-10 w-1 flex flex-col justify-end bg-white/5 rounded-full overflow-hidden">
                      <div class="w-full bg-primary-indigo shadow-[0_0_8px_rgba(79,70,229,0.5)] transition-all duration-1000" :style="{ height: Math.min(100, (e.count / 100) * 100) + '%' }"></div>
                    </div>
                    <span class="text-xl font-black tracking-tighter text-white/70">{{ e.count }}</span>
                  </div>
                </td>
                <td class="p-10 py-8">
                  <span class="text-[10px] font-black text-white/20 uppercase tracking-[0.2em] font-mono whitespace-nowrap">
                    {{ e.last_seen ? formatTime(e.last_seen) : 'NULL' }}
                  </span>
                </td>
                <td class="p-10 py-8 last:pr-12">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center transition-transform group-hover:scale-110 shadow-lg">
                      <component :is="e.is_shadow ? AlertTriangle : CheckCircle2" 
                        class="w-4 h-4" 
                        :class="e.is_shadow ? 'text-accent-rose animate-pulse' : 'text-accent-green'" 
                      />
                    </div>
                    <span class="text-[10px] font-black uppercase tracking-[0.2em]" :class="e.is_shadow ? 'text-accent-rose' : 'text-accent-green'">
                      {{ e.is_shadow ? 'Shadow Node' : 'Known Proxy' }}
                    </span>
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
  Radio, ShieldAlert, ShieldCheck, Database, Search, 
  RefreshCcw, AlertTriangle, CheckCircle2, Zap 
} from 'lucide-vue-next';
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
    showToast('Chyba pri nadväzovaní spojenia.');
  } finally {
    loading.value = false;
  }
};

const scan = async () => {
  scanning.value = true;
  try {
    const res = await api.post('/radar/scan');
    showToast(`Skenovanie hotové — ${res.data.scanned} endpointov.`);
    await fetchEndpoints();
  } catch {
    showToast('Chyba pri skenovaní.');
  } finally {
    scanning.value = false;
  }
};

const seed = async () => {
  seeding.value = true;
  try {
    const res = await api.post('/radar/seed');
    showToast(`Seed hotový — ${res.data.added} pridaných.`);
    await fetchEndpoints();
  } catch {
    showToast('Chyba pri seedovaní.');
  } finally {
    seeding.value = false;
  }
};

const filteredEndpoints = computed(() => {
  if (!data.value?.endpoints) return [];
  if (showShadowOnly.value) return data.value.endpoints.filter(e => e.is_shadow);
  return data.value.endpoints;
});

const methodStyle = (method) => ({
  'GET':    'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/30',
  'POST':   'bg-accent-green/10 text-accent-green border-accent-green/30',
  'DELETE': 'bg-accent-rose/10 text-accent-rose border-accent-rose/30',
  'PUT':    'bg-primary-cyan/10 text-primary-cyan border-primary-cyan/30',
  'PATCH':  'bg-white/5 text-white border-white/20',
}[method] || 'bg-white/5 text-white/30 border-white/10');

const formatTime = (ts) => new Date(ts).toLocaleString('sk-SK', {
  day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
});

onMounted(fetchEndpoints);
</script>

<style scoped>
.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translate(-50%, 20px) scale(0.9); }

table th, table td {
  white-space: nowrap;
}
</style>
