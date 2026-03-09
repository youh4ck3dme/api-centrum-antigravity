<template>
  <Login v-if="!isAuthenticated" @logged-in="checkAuth" />
  <div v-else class="app-root" :class="{ 'sidebar-open': isSidebarOpen }">

    <!-- Mobile Header -->
    <header class="mobile-header">
      <button @click="isSidebarOpen = !isSidebarOpen" class="menu-toggle">
        <span v-if="!isSidebarOpen">☰</span>
        <span v-else>✕</span>
      </button>
      <div class="navbar-brand">
        <div class="brand-icon">🌐</div>
        <span class="brand-name">API Centrum</span>
      </div>
      <div class="avatar">JD</div>
    </header>

    <!-- Sidebar / Navbar Container -->
    <nav class="navbar" :class="{ 'is-sidebar': !isDesktop, 'is-centered': isDesktop }">
      <div class="navbar-inner">
        <div class="navbar-brand" v-if="!isDesktop || true">
          <div class="brand-icon">🌐</div>
          <span class="brand-name">API Centrum</span>
        </div>

        <div class="nav-area">
          <div class="nav-tabs-wrapper">
            <div class="nav-tabs-label">Hlavné menu</div>
            <div class="nav-tabs">
              <button
                v-for="tab in mainTabs"
                :key="tab.id"
                @click="changeTab(tab.id)"
                class="nav-tab"
                :class="{ active: currentTab === tab.id }"
              >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.name }}</span>
              </button>
            </div>
          </div>

          <div class="nav-tabs-wrapper">
            <div class="nav-tabs-label">Extra nástroje</div>
            <div class="nav-tabs nav-tabs-extra">
              <button
                v-for="tab in extraTabs"
                :key="tab.id"
                @click="changeTab(tab.id)"
                class="nav-tab"
                :class="{ active: currentTab === tab.id }"
              >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.name }}</span>
              </button>
            </div>
          </div>
        </div>

        <div class="navbar-footer">
          <LicenseStatus 
            :is-unlimited="isUnlimited" 
            @open-modal="isModalOpen = true" 
          />
          <div class="user-profile">
            <div class="avatar">JD</div>
            <div class="user-info">
              <span class="user-name">Admin User</span>
              <button @click="logout" class="logout-link">Odhlásiť</button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="app-main">
      <div class="content-container">
        <transition name="fade" mode="out-in">
          <Dashboard v-if="currentTab === 'dashboard'" />
          <Domains v-else-if="currentTab === 'domains'" />
          <Backups v-else-if="currentTab === 'backups'" />
          <Performance v-else-if="currentTab === 'performance'" />
          <VPS v-else-if="currentTab === 'vps'" />
          <Radar v-else-if="currentTab === 'radar'" />
          <Notes v-else-if="currentTab === 'notes'" />
          <DNSMonitor v-else-if="currentTab === 'dns-monitor'" />
        </transition>
      </div>
    </main>

    <!-- Modals -->
    <LicenseActivationModal 
      v-if="isModalOpen" 
      :loading="activationLoading"
      :error="activationError"
      :success="activationSuccess"
      @close="closeModal" 
      @activate="handleActivateLicense" 
    />

    <!-- Overlay for mobile sidebar -->
    <div v-if="isSidebarOpen && !isDesktop" class="sidebar-overlay" @click="isSidebarOpen = false"></div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import Dashboard from "./views/Dashboard.vue";
import Domains from "./views/Domains.vue";
import Backups from "./views/Backups.vue";
import Performance from "./views/Performance.vue";
import VPS from "./views/VPS.vue";
import Radar from "./views/Radar.vue";
import Notes from "./views/Notes.vue";
import DNSMonitor from "./views/DNSMonitor.vue";
import Login from "./views/Login.vue";
import LicenseStatus from "./components/LicenseStatus.vue";
import LicenseActivationModal from "./components/LicenseActivationModal.vue";

const isAuthenticated = ref(!!localStorage.getItem('access_token'));
const isUnlimited = ref(false);
const currentTab = ref('dashboard');
const isSidebarOpen = ref(false);
const isDesktop = ref(window.innerWidth >= 1024);

// License Modal State
const isModalOpen = ref(false);
const activationLoading = ref(false);
const activationError = ref('');
const activationSuccess = ref('');

const tabs = [
  { id: 'dashboard',   name: 'Dashboard', icon: '📊' },
  { id: 'domains',     name: 'Domény',    icon: '🌐' },
  { id: 'dns-monitor', name: 'DNS Live',  icon: '🔴' },
  { id: 'backups',     name: 'Zálohy',    icon: '📦' },
  { id: 'performance', name: 'Výkon',     icon: '⚡' },
  { id: 'vps',         name: 'VPS',       icon: '🖥️' },
  { id: 'radar',       name: 'Radar',     icon: '🛡️' },
  { id: 'notes',       name: 'Poznámky',  icon: '📝' },
];

const mainTabs  = tabs.slice(0, 3);
const extraTabs = tabs.slice(3);

const checkAuth = () => {
  isAuthenticated.value = true;
  fetchLicenseStatus();
};

const logout = () => {
  localStorage.removeItem('access_token');
  isAuthenticated.value = false;
};

const changeTab = (tabId) => {
  currentTab.value = tabId;
  isSidebarOpen.value = false;
};

const fetchLicenseStatus = async () => {
  try {
    const res = await fetch('/api/license/status', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });
    if (res.ok) {
      const data = await res.json();
      isUnlimited.value = data.is_unlimited;
    }
  } catch (e) {}
};

