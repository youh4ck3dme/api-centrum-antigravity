<script setup>
import { computed } from 'vue'
import { 
  LayoutDashboard, Globe, Zap, BarChart3, 
  FolderOpen, Bookmark, Server, Radar, 
  StickyNote, Terminal, Settings, LogOut, Search
} from 'lucide-vue-next'

const props = defineProps({
  activeTab: { type: String, default: 'dashboard' },
  isOpen: { type: Boolean, default: true }
})

const emit = defineEmits(['navigate', 'show-search'])

const menuItems = [
  { id: 'dashboard',   name: 'Dashboard',  icon: LayoutDashboard },
  { id: 'domains',     name: 'Domény',     icon: Globe },
  { id: 'dns-monitor', name: 'DNS Live',   icon: Zap },
  { id: 'monitoring',  name: 'Monitoring', icon: BarChart3 },
  { id: 'backups',     name: 'Zálohy',     icon: FolderOpen },
  { id: 'vps',         name: 'VPS',        icon: Server },
  { id: 'performance', name: 'Výkon',      icon: Bookmark },
  { id: 'radar',       name: 'Radar',      icon: Radar },
  { id: 'notes',       name: 'Poznámky',   icon: StickyNote },
  { id: 'terminal',    name: 'SSH',        icon: Terminal },
]

const activeIndex = computed(() => {
  return menuItems.findIndex(item => item.id === props.activeTab)
})

function handleNavigate(id) {
  emit('navigate', id)
}
</script>

<template>
  <aside 
    class="sidebar-aside w-[280px] h-[calc(100vh-40px)] m-5 rounded-[40px] glass-panel flex flex-col overflow-hidden shadow-premium border-black/5 fixed lg:sticky left-0 top-0 z-50 transition-all duration-700 ease-[cubic-bezier(0.16,1,0.3,1)]"
    :class="[isOpen ? 'translate-x-0' : '-translate-x-[120%] lg:translate-x-0 opacity-0 lg:opacity-100']"
  >
    <!-- Branding -->
    <div class="px-8 py-10 flex items-center gap-4 group cursor-pointer" @click="handleNavigate('dashboard')">
      <div class="w-12 h-12 rounded-2xl bg-primary-indigo/10 border border-primary-indigo/20 flex items-center justify-center shadow-sm transition-transform group-hover:scale-105">
        <div class="w-6 h-6 bg-primary-indigo rounded-lg"></div>
      </div>
      <div>
        <h1 class="text-xl font-black text-text-main tracking-widest leading-none">API<span class="text-primary-indigo">CENTRUM</span></h1>
        <p class="text-[9px] font-bold text-text-dim uppercase tracking-[0.3em] mt-2 leading-none">Management v4.0</p>
      </div>
    </div>

    <!-- Search Section -->
    <div class="px-6 mb-8">
      <button 
        @click="$emit('show-search')"
        class="w-full bg-black/[0.03] border border-black/5 rounded-2xl py-3 px-4 flex items-center justify-between group hover:bg-black/5 transition-all text-left shadow-sm"
      >
        <div class="flex items-center gap-3">
          <Search class="w-4 h-4 text-text-dim group-hover:text-text-main transition-colors" />
          <span class="text-xs text-text-dim font-bold uppercase tracking-widest">Hľadať...</span>
        </div>
        <div class="px-2 py-0.5 rounded-md border border-black/10 bg-black/5 text-[9px] text-text-dim font-black">
          ⌘K
        </div>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 space-y-1 overflow-y-auto custom-scrollbar relative">
      <!-- Active Pill Follower (optional visual enhancement) -->
      <div 
        v-if="activeIndex !== -1"
        class="absolute left-3 right-3 h-14 bg-primary-indigo/5 border border-primary-indigo/10 rounded-2xl transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] pointer-events-none z-0"
        :style="{ transform: `translateY(${activeIndex * 56}px)` }"
      ></div>

      <button
        v-for="item in menuItems"
        :key="item.id"
        @click="handleNavigate(item.id)"
        class="group flex items-center gap-4 px-6 py-4 rounded-2xl transition-all relative overflow-hidden active:scale-95 w-full text-left z-10"
        :class="activeTab === item.id ? 'text-primary-indigo' : 'text-text-dim hover:text-text-main'"
      >
        <component
          :is="item.icon"
          class="w-5 h-5 transition-all duration-300"
          :class="activeTab === item.id ? 'text-primary-indigo scale-110' : 'opacity-60'"
        />
        <span class="text-[11px] font-bold uppercase tracking-[0.1em]">{{ item.name }}</span>
      </button>
    </nav>

    <!-- Footer Profile -->
    <div class="mt-auto px-4 pb-8 space-y-3">
      <div class="flex items-center p-3 rounded-[24px] bg-black/[0.02] border border-black/5 hover:bg-black/[0.04] transition-all group cursor-pointer">
        <div class="w-10 h-10 rounded-xl overflow-hidden glass-card p-0.5 border-black/10 flex-shrink-0">
          <div class="w-full h-full bg-primary-indigo rounded-lg flex items-center justify-center text-[10px] font-black text-white shadow-sm">
            EB
          </div>
        </div>
        <div class="ml-3 min-w-0 flex-1">
          <h3 class="text-xs font-bold text-text-main truncate leading-none mb-1.5">Erik Babčan</h3>
          <div class="flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-accent-green"></span>
            <p class="text-[8px] text-text-dim uppercase font-black tracking-widest leading-none">Administrator</p>
          </div>
        </div>
      </div>

      <div class="flex gap-2">
        <button 
          @click="handleNavigate('settings')"
          class="flex-1 flex items-center justify-center py-3.5 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all group shadow-lg"
          :class="{ 'border-primary-indigo/30 bg-primary-indigo/5': activeTab === 'settings' }"
        >
          <Settings class="w-4 h-4 text-white/30 group-hover:text-white transition-colors" />
        </button>
        <button class="flex-1 flex items-center justify-center py-3.5 rounded-2xl bg-accent-rose/5 hover:bg-accent-rose/10 border border-accent-rose/10 transition-all group shadow-lg">
          <LogOut class="w-4 h-4 text-accent-rose/40 group-hover:text-accent-rose transition-colors" />
        </button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-aside {
  background: rgba(255, 255, 255, 0.4);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.1);
}
</style>
