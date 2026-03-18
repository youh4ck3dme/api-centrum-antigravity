<template>
  <div class="bell-wrap" ref="wrapRef">

    <!-- Bell button -->
    <button class="bell-btn" @click.stop="toggle" :class="{ active: open }" :title="`${unreadCount} alertov`">
      🔔
      <span v-if="unreadCount > 0" class="bell-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
    </button>

    <!-- Dropdown -->
    <Teleport to="body">
      <div v-if="open" class="nb-backdrop" @click.self="open = false"></div>
      <Transition name="nb-slide">
        <div v-if="open" class="nb-dropdown" :style="dropdownPos">

          <div class="nb-header">
            <span class="nb-title">Upozornenia</span>
            <button v-if="unreadCount > 0" class="nb-dismiss-all" @click="dismissAll">Všetky prečítané</button>
          </div>

          <div v-if="alerts.length === 0" class="nb-empty">
            <span>✅</span>
            <span>Žiadne upozornenia</span>
          </div>

          <div v-else class="nb-list">
            <div
              v-for="alert in alerts"
              :key="alert.id"
              class="nb-item"
              :class="{ 'is-unread': !isDismissed(alert.id), [`sev-${alert.severity}`]: true }"
            >
              <span class="nb-item-icon">{{ alert.icon }}</span>
              <div class="nb-item-body" @click="handleAlertClick(alert)">
                <p class="nb-item-text">{{ alert.text }}</p>
                <p class="nb-item-time">{{ alert.time }}</p>
              </div>
              <button class="nb-item-dismiss" @click.stop="dismiss(alert.id)" title="Zatvoriť">✕</button>
            </div>
          </div>

        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const emit = defineEmits(['navigate']);

// ── State ─────────────────────────────────────
const open = ref(false);
const wrapRef = ref(null);
const alerts = ref([]);
const dismissed = ref(new Set(JSON.parse(localStorage.getItem('dismissed-alerts') || '[]')));
let pollTimer = null;

// ── Dismissed logic ─────────────────────────────
function isDismissed(id) { return dismissed.value.has(id); }
function dismiss(id) {
  dismissed.value.add(id);
  localStorage.setItem('dismissed-alerts', JSON.stringify([...dismissed.value]));
}
function dismissAll() {
  alerts.value.forEach(a => dismiss(a.id));
}

// ── Unread count ────────────────────────────────
const unreadCount = computed(() => alerts.value.filter(a => !isDismissed(a.id)).length);

