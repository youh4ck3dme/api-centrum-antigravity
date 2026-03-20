<template>
  <div class="flex-1 p-4 lg:p-8 overflow-y-auto custom-scrollbar relative">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-10 animate-in fade-in slide-in-from-top-4 duration-700">
      <div class="space-y-3">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-2.5 py-1 rounded-md bg-white/5 border border-white/5 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-success shadow-[0_0_8px_rgba(16,185,129,0.6)] animate-pulse"></span>
            <span class="text-[8px] font-mono text-gray-600 uppercase tracking-widest">System Status: Nominal</span>
          </div>
          <span v-if="lastUpdated" class="text-gray-600 text-[8px] font-mono uppercase tracking-widest">
            Last Sync: {{ timeAgo(lastUpdated) }}
          </span>
        </div>
        <h1 class="text-4xl lg:text-6xl font-bold text-white tracking-tight leading-none italic">Command Center <span class="text-brand-accent">v4.0</span></h1>
        <p class="text-gray-600 text-sm font-medium tracking-tight">Monitorovanie infraštruktúry v reálnom čase.</p>
      </div>

      <div class="mt-6 md:mt-0 flex gap-3">
        <button 
          @click="reload" 
          class="flex items-center justify-center w-12 h-12 rounded-xl bg-white/5 hover:bg-white/10 text-gray-600 hover:text-white transition-all border border-white/5"
          :class="{ 'opacity-50 pointer-events-none': loading }"
        >
          <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </header>

    <!-- Stats Grid (Bento Style) -->
    <div class="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4 mb-10">
      <div 
        v-for="(stat, index) in stats" 
        :key="index"
        class="group bg-[#0B0C0E] p-6 rounded-2xl border border-white/5 cursor-default relative overflow-hidden flex flex-col justify-between h-44 transition-all duration-300 hover:border-white/20"
      >
        <div class="flex items-start justify-between relative z-10">
          <div class="w-10 h-10 rounded-lg bg-white/5 border border-white/5 flex items-center justify-center transition-all group-hover:bg-brand-accent/10 group-hover:border-brand-accent/20">
            <component :is="getStatIcon(index)" class="w-4 h-4 text-gray-600 group-hover:text-brand-accent transition-colors" />
          </div>
          
          <div v-if="index === 1" class="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-white/5 border border-white/5">
            <span class="w-1 h-1 rounded-full" :class="dbStatus === 'online' ? 'bg-brand-success' : 'bg-brand-danger'"></span>
            <span class="w-1 h-1 rounded-full" :class="apiStatus === 'online' ? 'bg-brand-success' : 'bg-brand-danger'"></span>
          </div>
        </div>

        <div class="relative z-10">
          <h3 class="text-4xl font-bold text-white tracking-tight leading-none mb-1">
            {{ stat.value }}
          </h3>
          <p class="text-[8px] font-mono text-gray-600 uppercase tracking-widest">{{ stat.subValue || 'RT-TELEMETRY' }}</p>
        </div>
      </div>
    </div>

    <!-- Secondary Grid -->
    <div class="relative z-10 grid grid-cols-1 xl:grid-cols-3 gap-6">
      
      <!-- Activity Feed -->
      <div class="xl:col-span-2 bg-[#0B0C0E] rounded-3xl border border-white/5 flex flex-col overflow-hidden">
        <div class="p-6 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
          <div>
            <h2 class="text-xl font-bold text-white tracking-tight">Systémová Aktivita</h2>
            <p class="text-gray-600 text-[10px] font-mono mt-1 uppercase tracking-widest">Nexify Engine v4.0 // Secured Stream</p>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-1.5 h-1.5 rounded-full bg-brand-success animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <span class="px-3 py-1 bg-white/5 rounded-lg text-gray-600 text-[9px] font-mono uppercase tracking-widest border border-white/5">
              {{ recentActivity.length }} SESSIONS
            </span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar max-h-[450px]">
          <div v-if="loading && recentActivity.length === 0" class="flex flex-col items-center justify-center p-20 gap-4">
            <div class="w-8 h-8 border-2 border-white/5 border-t-brand-accent rounded-full animate-spin"></div>
            <span class="text-gray-600 text-[8px] font-mono uppercase tracking-widest">Connecting to Matrix...</span>
          </div>
          
          <div v-else class="divide-y divide-white/5">
            <transition-group name="list">
              <div 
                v-for="item in recentActivity" 
                :key="item.id" 
                class="flex items-center gap-6 p-6 hover:bg-white/[0.02] transition-colors group cursor-default"
              >
                <div class="w-12 h-12 flex items-center justify-center bg-white/5 rounded-xl group-hover:bg-white/10 transition-all border border-white/5 shrink-0">
                  <span class="text-xl">{{ item.icon }}</span>
                </div>
                <div class="flex-1">
                  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <h4 class="text-sm font-bold text-white tracking-tight group-hover:text-brand-accent transition-colors">{{ item.title }}</h4>
                    <span class="text-gray-600 text-[8px] font-mono uppercase tracking-widest">{{ item.time }}</span>
                  </div>
                  <div class="flex mt-2 gap-3 items-center">
                    <span 
                      class="px-2 py-0.5 rounded-md text-[8px] font-mono uppercase tracking-widest border"
                      :class="{
                        'bg-white/5 text-white border-white/10': item.color === 'badge-blue' || item.color === 'badge-gray',
                        'bg-brand-success/10 text-brand-success border-brand-success/20': item.color === 'badge-green',
                        'bg-brand-accent/10 text-brand-accent border-brand-accent/20': item.color === 'badge-purple'
                      }"
                    >
                      {{ item.label }}
                    </span>
                    <span class="w-1 h-1 rounded-full bg-white/10"></span>
                    <span class="text-[8px] text-gray-600 font-mono uppercase tracking-widest">Secured</span>
                  </div>
                </div>
              </div>
            </transition-group>
          </div>
        </div>
      </div>

      <!-- System Health Metrics -->
      <div class="flex flex-col gap-6">
        <!-- AI Sentinel Status -->
        <div class="bg-brand-accent rounded-3xl p-8 text-black relative overflow-hidden group border border-brand-accent">
          <div class="relative z-10">
            <div class="w-12 h-12 rounded-xl bg-black border border-black flex items-center justify-center mb-6 shadow-xl">
              <ShieldCheck class="w-6 h-6 text-brand-accent" />
            </div>
            <h2 class="text-3xl font-bold tracking-tight mb-2 leading-none italic">SENTINEL AI</h2>
            <p class="text-black/70 font-bold mb-8 leading-tight text-[11px] uppercase tracking-widest">AUTONOMOUS ANALYTICS ENGINE // v4.0</p>
            <button class="w-full bg-black text-brand-accent py-4 rounded-xl font-bold text-[10px] uppercase tracking-widest shadow-xl hover:translate-y-[-1px] transition-all flex items-center justify-center gap-2">
              Run Diagnostics
              <ArrowUpRight class="w-3 h-3" />
            </button>
          </div>
        </div>

        <!-- Node Status -->
        <div class="bg-[#0B0C0E] rounded-3xl p-6 border border-white/5 flex-1 shadow-xl">
          <h3 class="text-[8px] font-mono font-bold uppercase tracking-widest text-gray-600 mb-6">MATRIX HARDWARE STATUS</h3>
          
          <div class="space-y-3">
            <div v-for="(node, nIdx) in [
              { name: 'Node Zero (DB)', status: dbStatus, icon: Database, color: 'brand-success' },
              { name: 'External Nexus', status: apiStatus, icon: Zap, color: 'brand-accent' },
              { name: 'Primary VPS', status: 'online', icon: Server, color: 'white' }
            ]" :key="nIdx" 
              class="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 group hover:border-white/20 transition-all cursor-default"
            >
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center transition-all bg-white/5 border border-white/5">
                  <component :is="node.icon" class="w-4 h-4" :class="`text-${node.color}`" />
                </div>
                <div>
                  <p class="text-[8px] font-mono text-gray-600 uppercase tracking-widest leading-none mb-1">{{ node.name }}</p>
                  <p class="text-white font-bold text-sm tracking-tight">{{ node.status === 'online' ? 'NOMINAL' : 'OFFLINE' }}</p>
                </div>
              </div>
              <div class="w-1.5 h-1.5 rounded-full" :class="node.status === 'online' ? 'bg-brand-success shadow-[0_0_5px_#10B981]' : 'bg-brand-danger'"></div>
            </div>
          </div>

          <!-- Disk Metric -->
          <div v-if="vpsStats" class="mt-8 p-6 rounded-2xl bg-white/[0.03] border border-white/5 relative group overflow-hidden">
             <div class="relative z-10">
               <div class="flex items-center justify-between mb-4">
                 <div class="flex items-center gap-3">
                   <HardDrive class="w-3.5 h-3.5 text-gray-600" />
                   <span class="text-[8px] font-mono text-gray-600 uppercase tracking-widest">Storage Status</span>
                 </div>
                 <span class="text-[10px] font-mono text-white">{{ Math.round((vpsStats.disk_used_gb / vpsStats.disk_total_gb) * 100) }}%</span>
               </div>
               <div class="h-1.5 w-full bg-white/5 rounded-full overflow-hidden mb-2">
                 <div class="h-full bg-brand-accent transition-all duration-1000" :style="{ width: Math.round((vpsStats.disk_used_gb / vpsStats.disk_total_gb) * 100) + '%' }"></div>
               </div>
               <div class="flex justify-between text-[7px] font-mono text-gray-600 tracking-widest mt-2 uppercase">
                 <span>{{ vpsStats.disk_used_gb }}GB ALLOCATED</span>
                 <span>{{ vpsStats.disk_total_gb }}GB TOTAL</span>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { 
  CheckCircle2, Clock, Users, Globe, Activity, 
  AlertTriangle, Cpu, HardDrive, RefreshCcw, 
  ArrowUpRight, ArrowDownRight, Loader2, Database, Zap, Server, ShieldCheck
} from 'lucide-vue-next'
import { useStats } from '../composables/useStats'

