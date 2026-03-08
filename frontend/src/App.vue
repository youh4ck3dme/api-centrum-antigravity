<template>
  <Login v-if="!isAuthenticated" @logged-in="isAuthenticated = true" />
  <div v-else class="app-root">

    <!-- Navbar -->
    <nav class="navbar">
      <div class="navbar-inner">
        <div class="navbar-brand">
          <div class="brand-icon">🌐</div>
          <span class="brand-name">API Centrum</span>
        </div>

        <div class="nav-area">
          <div class="nav-tabs">
            <button
              v-for="tab in mainTabs"
              :key="tab.id"
              @click="currentTab = tab.id"
              class="nav-tab"
              :class="{ active: currentTab === tab.id }"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-label">{{ tab.name }}</span>
            </button>
          </div>
          <div class="nav-tabs nav-tabs-extra">
            <button
              v-for="tab in extraTabs"
              :key="tab.id"
              @click="currentTab = tab.id"
              class="nav-tab"
              :class="{ active: currentTab === tab.id }"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-label">{{ tab.name }}</span>
            </button>
          </div>
        </div>

        <div class="navbar-right">
          <button class="icon-btn">🔔</button>
          <div class="avatar">JD</div>
          <button @click="logout" class="logout-btn">Odhlásiť</button>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <main class="app-main">
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
    </main>

    <!-- Mobile nav -->
    <div class="mobile-nav">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="currentTab = tab.id"
        class="mobile-tab"
        :class="{ active: currentTab === tab.id }"
      >
        <span>{{ tab.icon }}</span>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref } from "vue";
import Dashboard from "./views/Dashboard.vue";
import Domains from "./views/Domains.vue";
import Backups from "./views/Backups.vue";
import Performance from "./views/Performance.vue";
import VPS from "./views/VPS.vue";
import Radar from "./views/Radar.vue";
import Notes from "./views/Notes.vue";
import DNSMonitor from "./views/DNSMonitor.vue";
import Login from "./views/Login.vue";

const isAuthenticated = ref(!!localStorage.getItem('access_token'));
const logout = () => { localStorage.removeItem('access_token'); isAuthenticated.value = false; };
const currentTab = ref('dashboard');
const tabs = [
  { id: 'dashboard',   name: 'Dashboard', icon: '📊' },
  { id: 'domains',     name: 'Domény',    icon: '🌐' },
  { id: 'backups',     name: 'Zálohy',    icon: '📦' },
  { id: 'performance', name: 'Výkon',     icon: '⚡' },
  { id: 'vps',         name: 'VPS',       icon: '🖥️' },
  { id: 'radar',       name: 'Radar',     icon: '🛡️' },
  { id: 'notes',       name: 'Poznámky',  icon: '📝' },
  { id: 'dns-monitor', name: 'DNS Live',  icon: '🔴' },
];
const mainTabs  = tabs.slice(0, 6);
const extraTabs = tabs.slice(6);
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: #080808;
  color: rgba(255,255,250,0.88);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text',
               'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  font-feature-settings: 'kern' 1, 'liga' 1;
  min-height: 100vh;
}

.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #080808;
}

/* ── Navbar ─────────────────────────── */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(12,12,12,0.88);
  backdrop-filter: blur(32px) saturate(170%);
  -webkit-backdrop-filter: blur(32px) saturate(170%);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  box-shadow: 0 1px 0 rgba(255,255,255,0.04), 0 4px 24px rgba(0,0,0,0.2);
}
.navbar::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: min(60%, 400px);
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
  pointer-events: none;
}
.navbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 8px 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}
.navbar-brand { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; margin-top: 5px; }
.brand-icon {
  width: 34px; height: 34px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.12);
}
.brand-name {
  font-size: 0.95rem;
  font-weight: 650;
  color: rgba(255,255,250,0.9);
  letter-spacing: -0.01em;
}

/* Tab area — two rows */
.nav-area {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

/* Tabs */
.nav-tabs {
  display: flex;
  gap: 2px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 3px;
  width: fit-content;
}
.nav-tabs-extra {
  font-size: 0.76rem;
}
.nav-tab {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  border: none;
  border-radius: 9px;
  background: transparent;
  color: rgba(255,255,255,0.4);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  white-space: nowrap;
}
.nav-tab:hover { color: rgba(255,255,255,0.7); background: rgba(255,255,255,0.05); }
.nav-tab.active {
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,250,0.95);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.12), 0 1px 4px rgba(0,0,0,0.3), 0 0 8px rgba(99,102,241,0.08);
}
.tab-icon { font-size: 0.85rem; }
.tab-label { display: none; }
@media (min-width: 640px) { .tab-label { display: inline; } }
@media (max-width: 480px) {
  .navbar-inner { padding: 6px 1rem; gap: 0.75rem; }
  .brand-name { font-size: 0.85rem; }
  .brand-icon { width: 28px; height: 28px; font-size: 0.85rem; }
  .nav-tab { padding: 0.35rem 0.5rem; font-size: 0.72rem; }
  .tab-icon { font-size: 0.75rem; }
  .navbar-right { gap: 0.5rem; }
  .avatar { width: 26px; height: 26px; font-size: 0.6rem; }
  .logout-btn { font-size: 0.7rem; padding: 0.25rem 0.5rem; }
}

/* Right side */
.navbar-right { display: flex; align-items: center; gap: 0.75rem; margin-left: auto; margin-top: 5px; }
.icon-btn {
  background: none; border: none; cursor: pointer;
  font-size: 1rem; opacity: 0.45;
  transition: opacity 0.2s;
  padding: 0.25rem;
}
.icon-btn:hover { opacity: 0.8; }
.avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
  color: rgba(255,255,250,0.7);
  letter-spacing: 0.02em;
}
.logout-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  padding: 0.3rem 0.7rem;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.35);
  cursor: pointer;
  transition: all 0.2s;
}
.logout-btn:hover { color: rgba(255,255,250,0.7); border-color: rgba(255,255,255,0.18); }

/* ── Main ───────────────────────────── */
.app-main {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 5rem;
}
@media (max-width: 480px) {
  .app-main { padding: 1rem 0.75rem 5rem; }
}
@media (min-width: 1440px) {
  .app-main { max-width: 1400px; padding: 2rem 2rem 5rem; }
}

/* ── Mobile nav ─────────────────────── */
.mobile-nav {
  display: flex;
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(20,20,20,0.92);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 18px;
  padding: 0.4rem;
  gap: 2px;
  z-index: 100;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.03);
  max-width: calc(100vw - 2rem);
  overflow-x: auto;
  scrollbar-width: none;
}
.mobile-nav::-webkit-scrollbar { display: none; }
@media (min-width: 768px) { .mobile-nav { display: none; } }
.mobile-tab {
  padding: 0.6rem 0.9rem;
  border: none;
  border-radius: 14px;
  background: transparent;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(255,255,255,0.4);
  flex-shrink: 0;
}
.mobile-tab:hover { color: rgba(255,255,255,0.6); }
.mobile-tab.active {
  background: rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.9);
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
@media (max-width: 480px) {
  .mobile-tab { padding: 0.5rem 0.7rem; font-size: 1rem; }
}

/* ── Fade transition ────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.22s cubic-bezier(0.4,0,0.2,1); }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