// ── Polling ─────────────────────────────────────
async function fetchAlerts() {
  try {
    const res = await fetch('/api/dashboard/stats', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    if (!res.ok) return;
    const data = await res.json();
    const h = data.system_health;
    const u = data.user_stats;
    const now = new Date().toLocaleTimeString('sk-SK', { hour: '2-digit', minute: '2-digit' });
    const newAlerts = [];

    if (h.database === 'offline') {
      newAlerts.push({ id: 'db-offline', icon: '🔴', severity: 'critical', text: 'Databáza nedostupná', time: now, tab: 'vps' });
    }
    if (h.websupport_api === 'offline') {
      newAlerts.push({ id: 'api-offline', icon: '🟠', severity: 'warn', text: 'Websupport API nedostupné', time: now, tab: 'domains' });
    }
    const exp = u.expiring_soon ?? 0;
    if (exp > 0) {
      newAlerts.push({ id: `expiring-${exp}`, icon: '⚠️', severity: 'warn', text: `${exp} ${exp === 1 ? 'doména expiruje' : 'domén expiruje'} do 30 dní`, time: now, tab: 'domains' });
    }

    // Keep dismissed IDs that are no longer relevant removed from storage
    alerts.value = newAlerts;
  } catch {}
}

// ── Click handler ───────────────────────────────
function handleAlertClick(alert) {
  dismiss(alert.id);
  if (alert.tab) { emit('navigate', alert.tab); }
  open.value = false;
}

// ── Dropdown position ────────────────────────────
const dropdownPos = computed(() => {
  if (!wrapRef.value) return 'top: 84px; right: 1.5rem;';
  const rect = wrapRef.value.getBoundingClientRect();
  return `top: ${rect.bottom + 8}px; right: ${window.innerWidth - rect.right}px;`;
});

// ── Toggle ──────────────────────────────────────
function toggle() { open.value = !open.value; }

// ── Click outside ────────────────────────────────
function onDocClick(e) {
  if (open.value && wrapRef.value && !wrapRef.value.contains(e.target)) {
    open.value = false;
  }
}

onMounted(() => {
  fetchAlerts();
  pollTimer = setInterval(fetchAlerts, 5 * 60 * 1000); // every 5 minutes
  document.addEventListener('click', onDocClick);
});
onUnmounted(() => {
  clearInterval(pollTimer);
  document.removeEventListener('click', onDocClick);
});
</script>

<style scoped>
/* ── Bell button ───────────────────────────────── */
.bell-wrap { position: relative; }

.bell-btn {
  position: relative;
  width: 32px; height: 32px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 50%;
  color: rgba(255,255,255,0.4);
  font-size: 0.85rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.bell-btn:hover,
.bell-btn.active {
  background: rgba(0,255,65,0.07);
  border-color: rgba(0,255,65,0.2);
  color: var(--color-primary);
  box-shadow: 0 0 12px rgba(0,255,65,0.1);
}

.bell-badge {
  position: absolute;
  top: -4px; right: -4px;
  min-width: 16px; height: 16px;
  background: var(--color-danger);
  border: 2px solid #000;
  border-radius: 99px;
  font-size: 0.55rem;
  font-weight: 800;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  padding: 0 2px;
  animation: pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes pop { from { transform: scale(0); } to { transform: scale(1); } }

/* ── Backdrop ─────────────────────────────────── */
.nb-backdrop {
  position: fixed; inset: 0; z-index: 2998;
}

/* ── Dropdown ─────────────────────────────────── */
.nb-dropdown {
  position: fixed;
  width: 280px;
  z-index: 2999;
  background: rgba(4, 8, 5, 0.97);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(0,255,65,0.12);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.8), inset 0 1px 0 rgba(0,255,65,0.06);
  overflow: hidden;
}

.nb-slide-enter-active { animation: nbSlide 0.16s cubic-bezier(0.16, 1, 0.3, 1); }
.nb-slide-leave-active { animation: nbSlide 0.12s reverse; }
@keyframes nbSlide {
  from { opacity: 0; transform: translateY(-6px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Header ───────────────────────────────────── */
.nb-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0,255,65,0.06);
}
.nb-title { font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.08em; }
.nb-dismiss-all {
  background: none; border: none;
  font-size: 0.65rem; color: rgba(0,255,65,0.4);
  cursor: pointer; transition: color 0.2s;
}
.nb-dismiss-all:hover { color: var(--color-primary); }

/* ── Empty state ──────────────────────────────── */
.nb-empty {
  display: flex; flex-direction: column; align-items: center; gap: 0.4rem;
  padding: 1.5rem; color: rgba(255,255,255,0.25); font-size: 0.8rem;
}

/* ── List ─────────────────────────────────────── */
.nb-list { display: flex; flex-direction: column; }

.nb-item {
  display: flex; align-items: flex-start; gap: 0.6rem;
  padding: 0.7rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  border-left: 3px solid transparent;
  transition: background 0.15s;
}
.nb-item:last-child { border-bottom: none; }
.nb-item.is-unread { background: rgba(0,255,65,0.03); }
.nb-item.sev-critical { border-left-color: rgba(239,68,68,0.5); }
.nb-item.sev-warn     { border-left-color: rgba(251,191,36,0.5); }
.nb-item:hover { background: rgba(255,255,255,0.03); }

.nb-item-icon { font-size: 0.95rem; flex-shrink: 0; line-height: 1.5; }

.nb-item-body { flex: 1; min-width: 0; cursor: pointer; }
.nb-item-text { font-size: 0.78rem; color: rgba(255,255,250,0.7); line-height: 1.4; }
.nb-item:hover .nb-item-text { color: #fff; }
.nb-item-time { font-size: 0.65rem; color: rgba(255,255,255,0.25); margin-top: 2px; }

.nb-item-dismiss {
  background: none; border: none;
  color: rgba(255,255,255,0.2); font-size: 0.6rem;
  cursor: pointer; padding: 2px 4px; border-radius: 4px;
  transition: all 0.15s; flex-shrink: 0; line-height: 1.5;
}
.nb-item-dismiss:hover { color: var(--color-danger); background: rgba(248,113,113,0.08); }
</style>
