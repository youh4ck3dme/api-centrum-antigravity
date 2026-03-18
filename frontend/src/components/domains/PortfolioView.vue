<script setup>
import { Globe, AlertTriangle, Clock, Database, XCircle } from 'lucide-vue-next';

const props = defineProps({
  portfolioData: { type: Object, default: null },
  portfolioLoading: { type: Boolean, default: false }
});
</script>

<template>
  <div v-if="portfolioLoading" class="flex-1 flex flex-col items-center justify-center p-48 gap-8">
    <div class="w-16 h-16 border-4 border-white/5 border-t-primary-cyan rounded-full animate-spin"></div>
    <span class="text-white/20 text-[10px] font-bold uppercase tracking-[0.5em]">Deep Portfolio Analysis...</span>
  </div>
  
  <div v-else-if="portfolioData" class="space-y-12 animate-in fade-in zoom-in-95 duration-700">
    <!-- Stat cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-8">
      <div v-for="(stat, sIdx) in [
        { label: 'Asset Total', val: portfolioData.total + ' domén', icon: Globe, color: 'indigo' },
        { label: 'Critical Risk', val: portfolioData.critical, icon: AlertTriangle, color: 'rose', critical: true },
        { label: 'Warning Status', val: portfolioData.warning, icon: Clock, color: 'warning' },
        { label: 'Annual Overhead', val: '~' + portfolioData.annual_cost_eur + '€', icon: Database, color: 'green' }
      ]" :key="sIdx" 
        class="glass-panel p-8 rounded-[32px] flex flex-col gap-6 group hover:translate-y-[-4px] transition-all"
        :class="stat.critical && stat.val > 0 ? 'border-accent-rose/30 bg-accent-rose/5 ring-1 ring-accent-rose/20' : ''"
      >
        <div class="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-2xl group-hover:scale-110 group-hover:bg-white/10 transition-all">
          <component :is="stat.icon" class="w-6 h-6 opacity-60" :class="`text-${stat.color}-400`" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mb-2">{{ stat.label }}</p>
          <h3 class="text-4xl font-bold text-white tracking-tighter leading-none">{{ stat.val }}</h3>
        </div>
      </div>
    </div>

    <!-- Expiry Table -->
    <div class="glass-panel rounded-[40px] overflow-hidden shadow-2xl">
      <div class="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
        <div>
          <h2 class="text-3xl font-bold text-white tracking-tighter">Expirácia Aktív</h2>
          <p class="text-white/30 text-sm mt-1 font-medium tracking-tight">Včasná obnova garantuje stabilitu služieb</p>
        </div>
        <div class="px-5 py-2 glass-card rounded-2xl text-white/70 text-[10px] font-bold uppercase tracking-widest border border-white/10">
          {{ portfolioData.domains.length }} ASSETS RECORDED
        </div>
      </div>
      
      <div class="overflow-x-auto custom-scrollbar">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-white/[0.02] border-b border-white/5">
              <th class="p-8 text-[10px] font-bold text-white/20 uppercase tracking-widest">Digital Asset</th>
              <th class="p-8 text-[10px] font-bold text-white/20 uppercase tracking-widest">Registrar Hub</th>
              <th class="p-8 text-[10px] font-bold text-white/20 uppercase tracking-widest">Time Remaining</th>
              <th class="p-8 text-[10px] font-bold text-white/20 uppercase tracking-widest">Auto-Scale</th>
              <th class="p-8 text-[10px] font-bold text-white/20 uppercase tracking-widest text-right">Risk Score</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/[0.03]">
            <tr v-for="d in portfolioData.domains" :key="d.name" class="group hover:bg-white/[0.02] transition-colors">
              <td class="p-8">
                <div class="flex items-center gap-4">
                   <div class="w-2 h-2 rounded-full" :class="d.days_until_expiry < 30 ? 'bg-accent-rose animate-pulse' : 'bg-accent-green'"></div>
                   <span class="font-mono text-base text-white font-bold tracking-tighter">{{ d.name }}</span>
                </div>
              </td>
              <td class="p-8">
                <span class="px-3 py-1 rounded-xl text-[10px] font-bold uppercase tracking-widest border border-white/10 bg-white/5 text-white/40">
                  {{ d.registrar }}
                </span>
              </td>
              <td class="p-8">
                <div v-if="d.days_until_expiry !== null" class="flex flex-col gap-1.5">
                   <div class="w-32 h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div class="h-full bg-primary-indigo transition-all duration-1000" :class="d.days_until_expiry < 30 ? 'bg-accent-rose' : ''" :style="{ width: Math.min(100, (d.days_until_expiry / 365) * 100) + '%' }"></div>
                   </div>
                   <span class="text-xs text-white/50 font-bold">{{ d.days_until_expiry }} dní</span>
                </div>
                <span v-else class="text-white/10">—</span>
              </td>
              <td class="p-8">
                <div v-if="d.autoExtend === true" class="text-accent-green flex items-center gap-2.5 text-xs font-bold uppercase tracking-widest">
                  <div class="w-1.5 h-1.5 rounded-full bg-accent-green shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div> Active
                </div>
                <div v-else-if="d.autoExtend === false" class="text-accent-rose flex items-center gap-2.5 text-xs font-bold uppercase tracking-widest opacity-40">
                  <XCircle class="w-3.5 h-3.5" /> Manual
                </div>
                <span v-else class="text-white/10">—</span>
              </td>
              <td class="p-8 text-right">
                <span 
                  class="px-4 py-1.5 rounded-2xl text-[10px] font-bold uppercase tracking-[0.1em] inline-block shadow-lg border"
                  :class="{
                    'bg-accent-rose/10 text-accent-rose border-accent-rose/20': d.risk === 'critical',
                    'bg-warning/10 text-warning border-warning/20': d.risk === 'warning',
                    'bg-accent-green/10 text-accent-green border-accent-green/20': d.risk === 'safe',
                    'bg-white/5 text-white/20 border-white/5': !['critical','warning','safe'].includes(d.risk)
                  }"
                >
                  {{ d.risk === 'critical' ? 'Kritické' : d.risk === 'warning' ? 'Varovanie' : 'Stabilné' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
