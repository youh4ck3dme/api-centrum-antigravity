<script setup>
import { computed } from 'vue'
import { 
  LayoutDashboard, Globe, Zap, BarChart3, 
  FolderOpen, Bookmark, Server, Radar, 
  StickyNote, Terminal, Settings, LogOut, Search, Github
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
  { id: 'github',      name: 'GitHub',     icon: Github },
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
    class="sidebar-aside w-[260px] h-[calc(100vh-32px)] m-4 rounded-3xl glass-panel flex flex-col overflow-hidden border border-white/5 fixed lg:sticky left-0 top-0 z-50 transition-all duration-500 ease-out"
    :class="[isOpen ? 'translate-x-0' : '-translate-x-[120%] lg:translate-x-0 opacity-0 lg:opacity-100']"
  >
    <!-- Branding -->
    <div class="px-6 py-8 flex items-center gap-3 group cursor-pointer" @click="handleNavigate('dashboard')">
      <div class="w-10 h-10 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center transition-transform group-hover:scale-105">
        <div class="w-5 h-5 bg-brand-accent rounded-md shadow-[0_0_10px_rgba(245,158,11,0.3)]"></div>
      </div>
      <div>
        <h1 class="text-lg font-bold text-white tracking-widest leading-none">API<span class="text-brand-accent">CENTRUM</span></h1>
        <p class="text-[8px] font-mono text-gray-600 uppercase tracking-[0.2em] mt-2 leading-none">v4.0 // Industrial</p>
      </div>
    </div>

    <!-- Search Section -->
    <div class="px-4 mb-6">
      <button 
        @click="$emit('show-search')"
        class="w-full bg-white/5 border border-white/5 rounded-xl py-2.5 px-3 flex items-center justify-between group hover:bg-white/10 transition-all text-left"
      >
        <div class="flex items-center gap-2">
          <Search class="w-3.5 h-3.5 text-gray-600 group-hover:text-white transition-colors" />
          <span class="text-[10px] text-gray-600 font-bold uppercase tracking-widest">Hľadať...</span>
        </div>
        <div class="px-1.5 py-0.5 rounded border border-white/10 bg-white/5 text-[8px] text-gray-600 font-mono">
          MK
        </div>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-3 space-y-0.5 overflow-y-auto custom-scrollbar relative">
      <!-- Active Pill Follower (optional visual enhancement) -->
      

      <button
        v-for="item in menuItems"
        :key="item.id"
        @click="handleNavigate(item.id)"
        class="group flex items-center gap-3.5 px-4 py-3 rounded-xl transition-all relative overflow-hidden active:scale-95 w-full text-left z-10"
        :class="activeTab === item.id ? 'bg-white/5 text-white' : 'text-gray-600 hover:text-white hover:bg-white/[0.02]'"
      >
        <component
          :is="item.icon"
          class="w-4 h-4 transition-all duration-300"
          :class="activeTab === item.id ? 'text-brand-accent' : 'opacity-40 group-hover:opacity-100'"
        />
        <span class="text-[10px] font-bold uppercase tracking-[0.1em]">{{ item.name }}</span>
        <div v-if="activeTab === item.id" class="absolute left-0 top-1/4 bottom-1/4 w-0.5 bg-brand-accent rounded-full"></div>
      </button>
    </nav>

    <!-- Footer Profile -->
    <div class="mt-auto px-3 pb-6 space-y-2">
      <div class="flex items-center p-2.5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all group cursor-pointer">
        <div class="w-8 h-8 rounded-lg overflow-hidden border border-white/10 flex-shrink-0 bg-brand-accent/20 flex items-center justify-center text-[10px] font-bold text-white">
          EB
        </div>
        <div class="ml-3 min-w-0 flex-1">
          <h3 class="text-[11px] font-bold text-white truncate leading-none mb-1">Erik Babčan</h3>
          <div class="flex items-center gap-1.5">
            <span class="w-1 h-1 rounded-full bg-brand-success shadow-[0_0_5px_rgba(16,185,129,0.5)]"></span>
            <p class="text-[7px] font-mono text-gray-600 uppercase tracking-widest leading-none">Online</p>
          </div>
        </div>
      </div>

      <div class="flex gap-1.5">
        <button 
          @click="handleNavigate('settings')"
          class="flex-1 flex items-center justify-center py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all group"
          :class="{ 'border-brand-accent/20 bg-brand-accent/5': activeTab === 'settings' }"
        >
          <Settings class="w-3.5 h-3.5 text-gray-600 group-hover:text-white transition-colors" />
        </button>
        
        <button class="flex-1 flex items-center justify-center py-3 rounded-xl bg-brand-danger/5 hover:bg-brand-danger/10 border border-brand-danger/10 transition-all group">
          <LogOut class="w-3.5 h-3.5 text-brand-danger/40 group-hover:text-brand-danger transition-colors" />
        </button>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-aside {
  background: var(--theme-glass-base);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--theme-border-subtle);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--theme-overlay-hover);
}
</style>
