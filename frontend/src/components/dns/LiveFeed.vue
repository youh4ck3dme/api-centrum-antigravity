<script setup>
const props = defineProps({
  feed: { type: Array, default: () => [] },
  wsStatus: { type: String, default: 'disconnected' },
  auditLoading: { type: Boolean, default: false }
});

const emit = defineEmits(['clear-feed', 'global-audit']);

const formatTime = (ts) => ts
  ? new Date(ts * 1000).toLocaleTimeString('sk-SK')
  : '';

const sevColor = (s) => ({
  CRITICAL: '#f43f5e', // accent-rose
  HIGH: '#fb923c',
  MEDIUM: '#eab308',   // warning
}[s] ?? '#94a3b8');

const feedClass = (item) => {
  if (item.severity === 'CRITICAL') return 'border-l-4 border-accent-rose bg-accent-rose/5';
  if (item.severity === 'HIGH') return 'border-l-4 border-orange-500 bg-orange-500/5';
  if (item.severity === 'MEDIUM') return 'border-l-4 border-warning bg-warning/5';
  if (item.type === 'heartbeat') return 'opacity-40 grayscale';
  return 'border-l-4 border-transparent hover:bg-white/[0.02]';
};

const feedMessage = (item) => {
  if (item.type === 'heartbeat')
    return `${item.domains_checked} domén skontrolovaných · ${item.threats_today} hrozieb dnes`;
  if (item.type === 'snapshot')
    return `Pripojený · ${item.domain_count} domén · ${item.threats_today} hrozieb dnes`;
  return item.message ?? '';
};
</script>

<template>
  <div class="glass-panel rounded-[40px] overflow-hidden flex flex-col shadow-2xl relative">
    <div class="p-8 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
      <div class="flex items-center gap-4">
        <div class="relative">
          <div class="w-3 h-3 rounded-full shadow-[0_0_12px]" :class="wsStatus === 'connected' ? 'bg-accent-green shadow-accent-green/50 animate-pulse' : 'bg-accent-rose shadow-accent-rose/50'"></div>
          <div v-if="wsStatus === 'connected'" class="absolute -inset-2 bg-accent-green/20 blur-xl rounded-full animate-pulse"></div>
        </div>
        <div>
          <h2 class="text-xl font-black text-white tracking-tighter leading-none mb-1.5 uppercase">Live Infrastructure Stream</h2>
          <p class="text-[9px] font-bold text-white/30 uppercase tracking-[0.3em] leading-none">Security Monitoring v4.0</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="emit('global-audit')" 
          class="px-5 py-2.5 rounded-2xl bg-white text-slate-950 text-[10px] font-black uppercase tracking-widest shadow-xl hover:translate-y-[-2px] active:translate-y-[0px] transition-all disabled:opacity-50 flex items-center gap-2" 
          :disabled="auditLoading"
        >
          <span v-if="!auditLoading">✨ AI Global Audit</span>
          <span v-else class="flex items-center gap-2">
             <div class="w-3 h-3 border-2 border-slate-950/20 border-t-slate-950 rounded-full animate-spin"></div>
             Analyzing Matrix...
          </span>
        </button>
        <button @click="emit('clear-feed')" class="w-10 h-10 flex items-center justify-center rounded-xl bg-white/5 border border-white/5 text-white/30 hover:text-white transition-all active:scale-95 outline-none">✕</button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar max-h-[600px] divide-y divide-white/[0.03]">
      <div v-if="feed.length === 0" class="flex flex-col items-center justify-center p-32 gap-6 opacity-20">
        <div class="w-12 h-12 border-2 border-dashed border-white rounded-full animate-spin-slow"></div>
        <span class="text-[10px] font-black uppercase tracking-[0.5em] text-center">Awaiting data<br/>packets...</span>
      </div>

      <div
        v-for="(item, i) in feed"
        :key="i"
        class="flex items-center gap-6 p-6 transition-all duration-300"
        :class="feedClass(item)"
      >
        <div class="min-w-[80px]">
           <span class="text-[10px] font-black text-white/20 tracking-widest">{{ formatTime(item.timestamp) }}</span>
        </div>
        
        <div class="min-w-[100px]">
          <span class="text-[9px] font-black uppercase tracking-[0.2em] px-2 py-1 rounded-md border" 
            :style="{ color: sevColor(item.severity), borderColor: sevColor(item.severity) + '1a', background: sevColor(item.severity) + '05' }"
            v-if="item.severity"
          >
            {{ item.severity }}
          </span>
          <span class="text-[9px] font-black uppercase tracking-[0.2em] text-primary-indigo" v-else-if="item.type === 'heartbeat'">Pulse</span>
          <span class="text-[9px] font-black uppercase tracking-[0.2em] text-primary-cyan" v-else-if="item.type === 'snapshot'">Init</span>
        </div>

        <div class="flex-1 flex flex-col gap-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold text-white tracking-tight truncate" v-if="item.domain">{{ item.domain }}</span>
            <span class="text-xs font-medium text-white/60 tracking-tight leading-relaxed">{{ feedMessage(item) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-spin-slow {
  animation: spin 8s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
