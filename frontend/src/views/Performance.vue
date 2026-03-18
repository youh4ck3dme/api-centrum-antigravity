<template>
  <div class="flex-1 p-6 lg:p-10 overflow-y-auto custom-scrollbar relative">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-accent-green shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"></span>
            <span class="text-[9px] uppercase font-black text-white/50 tracking-[0.2em]">Telemetry Stream: Active</span>
          </div>
          <span v-if="stats" class="text-white/20 text-[9px] uppercase tracking-widest font-bold">
            Analysis of {{ stats.count }} requests
          </span>
        </div>
        <h1 class="text-4xl lg:text-7xl font-black text-white tracking-tighter leading-none">Performance</h1>
        <p class="text-white/40 text-lg font-medium tracking-tight">Kvantitatívna analýza priepustnosti a latencie API.</p>
      </div>

      <div class="mt-8 md:mt-0 flex gap-4">
        <button 
          @click="toggleAuto" 
          class="flex items-center justify-center h-14 px-8 rounded-2xl glass-card transition-all shadow-xl hover:scale-105 active:scale-95 group overflow-hidden border border-white/5 font-black text-xs uppercase tracking-widest gap-3"
          :class="autoRefresh ? 'text-accent-green' : 'text-white/30'"
        >
          <div v-if="autoRefresh" class="w-2 h-2 rounded-full bg-accent-green animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
          <Activity v-else class="w-4 h-4" />
          <span>{{ autoRefresh ? 'Auto Sync ON' : 'Auto Sync OFF' }}</span>
          <div class="absolute inset-0 bg-white/5 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
        </button>

        <button 
          @click="fetchPerformance" 
          class="flex items-center justify-center w-14 h-14 rounded-2xl glass-card text-white/50 hover:text-white transition-all shadow-xl hover:scale-105 active:scale-95 group overflow-hidden border border-white/5"
          :disabled="loading"
        >
          <RefreshCcw class="w-5 h-5 relative z-10" :class="{ 'animate-spin': loading }" />
          <div class="absolute inset-0 bg-white/5 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
        </button>
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 mb-16" v-if="stats">
      <div v-for="(stat, sIdx) in [
        { label: 'Total Invocations', value: stats.count, icon: Zap, color: 'primary-cyan' },
        { label: 'Average Latency', value: `${stats.average_latency_ms} ms`, icon: Clock, color: 'primary-indigo', isLatency: true },
        { label: 'Status Distribution', isStatus: true, icon: CheckCircle2, color: 'accent-green' }
      ]" :key="sIdx"
        class="group glass-panel p-8 rounded-[32px] cursor-default transition-all duration-500 hover:translate-y-[-4px] hover:shadow-2xl overflow-hidden relative"
      >
        <div class="flex items-center gap-5 mb-6 relative z-10">
          <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-white/10 transition-all duration-500 shadow-xl">
            <component :is="stat.icon" class="w-5 h-5 opacity-70" :class="`text-${stat.color}`" />
          </div>
          <h3 class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] leading-none">{{ stat.label }}</h3>
        </div>

        <!-- Value Renderers -->
        <div class="relative z-10" v-if="!stat.isStatus">
          <p class="text-5xl font-black text-white tracking-tighter" :class="stat.isLatency ? latencyColor(stats.average_latency_ms) : ''">
            {{ stat.value }}
          </p>
        </div>
        <div class="relative z-10 flex flex-wrap gap-2 mt-1" v-else>
          <div v-for="(count, code) in stats.status_distribution" :key="code" 
            class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="String(code).startsWith('2') ? 'bg-accent-green shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-accent-rose shadow-[0_0_8px_rgba(244,63,94,0.5)]'"></span>
            <span class="text-xs font-black text-white/50 tracking-tighter">{{ code }}:</span>
            <span class="text-xs font-black text-white">{{ count }}</span>
          </div>
        </div>

        <!-- Decorative Glow -->
        <div class="absolute -right-8 -bottom-8 w-32 h-32 blur-[60px] rounded-full opacity-20 pointer-events-none transition-opacity group-hover:opacity-40" :class="`bg-${stat.color}`"></div>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      
      <!-- Empty State -->
      <div v-if="!stats || !stats.recent_metrics?.length" class="glass-panel rounded-[40px] p-32 flex flex-col items-center justify-center gap-6 shadow-2xl">
        <div class="w-20 h-20 rounded-[28px] bg-white/5 border border-white/10 flex items-center justify-center text-4xl shadow-xl border border-white/5">
           📭
        </div>
        <div class="text-center">
          <h3 class="text-2xl font-black text-white tracking-tight mb-2">No Data Available</h3>
          <p class="text-white/40 font-medium">Use the application to generate performance metrics.</p>
        </div>
      </div>

      <!-- Metrics Panel -->
      <div v-else class="glass-panel rounded-[40px] overflow-hidden shadow-2xl">
        <div class="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
          <div>
            <h2 class="text-3xl font-black text-white tracking-tighter line-height-none">Live Telemetry</h2>
            <p class="text-white/30 text-sm font-medium mt-1 tracking-tight">Posledných {{ stats.recent_metrics.length }} operácií v reálnom čase</p>
          </div>
          <div class="flex items-center gap-3">
             <span class="px-5 py-2 glass-card rounded-2xl text-white/70 text-[10px] font-black uppercase tracking-[0.2em] border border-white/5">
              REAL-TIME
            </span>
          </div>
        </div>

        <div class="table-wrap custom-scrollbar overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-white/[0.02]">
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] first:pl-12">API Target</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Method</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Latency</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Graph</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Status</th>
                <th class="p-10 py-6 text-[10px] font-black text-white/20 uppercase tracking-[0.4em] last:pr-12">Timestamp</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/[0.03]">
              <tr v-for="(m, idx) in [...stats.recent_metrics].reverse()" :key="idx" class="group hover:bg-white/[0.02] transition-colors duration-300">
                <td class="p-10 py-8 first:pl-12">
                   <span class="text-base font-bold text-white tracking-tight group-hover:text-primary-indigo transition-colors">{{ m.path }}</span>
                </td>
                <td class="p-10 py-8">
                  <span 
                    class="px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-[0.2em] shadow-lg border"
                    :class="methodStyle(m.method)"
                  >
                    {{ m.method }}
                  </span>
                </td>
                <td class="p-10 py-8">
                   <span class="text-lg font-black tracking-tighter" :class="latencyColor(m.latency * 1000)">
                    {{ (m.latency * 1000).toFixed(0) }} <span class="text-[10px] font-medium opacity-40 ml-0.5">ms</span>
                   </span>
                </td>
                <td class="p-10 py-8 min-w-[140px]">
                  <div class="h-1.5 w-full bg-white/5 rounded-full overflow-hidden shadow-inner border border-white/5">
                    <div 
                      class="h-full transition-all duration-1000 rounded-full" 
                      :class="latencyBg(m.latency * 1000)" 
                      :style="{ width: Math.min((m.latency * 1000) / 10, 100) + '%' }"
                    ></div>
                  </div>
                </td>
                <td class="p-10 py-8">
                   <div class="flex items-center gap-3">
                     <div class="w-2 h-2 rounded-full" :class="m.status < 400 ? 'bg-accent-green' : 'bg-accent-rose'"></div>
                     <span class="text-base font-black tracking-tighter text-white/70">{{ m.status }}</span>
                   </div>
                </td>
                <td class="p-10 py-8 last:pr-12">
                   <span class="text-[10px] font-black text-white/20 uppercase tracking-[0.2em] font-mono">
                     {{ formatTime(m.timestamp) }}
                   </span>
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
import { ref, onMounted, onUnmounted } from "vue";
import { 
  Zap, Clock, CheckCircle2, Activity, RefreshCcw, 
  ChevronRight, BarChart3, Database, Globe 
} from 'lucide-vue-next';
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
    timer = setInterval(fetchPerformance, 15000);
  } else {
    clearInterval(timer);
    timer = null;
  }
};

