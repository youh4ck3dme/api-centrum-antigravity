<template>
  <div class="min-h-screen bg-bg-dark font-sans selection:bg-primary-indigo/10 selection:text-primary-indigo text-text-main">
    <Login v-if="!isAuthenticated" @logged-in="checkAuth" />
    
    <div v-else class="flex min-h-screen relative overflow-hidden">
      <!-- Pure Minimalist Background -->
      <div class="fixed inset-0 pointer-events-none bg-bg-dark"></div>

      <!-- Mobile Header -->
      <header class="lg:hidden fixed top-0 left-0 right-0 h-20 glass-panel z-[3000] flex items-center justify-between px-8 border-b border-white/5">
        <div class="flex items-center gap-4">
          <button @click="isSidebarOpen = !isSidebarOpen" class="w-12 h-12 flex items-center justify-center rounded-2xl bg-white/5 border border-white/10 active:scale-90 transition-transform shadow-xl">
            <Menu v-if="!isSidebarOpen" class="w-6 h-6 text-white/70" />
            <X v-else class="w-6 h-6 text-white/70" />
          </button>
          <div class="flex flex-col uppercase tracking-tighter">
            <span class="font-black text-white leading-none">API HUB</span>
            <span class="text-[8px] font-bold text-primary-indigo mt-0.5 tracking-widest">Mobile Unit</span>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <NotificationBell />
          <div class="w-8 h-8 rounded-lg glass-card flex items-center justify-center text-[10px] font-bold text-white cursor-pointer" @click="showPopup = !showPopup">
            {{ avatarDisplay }}
          </div>
        </div>
      </header>

      <!-- Sidebar -->
      <Sidebar 
        :activeTab="currentTab" 
        :isOpen="isSidebarOpen"
        @navigate="changeTab" 
        @show-search="showPalette = true"
      />

      <!-- Content -->
      <main class="flex-1 min-h-screen overflow-x-hidden relative z-10">
        <div class="content-container p-6 lg:p-10 max-w-[1800px] mx-auto">
          <transition 
            name="page" 
            mode="out-in"
            enter-active-class="transition duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
            enter-from-class="transform translate-y-4 opacity-0 scale-[0.98]"
            enter-to-class="transform translate-y-0 opacity-100 scale-100"
            leave-active-class="transition duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
            leave-from-class="transform translate-y-0 opacity-100 scale-100"
            leave-to-class="transform -translate-y-4 opacity-0 scale-[1.02]"
          >
            <Dashboard v-if="currentTab === 'dashboard'" />
            <Domains v-else-if="currentTab === 'domains'" />
            <DNSMonitor v-else-if="currentTab === 'dns-monitor'" />
            <Backups v-else-if="currentTab === 'backups'" />
            <Performance v-else-if="currentTab === 'performance'" />
            <VPS v-else-if="currentTab === 'vps'" />
            <Radar v-else-if="currentTab === 'radar'" />
            <Notes v-else-if="currentTab === 'notes'" />
            <Terminal v-else-if="currentTab === 'terminal'" />
            <AppSettings v-else-if="currentTab === 'settings'" />
          </transition>
        </div>
      </main>

      <!-- Global Overlays -->
      <LicenseActivationModal v-if="isModalOpen" @close="closeModal" @activate="handleActivateLicense" />
      <AIChat />
      <CommandPalette
        v-if="showPalette"
        :tabs="tabs"
        @close="showPalette = false"
        @navigate="changeTab"
        @logout="logout"
      />
      <UserPopup v-if="showPopup" :email="userEmail" @close="showPopup = false" @navigate="changeTab" />
      
      <!-- Mobile Sidebar Overlay -->
      <div v-if="isSidebarOpen" class="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-md z-[1500]" @click="isSidebarOpen = false"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineAsyncComponent, markRaw } from "vue";