const handleActivateLicense = async (key) => {
  activationLoading.value = true;
  activationError.value = '';
  activationSuccess.value = '';
  try {
    const res = await fetch('/api/license/activate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({ key })
    });
    const data = await res.json();
    if (res.ok) {
      activationSuccess.value = data.detail;
      isUnlimited.value = true;
      setTimeout(() => closeModal(), 2000);
    } else {
      activationError.value = data.detail || 'Chyba pri aktivácii.';
    }
  } catch (e) {
    activationError.value = 'Chyba spojenia so serverom.';
  } finally {
    activationLoading.value = false;
  }
};

const closeModal = () => {
  isModalOpen.value = false;
  activationError.value = '';
  activationSuccess.value = '';
};

const handleResize = () => {
  isDesktop.value = window.innerWidth >= 1024;
  if (isDesktop.value) isSidebarOpen.value = false;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  if (isAuthenticated.value) fetchLicenseStatus();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --sidebar-width: 260px;
  --navbar-height: 64px;
}

body {
  background: #080808;
  color: rgba(255,255,250,0.88);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text',
               'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

.app-root {
  min-height: 100vh;
  display: flex;
  background: #080808;
}

/* ── Mobile Header ─────────────────── */
.mobile-header {
  display: none;
  position: fixed; top: 0; left: 0; right: 0; height: var(--navbar-height);
  background: rgba(12,12,12,0.9); backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  z-index: 1000;
  padding: 0 1rem;
  align-items: center; justify-content: space-between;
}
@media (max-width: 1023px) { .mobile-header { display: flex; } }

.menu-toggle {
  background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer;
  width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;
}

/* ── Navbar Layouts ────────────────── */
.navbar {
  z-index: 1100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 1. Vertical Sidebar (Mobile/Tablet) */
.navbar.is-sidebar {
  position: fixed; top: 0; bottom: 0; left: 0;
  width: var(--sidebar-width);
  background: #0c0c0c;
  border-right: 1px solid rgba(255,255,255,0.05);
  transform: translateX(-100%);
  display: flex; flex-direction: column;
}
.app-root.sidebar-open .navbar.is-sidebar { transform: translateX(0); }

/* 2. Floating Centered (Desktop) */
.navbar.is-centered {
  position: fixed; top: 1.5rem; left: 50%;
  transform: translateX(-50%);
  width: min(90%, 1200px);
  background: rgba(15,15,15,0.8); backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.02);
}

.navbar-inner {
  height: 100%; width: 100%;
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 2rem;
}
.navbar.is-centered .navbar-inner {
  flex-direction: row; height: auto; align-items: center; padding: 0.75rem 1.5rem; gap: 2rem;
}

.navbar-brand { display: flex; align-items: center; gap: 0.8rem; }
.brand-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #1e1e1e, #0e0e0e);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}
.brand-name { font-weight: 700; color: #fff; letter-spacing: -0.02em; }

.nav-area { flex: 1; display: flex; flex-direction: column; gap: 1.5rem; }
.navbar.is-centered .nav-area { flex-direction: row; align-items: center; gap: 1rem; }

.nav-tabs-wrapper { display: flex; flex-direction: column; gap: 0.5rem; }
.navbar.is-centered .nav-tabs-wrapper { flex-direction: row; align-items: center; }

.nav-tabs-label {
  font-size: 0.65rem; font-weight: 800; color: rgba(255,255,255,0.2);
  text-transform: uppercase; letter-spacing: 0.1em; padding-left: 0.5rem;
}
.navbar.is-centered .nav-tabs-label { display: none; }

.nav-tabs {
  display: flex; flex-direction: column; gap: 4px;
}
.navbar.is-centered .nav-tabs { flex-direction: row; background: rgba(255,255,255,0.03); padding: 4px; border-radius: 12px; }

.nav-tab {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.75rem 1rem; border: none; border-radius: 12px;
  background: transparent; color: rgba(255,255,255,0.4);
  font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s;
  text-align: left;
}
.navbar.is-centered .nav-tab { padding: 0.5rem 0.9rem; font-size: 0.85rem; gap: 0.5rem; border-radius: 10px; }

.nav-tab:hover { color: #fff; background: rgba(255,255,255,0.05); }
.nav-tab.active { background: rgba(255,255,255,0.1); color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }

/* Footer / Profile */
.navbar-footer { margin-top: auto; display: flex; flex-direction: column; gap: 1rem; }
.navbar.is-centered .navbar-footer { margin-top: 0; flex-direction: row; align-items: center; margin-left: auto; }

.user-profile { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem; }
.user-info { display: flex; flex-direction: column; }
.navbar.is-centered .user-info { display: none; } /* On desktop, hide extra text for space */

.user-name { font-size: 0.85rem; font-weight: 600; color: #fff; }
.logout-link { background: none; border: none; color: #f87171; font-size: 0.75rem; cursor: pointer; text-align: left; }
.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: #27272a; border: 1px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; color: #94a3b8;
}

/* ── Main Content Area ──────────────── */
.app-main {
  flex: 1;
  width: 100%;
  padding-top: var(--navbar-height); /* For mobile header */
  min-height: 100vh;
}
@media (min-width: 1024px) {
  .app-root { padding-left: 0; }
  .app-main { padding-top: 5rem; } /* Room for floating header */
}

.content-container {
  max-width: 1400px; margin: 0 auto; padding: 2rem;
}
@media (max-width: 767px) { .content-container { padding: 1rem; } }

.sidebar-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); z-index: 1050;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
