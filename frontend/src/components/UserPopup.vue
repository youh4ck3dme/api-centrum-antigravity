<template>
  <Teleport to="body">
    <!-- Click-outside backdrop -->
    <div class="popup-backdrop" @click.self="$emit('close')"></div>

    <div class="popup-card" :class="{ 'is-mobile': isMobile }">

      <!-- ── Header ─────────────────── -->
      <div class="popup-header">
        <div class="popup-avatar" @click="cycleAvatar">{{ currentAvatar }}</div>
        <div class="popup-identity">
          <div class="popup-name">{{ email || 'Admin' }}</div>
          <div class="popup-role">Administrator</div>
        </div>
        <button class="popup-close" @click="$emit('close')">✕</button>
      </div>

      <!-- ── System Pulse ───────────── -->
      <div class="popup-section">
        <div class="section-header">
          <span class="pulse-dot"></span>
          <span class="section-title">System Pulse</span>
          <span class="containers-badge">
            {{ stats ? stats.containers_running : '—' }} / {{ stats ? stats.containers_total : '—' }} containers
          </span>
        </div>
        <div v-if="statsLoading" class="status-row dim">Connecting to VPS...</div>
        <div v-else-if="statsError" class="status-row error">VPS nedostupný</div>
        <div v-else-if="stats" class="metrics">
          <div class="metric-row">
            <span class="metric-label">CPU</span>
            <div class="bar-track">
              <div class="bar-fill" :class="barCls(stats.cpu_percent)" :style="{ width: stats.cpu_percent + '%' }"></div>
            </div>
            <span class="metric-val">{{ stats.cpu_percent }}%</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">RAM</span>
            <div class="bar-track">
              <div class="bar-fill" :class="barCls(ramPct)" :style="{ width: ramPct + '%' }"></div>
            </div>
            <span class="metric-val">{{ stats.ram_used_mb }}M / {{ stats.ram_total_mb }}M</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Disk</span>
            <div class="bar-track">
              <div class="bar-fill" :class="barCls(diskPct)" :style="{ width: diskPct + '%' }"></div>
            </div>
            <span class="metric-val">{{ stats.disk_used_gb }}G / {{ stats.disk_total_gb }}G</span>
          </div>
        </div>
      </div>

      <!-- ── Quick Actions ──────────── -->
      <div class="popup-section">
        <div class="section-header">
          <span class="section-title">Quick Actions</span>
        </div>
        <div class="actions-grid">
          <button class="action-btn" @click="copyIP">
            <span class="action-icon">📋</span>Copy IP
          </button>
          <button class="action-btn" @click="refreshStats">
            <span class="action-icon">↺</span>Refresh
          </button>
          <button class="action-btn" @click="navTo('vps')">
            <span class="action-icon">🖥</span>VPS Monitor
          </button>
          <button class="action-btn accent" @click="navTo('dns-monitor')">
            <span class="action-icon">🛡</span>DNS Audit
          </button>
        </div>
        <transition name="fade-toast">
          <div v-if="toast" class="popup-toast">{{ toast }}</div>
        </transition>
      </div>

      <!-- ── Activity Feed ──────────── -->
      <div class="popup-section">
        <div class="section-header">
          <span class="section-title">Posledná aktivita</span>
        </div>
        <div v-if="activitiesLoading" class="status-row dim">Načítavam...</div>
        <div v-else-if="activities.length === 0" class="status-row dim">Žiadna aktivita</div>
        <div v-else class="activity-list">
          <div v-for="a in activities" :key="a.timestamp" class="activity-item">
            <span class="activity-icon">{{ actionIcon(a.action) }}</span>
            <div class="activity-body">
              <span class="activity-text">{{ a.detail || a.action }}</span>
              <span class="activity-time">{{ timeAgo(a.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  email: { type: String, default: '' },
  userInitials: { type: String, default: '??' },
});
const emit = defineEmits(['close', 'navigate']);

// ── Avatar cycle ─────────────────────────────
const AVATARS = ['🦊', '🐺', '🤖', '🦅', '⚡', '🔥', '🎯', '🦁', '🐉', '🌙', '🧬', '🔮'];
const storedAvatar = localStorage.getItem('user-avatar');
const avatarIndex = ref(storedAvatar ? AVATARS.indexOf(storedAvatar) : -1);
const currentAvatar = computed(() =>
  avatarIndex.value >= 0 ? AVATARS[avatarIndex.value] : props.userInitials
);
function cycleAvatar() {
  avatarIndex.value = (avatarIndex.value + 1) % AVATARS.length;
  localStorage.setItem('user-avatar', AVATARS[avatarIndex.value]);
}

// ── Mobile detection ─────────────────────────
const isMobile = ref(window.innerWidth < 1024);
const onResize = () => { isMobile.value = window.innerWidth < 1024; };

// ── Stats ────────────────────────────────────
const stats = ref(null);
const statsLoading = ref(true);
const statsError = ref(false);
let refreshTimer = null;

const ramPct = computed(() =>
  stats.value ? Math.round(stats.value.ram_used_mb / stats.value.ram_total_mb * 100) : 0
);
const diskPct = computed(() =>
  stats.value ? Math.round(stats.value.disk_used_gb / stats.value.disk_total_gb * 100) : 0
);
function barCls(pct) {
  if (pct >= 85) return 'danger';
  if (pct >= 60) return 'warn';
  return 'ok';
}

async function fetchStats() {
  statsLoading.value = true;
  statsError.value = false;
  try {
    const res = await fetch('/api/vps/stats', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    if (!res.ok) throw new Error();
    stats.value = await res.json();
  } catch {
    statsError.value = true;
  } finally {
    statsLoading.value = false;
  }
}

function refreshStats() {
  fetchStats();
  showToast('Refreshing...');
}

// ── Activities ───────────────────────────────
const activities = ref([]);
const activitiesLoading = ref(true);

async function fetchActivities() {
  try {
    const res = await fetch('/api/dashboard/activities?limit=5', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    if (res.ok) {
      const data = await res.json();
      activities.value = data.activities || [];
    }
  } catch {}
  activitiesLoading.value = false;
}

function actionIcon(action) {
  if (!action) return '⚡';
  const a = action.toLowerCase();
  if (a.includes('login')) return '🔑';
  if (a.includes('domain')) return '🌐';
  if (a.includes('dns')) return '🛡';
  if (a.includes('backup')) return '💾';
  if (a.includes('ssl')) return '🔒';
  if (a.includes('create')) return '✨';
  if (a.includes('delete')) return '🗑';
  if (a.includes('update')) return '✏️';
  return '⚡';
}

function timeAgo(iso) {
  if (!iso) return '';
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

// ── Quick actions ─────────────────────────────
const toast = ref('');
let toastTimer = null;

function showToast(msg) {
  toast.value = msg;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.value = ''; }, 2000);
}

function copyIP() {
  navigator.clipboard.writeText('194.182.87.6').then(() => showToast('IP skopírovaná!')).catch(() => showToast('194.182.87.6'));
}

function navTo(tab) {
  emit('navigate', tab);
  emit('close');
}

// ── Keyboard close ─────────────────────────────
function onKeydown(e) {
  if (e.key === 'Escape') emit('close');
}

onMounted(() => {
  fetchStats();
  fetchActivities();
  refreshTimer = setInterval(fetchStats, 10000);
  window.addEventListener('resize', onResize);
  window.addEventListener('keydown', onKeydown);
});

onUnmounted(() => {
  clearInterval(refreshTimer);
  clearTimeout(toastTimer);
  window.removeEventListener('resize', onResize);
  window.removeEventListener('keydown', onKeydown);
});
</script>

<style scoped>
/* ── Backdrop ─────────────────────────────────── */
.popup-backdrop {
  position: fixed;
  inset: 0;
  z-index: 2000;
}

/* ── Card ─────────────────────────────────────── */
.popup-card {
  position: fixed;
  top: 84px;
  right: 1.5rem;
  width: 300px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  z-index: 2001;
  background: rgba(4, 8, 5, 0.96);
  backdrop-filter: blur(32px) saturate(180%);
  -webkit-backdrop-filter: blur(32px) saturate(180%);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--r-xl);
  box-shadow: 0 24px 64px rgba(0,0,0,0.8), 0 0 0 1px rgba(16, 185, 129, 0.05);
  animation: slideDown 0.18s cubic-bezier(0.16, 1, 0.3, 1);
  scrollbar-width: thin;
  scrollbar-color: rgba(0,255,65,0.15) transparent;
}

.popup-card.is-mobile {
  top: 68px;
  right: 0.5rem;
  left: 0.5rem;
  width: auto;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Header ───────────────────────────────────── */
.popup-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid rgba(0,255,65,0.06);
}

.popup-avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  background: rgba(0,0,0,0.5);
  border: 1px solid rgba(0,255,65,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 800;
  color: var(--color-primary);
  box-shadow: 0 0 12px rgba(0,255,65,0.1);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  user-select: none;
}
.popup-avatar:hover {
  border-color: rgba(0,255,65,0.5);
  box-shadow: 0 0 20px rgba(0,255,65,0.2);
}

.popup-identity { flex: 1; min-width: 0; }
.popup-name { font-size: 0.82rem; font-weight: 600; color: var(--color-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.popup-role { font-size: 0.68rem; color: rgba(0,255,65,0.4); margin-top: 1px; }

.popup-close {
  background: none; border: none; color: rgba(255,255,255,0.3);
  font-size: 0.75rem; cursor: pointer; padding: 4px; border-radius: 6px;
  transition: color 0.2s, background 0.2s;
  line-height: 1;
}
.popup-close:hover { color: #fff; background: rgba(255,255,255,0.06); }

/* ── Section ──────────────────────────────────── */
.popup-section {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid rgba(0,255,65,0.05);
}
.popup-section:last-child { border-bottom: none; }

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}
.section-title {
  font-size: 0.68rem;
  font-weight: 700;
  color: rgba(255,255,255,0.3);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  flex: 1;
}

/* ── Pulse dot ────────────────────────────────── */
.pulse-dot {
  width: 6px; height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(0,255,65,0.8);
  animation: blink 1.8s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.3; } }

.containers-badge {
  font-size: 0.62rem;
  color: rgba(0,255,65,0.5);
  background: rgba(0,255,65,0.06);
  border: 1px solid rgba(0,255,65,0.1);
  border-radius: 6px;
  padding: 1px 6px;
}

/* ── Metrics ──────────────────────────────────── */
.metrics { display: flex; flex-direction: column; gap: 0.45rem; }

.metric-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.metric-label {
  font-size: 0.65rem;
  color: rgba(255,255,255,0.3);
  width: 28px;
  flex-shrink: 0;
}
.bar-track {
  flex: 1;
  height: 5px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
}
.bar-fill.ok     { background: linear-gradient(90deg, var(--color-primary), var(--color-primary-hover)); box-shadow: 0 0 6px rgba(0,255,65,0.4); }
.bar-fill.warn   { background: linear-gradient(90deg, #ffbb00, #ff8800); box-shadow: 0 0 6px rgba(255,187,0,0.4); }
.bar-fill.danger { background: linear-gradient(90deg, var(--color-danger), #cc0000); box-shadow: 0 0 6px rgba(255,68,68,0.4); }

.metric-val {
  font-size: 0.62rem;
  color: rgba(255,255,255,0.4);
  min-width: 70px;
  text-align: right;
}

/* ── Status rows ──────────────────────────────── */
.status-row { font-size: 0.72rem; padding: 0.25rem 0; }
.status-row.dim   { color: rgba(255,255,255,0.25); }
.status-row.error { color: rgba(255,100,100,0.7); }

/* ── Quick Actions ────────────────────────────── */
.actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.4rem;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.7rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: var(--r-sm);
  color: rgba(255,255,255,0.55);
  font-size: 0.72rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s;
  text-align: left;
}
.action-btn:hover {
  background: rgba(0,255,65,0.05);
  border-color: rgba(0,255,65,0.15);
  color: #fff;
}
.action-btn.accent {
  border-color: rgba(0,255,65,0.15);
  color: rgba(0,255,65,0.7);
}
.action-btn.accent:hover {
  background: rgba(0,255,65,0.08);
  color: var(--color-primary);
}
.action-icon { font-size: 0.8rem; }

/* ── Toast ────────────────────────────────────── */
.popup-toast {
  margin-top: 0.5rem;
  padding: 0.35rem 0.7rem;
  background: rgba(0,255,65,0.08);
  border: 1px solid rgba(0,255,65,0.18);
  border-radius: 8px;
  color: var(--color-primary);
  font-size: 0.7rem;
  text-align: center;
}
.fade-toast-enter-active, .fade-toast-leave-active { transition: opacity 0.2s; }
.fade-toast-enter-from, .fade-toast-leave-to { opacity: 0; }

/* ── Activity Feed ────────────────────────────── */
.activity-list { display: flex; flex-direction: column; gap: 0.45rem; }
.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
.activity-icon { font-size: 0.8rem; line-height: 1.4; flex-shrink: 0; }
.activity-body { flex: 1; min-width: 0; }
.activity-text {
  display: block;
  font-size: 0.72rem;
  color: rgba(255,255,255,0.55);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.activity-time {
  display: block;
  font-size: 0.62rem;
  color: rgba(0,255,65,0.35);
  margin-top: 1px;
}
</style>