import { Menu, X, Terminal, Search, Settings } from 'lucide-vue-next';
import Login from "./views/Login.vue";

// Components
import Sidebar from "./components/Sidebar.vue";
import LicenseActivationModal from "./components/LicenseActivationModal.vue";
import AIChat from "./components/AIChat.vue";
import UserPopup from "./components/UserPopup.vue";
import CommandPalette from "./components/CommandPalette.vue";
import NotificationBell from "./components/NotificationBell.vue";

// Views
const Dashboard = markRaw(defineAsyncComponent(() => import("./views/Dashboard.vue")));
const Domains = markRaw(defineAsyncComponent(() => import("./views/Domains.vue")));
const DNSMonitor = markRaw(defineAsyncComponent(() => import("./views/DNSMonitor.vue")));
const Backups = markRaw(defineAsyncComponent(() => import("./views/Backups.vue")));
const Performance = markRaw(defineAsyncComponent(() => import("./views/Performance.vue")));
const VPS = markRaw(defineAsyncComponent(() => import("./views/VPS.vue")));
const Radar = markRaw(defineAsyncComponent(() => import("./views/Radar.vue")));
const Notes = markRaw(defineAsyncComponent(() => import("./views/Notes.vue")));
const TerminalView = markRaw(defineAsyncComponent(() => import("./views/Terminal.vue")));
const AppSettings = markRaw(defineAsyncComponent(() => import("./views/Settings.vue")));

// Auth & State
const isAuthenticated = ref(true);
const currentTab = ref(window.location.pathname.substring(1) || 'dashboard');
const isSidebarOpen = ref(false);
const showPalette = ref(false);
const showPopup = ref(false);
const userEmail = ref('');
const isModalOpen = ref(false);

const tabs = [
  { id: 'dashboard',   label: 'Dashboard' },
  { id: 'domains',     label: 'Domény' },
  { id: 'dns-monitor', label: 'DNS Live' },
  { id: 'backups',     label: 'Zálohy' },
  { id: 'performance', label: 'Výkon' },
  { id: 'vps',         label: 'VPS' },
  { id: 'radar',       label: 'Radar' },
  { id: 'notes',       label: 'Poznámky' },
  { id: 'terminal',   label: 'SSH' },
  { id: 'settings',  label: 'Nastavenia' },
];

const avatarDisplay = computed(() => {
  const stored = localStorage.getItem('user-avatar');
  return stored || 'EB'; // user is Erik Babčan
});

const changeTab = (tabId) => {
  currentTab.value = tabId;
  isSidebarOpen.value = false;
  showPalette.value = false;
  window.history.pushState({}, '', `/${tabId}`);
};

const checkAuth = () => {
  isAuthenticated.value = true;
  fetchUser();
};

const logout = () => {
  localStorage.removeItem('access_token');
  isAuthenticated.value = false;
};

const fetchUser = async () => {
  try {
    const res = await fetch('/api/users/me', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });
    if (res.ok) {
      const data = await res.json();
      userEmail.value = data.email || '';
    }
  } catch (e) {}
};

// Keys
const onKey = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    if (isAuthenticated.value) showPalette.value = !showPalette.value;
  }
};

onMounted(() => {
  window.addEventListener('keydown', onKey);
  if (isAuthenticated.value) fetchUser();
  window.addEventListener('popstate', () => {
    currentTab.value = window.location.pathname.substring(1) || 'dashboard';
  });
});

onUnmounted(() => {
  window.removeEventListener('keydown', onKey);
});
</script>

<style>
@import "tailwindcss";

/* Global Refinements */
body {
  margin: 0;
  background: var(--color-bg-dark);
  color: var(--color-text-main);
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.content-container {
  max-width: 1600px;
  margin: 0 auto;
}

@media (max-width: 1023px) {
  .content-container {
    padding-top: 4rem;
  }
}

/* Page Transitions */
.page-enter-active, .page-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(1.02);
}
</style>
