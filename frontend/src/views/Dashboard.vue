<template>
  <div class="flex-1 p-6 lg:p-10 overflow-y-auto custom-scrollbar relative">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-12 animate-in fade-in slide-in-from-top-4 duration-700">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-accent-green shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"></span>
            <span class="text-[9px] uppercase font-black text-white/50 tracking-[0.2em]">Operational Status: Nominal</span>
          </div>
          <span v-if="lastUpdated" class="text-white/20 text-[9px] uppercase tracking-widest font-bold">
            Last Sync: {{ timeAgo(lastUpdated) }}
          </span>
        </div>
        <h1 class="text-4xl lg:text-7xl font-black text-white tracking-tighter leading-none">Command Center</h1>
        <p class="text-white/40 text-lg font-medium tracking-tight">Všetky systémy sú monitorované a plne funkčné.</p>
      </div>

      <div class="mt-8 md:mt-0 flex gap-4">
        <button 
          @click="reload" 
          class="flex items-center justify-center w-14 h-14 rounded-2xl glass-card text-white/50 hover:text-white transition-all shadow-xl hover:scale-105 active:scale-95 group overflow-hidden border border-white/5"
          :class="{ 'opacity-50 pointer-events-none': loading }"
        >
          <RefreshCcw class="w-5 h-5 relative z-10" :class="{ 'animate-spin': loading }" />
          <div class="absolute inset-0 bg-white/5 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
        </button>
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="relative z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-8 mb-16">
      <div 
        v-for="(stat, index) in stats" 
        :key="index"
        class="group glass-panel p-8 rounded-[32px] cursor-default relative overflow-hidden flex flex-col justify-between h-52 transition-all duration-500 hover:translate-y-[-4px]"
        :class="[flashIdx === index ? 'border-primary-indigo/50 bg-primary-indigo/10 ring-1 ring-primary-indigo/20' : '']"
        @mousemove="handleMouseMove"
        @mouseleave="resetTransform"
      >
        <div class="flex items-start justify-between relative z-10">
          <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center transition-all group-hover:scale-110 group-hover:bg-primary-indigo/10 group-hover:border-primary-indigo/20 shadow-xl">
            <component :is="getStatIcon(index)" class="w-5 h-5 text-white/60 group-hover:text-primary-indigo transition-colors" />
          </div>
          
          <div v-if="index === 1" class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-black/20 border border-white/5">
            <span class="w-1.5 h-1.5 rounded-full" :class="dbStatus === 'online' ? 'bg-accent-green' : 'bg-accent-rose'"></span>
            <span class="w-1.5 h-1.5 rounded-full" :class="apiStatus === 'online' ? 'bg-accent-green' : 'bg-accent-rose'"></span>
          </div>
        </div>

        <div class="relative z-10">
          <h3 class="text-5xl font-black text-white tracking-tighter leading-none mb-2">
            {{ stat.value }}
          </h3>
          <p class="text-[9px] font-black text-white/20 uppercase tracking-[0.3em] ml-1">{{ stat.subValue || 'Real-time telemetry' }}</p>
        </div>

        <!-- VPS Mini Metrics overlay -->
        <div v-if="index === 4 && vpsStats" class="absolute bottom-8 right-8 flex flex-col items-end gap-2 relative z-10">
           <div class="flex items-center gap-2">
             <div class="w-16 h-1 bg-white/5 rounded-full overflow-hidden shadow-inner">
               <div class="h-full transition-all duration-1000" :class="getBarColor(vpsStats.cpu_percent)" :style="{ width: vpsStats.cpu_percent + '%' }"></div>
             </div>
             <span class="text-[9px] font-black text-white/30 uppercase tracking-tighter">{{ vpsStats.cpu_percent }}%</span>
           </div>
        </div>
      </div>
    </div>

    <!-- Secondary Grid -->
    <div class="relative z-10 grid grid-cols-1 xl:grid-cols-3 gap-10">
      
      <!-- Activity Feed -->
      <div class="xl:col-span-2 glass-panel rounded-[40px] flex flex-col overflow-hidden shadow-2xl">
        <div class="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
          <div>
            <h2 class="text-3xl font-black text-white tracking-tighter line-height-none">System Activity</h2>
            <p class="text-white/30 text-sm font-medium mt-1 tracking-tight">Monitorované v reálnom čase cez Nexify Engine</p>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-accent-green animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
            <span class="px-5 py-2 glass-card rounded-2xl text-white/70 text-[10px] font-black uppercase tracking-[0.2em] border border-white/5">
              {{ recentActivity.length }} SESSIONS
            </span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar max-h-[550px]">
          <div v-if="loading && recentActivity.length === 0" class="flex flex-col items-center justify-center p-32 gap-6">
            <div class="w-12 h-12 border-2 border-primary-indigo/20 border-t-primary-indigo rounded-full animate-spin"></div>
            <span class="text-white/20 text-[10px] font-bold uppercase tracking-[0.4em]">Initializing Stream...</span>
          </div>
          
          <div v-else class="divide-y divide-white/[0.03]">
            <transition-group name="list">
              <div 
                v-for="item in recentActivity" 
                :key="item.id" 
                class="flex items-center gap-8 p-8 hover:bg-white/[0.02] transition-colors group cursor-default relative overflow-hidden"
              >
                <div class="w-16 h-16 flex items-center justify-center glass-card rounded-2xl text-3xl group-hover:scale-105 group-hover:bg-white/[0.05] transition-all duration-500 shadow-xl border border-white/5 relative z-10">
                  {{ item.icon }}
                </div>
                <div class="flex-1 relative z-10">
                  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <h4 class="text-xl font-bold text-white tracking-tight group-hover:text-primary-indigo transition-colors">{{ item.title }}</h4>
                    <span class="text-white/20 text-[9px] font-black uppercase tracking-[0.2em] bg-white/5 px-3 py-1 rounded-lg border border-white/5">{{ item.time }}</span>
                  </div>
                  <div class="flex mt-4 gap-3 items-center">
                    <span 
                      class="px-4 py-1.5 rounded-2xl text-[9px] font-black uppercase tracking-widest transition-all shadow-lg border"
                      :class="{
                        'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/30': item.color === 'badge-blue',
                        'bg-accent-green/10 text-accent-green border-accent-green/30': item.color === 'badge-green',
                        'bg-primary-cyan/10 text-primary-cyan border-primary-cyan/30': item.color === 'badge-purple',
                        'bg-white/5 text-white/30 border-white/10': item.color === 'badge-gray'
                      }"
                    >
                      {{ item.label }}
                    </span>
                    <span class="w-1 h-1 rounded-full bg-white/10"></span>
                    <span class="text-[10px] text-white/20 font-bold uppercase tracking-widest mt-0.5">Operation Secured</span>
                  </div>
                </div>
                <div class="absolute right-0 top-0 h-full w-24 bg-gradient-to-l from-primary-indigo/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </div>
            </transition-group>
          </div>
        </div>
      </div>

      <!-- System Health Metrics -->
      <div class="flex flex-col gap-10">
        <!-- Premium Promo / Help -->
        <div class="bg-primary-indigo rounded-[40px] p-10 text-white relative overflow-hidden shadow-2xl group cursor-pointer border border-white/10">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-indigo via-indigo-600 to-primary-cyan opacity-80 group-hover:opacity-100 transition-opacity"></div>
          <div class="absolute -right-20 -top-20 w-64 h-64 bg-white/10 blur-[80px] rounded-full group-hover:scale-125 transition-transform duration-1000"></div>
          
          <div class="relative z-10">
            <div class="w-14 h-14 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center mb-10 shadow-xl group-hover:scale-110 transition-transform">
              <ShieldCheck class="w-7 h-7 text-white" />
            </div>
            <h2 class="text-4xl font-black tracking-tighter mb-4 leading-none uppercase">Sentinel AI</h2>
            <p class="text-white/70 font-bold mb-12 leading-relaxed text-sm tracking-tight">Automatizovaná analýza infraštruktúry pod dohľadom Nexify v4.0.</p>
            <button class="w-full bg-white text-slate-950 py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] shadow-2xl hover:translate-y-[-2px] active:translate-y-[0px] transition-all flex items-center justify-center gap-3 group/btn">
              Spustiť Diagnostiku
              <ArrowUpRight class="w-4 h-4 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
            </button>
          </div>
        </div>

        <!-- Node Status -->
        <div class="glass-panel rounded-[40px] p-10 flex-1 flex flex-col shadow-xl">
          <h3 class="text-[10px] font-black uppercase tracking-[0.4em] text-white/20 mb-10 ml-2">Hardware Matrix</h3>
          
          <div class="space-y-6 flex-1">
            <div v-for="(node, nIdx) in [
              { name: 'Node Zero (DB)', status: dbStatus, icon: Database, color: 'accent-green' },
              { name: 'External Nexus', status: apiStatus, icon: Zap, color: 'primary-cyan' },
              { name: 'Primary VPS', status: 'online', icon: Server, color: 'primary-indigo' }
            ]" :key="nIdx" 
              class="flex items-center justify-between p-6 glass-card rounded-[28px] border-white/5 group hover:bg-white/[0.05] transition-all"
            >
              <div class="flex items-center gap-5">
                <div class="w-12 h-12 rounded-2xl flex items-center justify-center transition-all bg-white/5 border border-white/10 group-hover:scale-110 shadow-lg">
                  <component :is="node.icon" class="w-5 h-5 opacity-80" :class="`text-${node.color}`" />
                </div>
                <div>
                  <p class="text-[9px] font-black text-white/20 uppercase tracking-[0.3em] leading-none mb-1.5">{{ node.name }}</p>
                  <p class="text-white font-black text-base tracking-tighter">{{ node.status === 'online' ? 'NOMINAL' : 'OFFLINE' }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-2.5 h-2.5 rounded-full shadow-[0_0_8px]" :class="node.status === 'online' ? 'bg-accent-green shadow-accent-green/50' : 'bg-accent-rose shadow-accent-rose/50'"></div>
              </div>
            </div>
          </div>

          <!-- Disk Metric -->
          <div v-if="vpsStats" class="mt-12 p-8 rounded-[32px] bg-black/40 border border-white/5 relative group overflow-hidden shadow-inner">
             <div class="relative z-10">
               <div class="flex items-center justify-between mb-5">
                 <div class="flex items-center gap-3">
                   <HardDrive class="w-4 h-4 text-primary-cyan opacity-40 group-hover:rotate-12 transition-transform" />
                   <span class="text-[10px] font-black text-white/30 uppercase tracking-[0.3em]">Matrix Storage</span>
                 </div>
                 <span class="text-xs font-black text-white/70">{{ Math.round((vpsStats.disk_used_gb / vpsStats.disk_total_gb) * 100) }}%</span>
               </div>
               <div class="h-2.5 w-full bg-white/5 rounded-full overflow-hidden mb-3 p-0.5 border border-white/5">
                 <div class="h-full bg-gradient-to-r from-primary-indigo to-primary-cyan transition-all duration-1000 rounded-full" :style="{ width: Math.round((vpsStats.disk_used_gb / vpsStats.disk_total_gb) * 100) + '%' }"></div>
               </div>
               <div class="flex justify-between text-[9px] font-black text-white/20 tracking-[0.2em] mt-2">
                 <span>{{ vpsStats.disk_used_gb }}GB ALLOCATED</span>
                 <span>{{ vpsStats.disk_total_gb }}GB CAPACITY</span>
               </div>
             </div>
             <div class="absolute inset-0 bg-gradient-to-br from-primary-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
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