const latencyColor = (ms) => {
  if (ms < 300) return 'text-accent-green shadow-accent-green/20';
  if (ms < 600) return 'text-primary-cyan shadow-primary-cyan/20';
  return 'text-accent-rose shadow-accent-rose/20';
};

const latencyBg = (ms) => {
  if (ms < 300) return 'bg-accent-green shadow-[0_0_8px_rgba(34,197,94,0.5)]';
  if (ms < 600) return 'bg-primary-cyan shadow-[0_0_8px_rgba(6,182,212,0.5)]';
  return 'bg-accent-rose shadow-[0_0_8px_rgba(244,63,94,0.5)]';
};

const methodStyle = (method) => ({
  'GET':    'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/30',
  'POST':   'bg-accent-green/10 text-accent-green border-accent-green/30',
  'DELETE': 'bg-accent-rose/10 text-accent-rose border-accent-rose/30',
  'PUT':    'bg-primary-cyan/10 text-primary-cyan border-primary-cyan/30',
  'PATCH':  'bg-white/5 text-white border-white/20',
}[method] || 'bg-white/5 text-white/30 border-white/10');

const formatTime = (ts) => new Date(ts * 1000).toLocaleTimeString('sk-SK');

onMounted(fetchPerformance);
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
table th, table td {
  white-space: nowrap;
}
</style>