const { 
  stats, recentActivity, loading, lastUpdated, 
  vpsStats, dbStatus, apiStatus, flashIdx, ramPct, 
  loadStats, loadVPS, reload 
} = useStats()

const timeAgo = (date) => {
  if (!date) return ''
  const s = Math.floor((Date.now() - date.getTime()) / 1000)
  if (s < 10) return 'práve teraz'
  if (s < 60) return `${s}s`
  return `${Math.floor(s/60)}m`
}

const getStatIcon = (index) => {
  const icons = [Globe, Activity, ArrowUpRight, AlertTriangle, Cpu]
  return icons[index] || Globe
}

const getBarColor = (p) => {
  if (p >= 85) return 'bg-accent-rose shadow-[0_0_8px_rgba(244,63,94,0.5)]'
  if (p >= 60) return 'bg-primary-indigo shadow-[0_0_8px_rgba(79,70,229,0.5)]'
  return 'bg-primary-cyan shadow-[0_0_8px_rgba(6,182,212,0.5)]'
}

const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const rY = (x / rect.width - 0.5) * 8
  const rX = (y / rect.height - 0.5) * -8
  
  e.currentTarget.style.transform = `perspective(1000px) rotateX(${rX}deg) rotateY(${rY}deg) translateY(-8px)`
  e.currentTarget.style.boxShadow = `0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.08)`
}

const resetTransform = (e) => {
  e.currentTarget.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)'
  e.currentTarget.style.boxShadow = 'none'
}

let refreshTimer = null
onMounted(() => {
  loadStats()
  loadVPS()
  refreshTimer = setInterval(() => { loadStats(); loadVPS(); }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.list-enter-active, .list-leave-active {
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.list-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
.list-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(1.02);
}
</style>
