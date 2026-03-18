<template>
  <div class="flex-1 p-6 lg:p-10 overflow-y-auto custom-scrollbar relative">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-primary-cyan shadow-[0_0_8px_rgba(6,182,212,0.6)] animate-pulse"></span>
            <span class="text-[9px] uppercase font-black text-white/50 tracking-[0.2em]">Matrix Node: Active</span>
          </div>
          <span v-if="data" class="text-white/20 text-[9px] uppercase tracking-widest font-bold">
            IPv4: {{ data.server.ip }}
          </span>
        </div>
        <h1 class="text-4xl lg:text-7xl font-black text-white tracking-tighter leading-none">VPS Monitor</h1>
        <p class="text-white/40 text-lg font-medium tracking-tight">
          {{ data ? `${data.total} monitorovaných domén na uzle ${data.server.hostname}` : 'Inicializujem spojenie...' }}
        </p>
      </div>

      <div class="mt-8 md:mt-0 flex gap-4">
        <button 
          @click="fetchStatus" 
          class="flex items-center justify-center h-14 px-8 rounded-2xl glass-card text-white/50 hover:text-white transition-all shadow-xl hover:scale-105 active:scale-95 group overflow-hidden border border-white/5 font-black text-xs uppercase tracking-widest"
          :disabled="loading"
        >
          <RefreshCcw class="w-4 h-4 mr-3 relative z-10" :class="{ 'animate-spin': loading }" />
          <span class="relative z-10">{{ loading ? 'Syncing...' : 'Refresh' }}</span>
          <div class="absolute inset-0 bg-white/5 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
        </button>
      </div>
    </header>

    <!-- Stats Row -->
    <div class="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16" v-if="data">
      <div v-for="(stat, sIdx) in [
        { label: 'Network Endpoint', value: data.server.ip, icon: Server, color: 'primary-indigo' },
        { label: 'Matrix Host', value: data.server.hostname, icon: Globe, color: 'primary-cyan' },
        { label: 'API Throughput (24h)', value: data.api_calls_24h, icon: Zap, color: 'accent-green' },
        { label: 'Domain Capacity', value: `${onlineCount} / ${data.total}`, icon: Activity, color: 'primary-indigo' }
      ]" :key="sIdx"
        class="group glass-panel p-8 rounded-[32px] cursor-default transition-all duration-500 hover:translate-y-[-4px] hover:shadow-2xl"
      >
        <div class="flex items-center gap-5 mb-6">
          <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-white/10 transition-all duration-500 shadow-xl">
            <component :is="stat.icon" class="w-5 h-5 opacity-70" :class="`text-${stat.color}`" />
          </div>
          <h3 class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] leading-none">{{ stat.label }}</h3>
        </div>
        <div class="pl-1">
          <p class="text-2xl font-black text-white tracking-tighter truncate">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- Main Content Panel -->
    <div class="relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-200">
      
      <!-- Loading State -->
      <div v-if="loading && !data" class="glass-panel rounded-[40px] p-32 flex flex-col items-center justify-center gap-8 shadow-2xl">
        <div class="w-16 h-16 border-2 border-primary-cyan/20 border-t-primary-cyan rounded-full animate-spin"></div>
        <div class="flex flex-col items-center gap-2">
          <span class="text-white/20 text-[10px] font-black uppercase tracking-[0.4em]">Interrogating Domains...</span>
          <p class="text-white/10 text-xs italic">Verifying HTTPS handshakes and TTL records</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="glass-panel rounded-[40px] p-24 flex flex-col items-center justify-center gap-6 border-accent-rose/20 bg-accent-rose/5">
        <div class="w-20 h-20 rounded-full bg-accent-rose/10 flex items-center justify-center border border-accent-rose/20">
          <AlertTriangle class="w-10 h-10 text-accent-rose animate-pulse" />
        </div>
        <div class="text-center">
          <h3 class="text-2xl font-black text-white tracking-tight mb-2">Sync Error</h3>
          <p class="text-white/40 font-medium">{{ error }}</p>
        </div>
        <button @click="fetchStatus" class="px-8 py-3 bg-white text-slate-950 rounded-xl font-black text-[10px] uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-xl">
          Attempt Recon
        </button>
      </div>

      <!-- Domain List Panel -->
      <div v-else-if="data" class="glass-panel rounded-[40px] overflow-hidden shadow-2xl">
        <div class="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
          <div>
            <h2 class="text-3xl font-black text-white tracking-tighter line-height-none">Status Grid</h2>
            <p class="text-white/30 text-sm font-medium mt-1 tracking-tight">Detailný prehľad sieťovej dostupnosti</p>
          </div>
          <div class="flex items-center gap-3">
             <span class="px-5 py-2 glass-card rounded-2xl text-white/70 text-[10px] font-black uppercase tracking-[0.2em] border border-white/5">
              {{ data.domains.length }} NODES
            </span>
          </div>
        </div>

        <div class="table-wrap custom-scrollbar overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-white/[0.02]">
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] first:pl-12">Target Domain</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Gateway</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Response</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Encryption</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Entropy</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] last:pr-12">Integrity</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/[0.03]">
              <tr v-for="d in data.domains" :key="d.name" class="group hover:bg-white/[0.02] transition-colors duration-300">
                <td class="p-10 py-8 first:pl-12">
                  <div class="flex flex-col gap-1">
                    <span class="text-lg font-bold text-white tracking-tight group-hover:text-primary-cyan transition-colors">{{ d.name }}</span>
                    <span class="text-[9px] font-black text-white/10 uppercase tracking-widest">Global Entry Point</span>
                  </div>
                </td>
                <td class="p-10 py-8">
                  <span 
                    class="px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest border"
                    :class="d.registrar === 'Forpsi' ? 'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/20' : 'bg-primary-cyan/10 text-primary-cyan border-primary-cyan/20'"
                  >
                    {{ d.registrar }}
                  </span>
                </td>
                <td class="p-10 py-8">
                  <div v-if="d.http_status" class="flex items-center gap-3">
                    <div class="w-2 h-2 rounded-full" :class="d.http_status < 400 ? 'bg-accent-green' : 'bg-accent-rose'"></div>
                    <span class="text-base font-black tracking-tighter text-white/70">{{ d.http_status }}</span>
                  </div>
                  <span v-else class="text-white/10 text-xs font-bold italic">No Response</span>
                </td>
                <td class="p-10 py-8">
                  <div class="flex items-center gap-2">
                    <component :is="d.https_reachable ? ShieldCheck : ShieldAlert" 
                      class="w-4 h-4" 
                      :class="d.https_reachable ? 'text-accent-green' : 'text-accent-rose'" 
                    />
                    <span class="text-[10px] font-black uppercase tracking-widest" :class="d.https_reachable ? 'text-white/40' : 'text-accent-rose/60'">
                      {{ d.https_reachable ? 'Secure' : 'Insecure' }}
                    </span>
                  </div>
                </td>
                <td class="p-10 py-8">
                  <div v-if="d.ssl_expiry_days !== null" class="flex flex-col gap-1.5 min-w-[100px]">
                    <div class="flex justify-between items-end">
                      <span class="text-[10px] font-black uppercase tracking-widest" :class="sslColor(d.ssl_expiry_days)">{{ d.ssl_expiry_days }} Dni</span>
                    </div>
                    <div class="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                      <div class="h-full transition-all duration-1000" :class="sslBg(d.ssl_expiry_days)" :style="{ width: Math.min(100, (d.ssl_expiry_days / 90) * 100) + '%' }"></div>
                    </div>
                  </div>
                  <span v-else class="text-white/10 text-[10px] font-bold uppercase tracking-widest">N/A</span>
                </td>
                <td class="p-10 py-8 last:pr-12">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <div class="w-2 h-2 rounded-full shadow-[0_0_8px]" :class="isOnline(d) ? 'bg-accent-green shadow-accent-green/50' : 'bg-accent-rose shadow-accent-rose/50'"></div>
                    </div>
                    <span class="text-[10px] font-black uppercase tracking-[0.2em]" :class="isOnline(d) ? 'text-accent-green' : 'text-accent-rose'">
                      {{ isOnline(d) ? 'Operational' : 'Critical' }}
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
  Server, Globe, Zap, Activity, RefreshCcw, 
  ShieldCheck, ShieldAlert, AlertTriangle, Search, ChevronRight
} from 'lucide-vue-next';
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
    error.value = 'Chyba pri nadväzovaní spojenia s Nexus uzlom.';
  } finally {
    loading.value = false;
  }
};

const isOnline = (d) => d.http_status !== null && d.http_status < 500;
const onlineCount = computed(() => data.value?.domains.filter(isOnline).length ?? 0);

const sslColor = (days) => {
  if (days > 30) return 'text-accent-green';
  if (days > 7)  return 'text-primary-cyan';
  return 'text-accent-rose';
};

const sslBg = (days) => {
  if (days > 30) return 'bg-accent-green';
  if (days > 7)  return 'bg-primary-cyan';
  return 'bg-accent-rose';
};

onMounted(fetchStatus);
</script>

<style scoped>
/* Table padding adjustment for custom layout */
table th, table td {
  white-space: nowrap;
}
</style>
