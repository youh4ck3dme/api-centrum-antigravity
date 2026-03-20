<template>
  <div class="min-h-screen bg-black font-sans selection:bg-brand-accent/20 selection:text-brand-accent text-gray-900">
    <Login v-if="!isAuthenticated" @logged-in="checkAuth" />
    
    <div v-else class="flex min-h-screen relative overflow-hidden">
      <!-- Pure Minimalist Background -->
      <div class="fixed inset-0 pointer-events-none bg-black"></div>

      <!-- Mobile Header -->
      <header class="lg:hidden fixed top-0 left-0 right-0 h-16 glass-panel z-[3000] flex items-center justify-between px-6 border-b border-white/5">
        <div class="flex items-center gap-3">
          <button @click="isSidebarOpen = !isSidebarOpen" class="w-10 h-10 flex items-center justify-center rounded-xl bg-white/5 border border-white/10 active:scale-90 transition-transform">
            <Menu v-if="!isSidebarOpen" class="w-5 h-5 text-gray-600" />
            <X v-else class="w-5 h-5 text-gray-600" />
          </button>
          <div class="flex flex-col uppercase tracking-widest">
            <span class="font-bold text-[12px] text-white leading-none">API CENTRUM</span>
            <span class="text-[7px] font-bold text-brand-accent mt-1">Industrial Unit</span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <NotificationBell />
          <div class="w-8 h-8 rounded-full bg-white/10 border border-white/10 flex items-center justify-center text-[10px] font-bold text-white cursor-pointer" @click="showPopup = !showPopup">
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
      <main class="flex-1 min-h-screen overflow-x-hidden relative z-10 lg:pl-0">
        <div :class="['mx-auto h-full', currentTab === 'github' ? 'max-w-full w-full' : 'content-container p-4 lg:p-8 max-w-[1800px]']">
          <Suspense>
            <template #fallback>
              <div class="flex items-center justify-center h-[60vh]">
                <div class="w-8 h-8 border-2 border-white/10 border-t-brand-accent rounded-full animate-spin"></div>
              </div>
            </template>
            <transition 
              name="page" 
              mode="out-in"
            >
              <Dashboard v-if="currentTab === 'dashboard'" />
              <Domains v-else-if="currentTab === 'domains'" />
              <DNSMonitor v-else-if="currentTab === 'dns-monitor'" />
              <Backups v-else-if="currentTab === 'backups'" />
              <Performance v-else-if="currentTab === 'performance'" />
              <VPS v-else-if="currentTab === 'vps'" />
              <Radar v-else-if="currentTab === 'radar'" />
              <GithubProfile v-else-if="currentTab === 'github'" />
              <Notes v-else-if="currentTab === 'notes'" />
              <Terminal v-else-if="currentTab === 'terminal'" />
              <AppSettings v-else-if="currentTab === 'settings'" />
            </transition>
          </Suspense>
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
      <div v-if="isSidebarOpen" class="lg:hidden fixed inset-0 bg-black/80 backdrop-blur-sm z-[1500]" @click="isSidebarOpen = false"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineAsyncComponent, markRaw } from "vue";
import { Menu, X, Terminal, Search, Settings, Moon, Sun } from 'lucide-vue-next';
import { useTheme } from "./composables/useTheme";
import Login from "./views/Login.vue";

// Theme
const { isDark, toggleTheme } = useTheme();

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
const GithubProfile = markRaw(defineAsyncComponent(() => import("./views/GithubProfile.vue")));
const Notes = markRaw(defineAsyncComponent(() => import("./views/Notes.vue")));
const TerminalView = markRaw(defineAsyncComponent(() => import("./views/Terminal.vue")));
const AppSettings = markRaw(defineAsyncComponent(() => import("./views/Settings.vue")));

// Auth & State
const isAuthenticated = ref(!!localStorage.getItem('access_token'));
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
  { id: 'github',      label: 'GitHub' },
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
  background: var(--color-border-subtle);
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
