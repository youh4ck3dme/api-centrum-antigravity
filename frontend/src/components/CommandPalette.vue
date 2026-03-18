<template>
  <Teleport to="body">
    <div class="cp-backdrop" @click.self="$emit('close')">
      <div class="cp-modal">

        <!-- Search input -->
        <div class="cp-search-row">
          <span class="cp-search-icon">⌘</span>
          <input
            ref="inputRef"
            v-model="query"
            class="cp-input"
            placeholder="Hľadaj príkaz alebo naviguj..."
            autocomplete="off"
            spellcheck="false"
            @keydown.up.prevent="moveUp"
            @keydown.down.prevent="moveDown"
            @keydown.enter.prevent="runSelected"
            @keydown.escape.prevent="$emit('close')"
          />
          <kbd class="cp-esc">Esc</kbd>
        </div>

        <!-- Results -->
        <div class="cp-results" ref="resultsRef">
          <template v-for="group in filteredGroups" :key="group.label">
            <div class="cp-group-label">{{ group.label }}</div>
            <div
              v-for="(cmd, cmdIdx) in group.items"
              :key="cmd.id"
              class="cp-item"
              :class="{ 'is-active': cmd._globalIdx === activeIdx }"
              @click="run(cmd)"
              @mouseenter="activeIdx = cmd._globalIdx"
              :ref="el => { if (cmd._globalIdx === activeIdx) activeEl = el }"
            >
              <span class="cp-item-icon">{{ cmd.icon }}</span>
              <span class="cp-item-label">{{ cmd.label }}</span>
              <span v-if="cmd.hint" class="cp-item-hint">{{ cmd.hint }}</span>
              <kbd v-if="cmd.kbd" class="cp-item-kbd">{{ cmd.kbd }}</kbd>
            </div>
          </template>

          <div v-if="filteredGroups.length === 0" class="cp-empty">
            Žiadne výsledky pre "<strong>{{ query }}</strong>"
          </div>
        </div>

        <!-- Footer -->
        <div class="cp-footer">
          <span><kbd>↑</kbd><kbd>↓</kbd> pohyb</span>
          <span><kbd>↵</kbd> otvoriť</span>
          <span><kbd>Esc</kbd> zatvoriť</span>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  tabs: { type: Array, default: () => [] },
});
const emit = defineEmits(['close', 'navigate', 'logout']);

const query = ref('');
const activeIdx = ref(0);
const activeEl = ref(null);
const inputRef = ref(null);
const resultsRef = ref(null);

// ── Build command list ─────────────────────────
const TAB_ICONS = {
  dashboard: '🏠', domains: '🌐', 'dns-monitor': '📡',
  backups: '💾', performance: '⚡', vps: '🖥',
  radar: '🛡', notes: '📝', terminal: '⌨️', settings: '⚙️',
};

const allGroups = computed(() => [
  {
    label: 'Navigácia',
    items: props.tabs.map(t => ({
      id: `nav:${t.id}`,
      icon: TAB_ICONS[t.id] || '▸',
      label: t.label,
      hint: `/${t.id}`,
      action: () => emit('navigate', t.id),
    })),
  },
  {
    label: 'Rýchle akcie',
    items: [
      {
        id: 'action:copy-ip',
        icon: '📋',
        label: 'Kopírovať IP VPS',
        hint: '194.182.87.6',
        action: () => {
          navigator.clipboard.writeText('194.182.87.6').catch(() => {});
          emit('close');
        },
      },
      {
        id: 'action:logout',
        icon: '🚪',
        label: 'Odhlásiť sa',
        kbd: '',
        action: () => { emit('logout'); emit('close'); },
      },
    ],
  },
]);

// ── Filtered + flattened with global index ──────
const filteredGroups = computed(() => {
  const q = query.value.toLowerCase().trim();
  let globalIdx = 0;
  return allGroups.value
    .map(group => {
      const items = group.items
        .filter(cmd => !q || cmd.label.toLowerCase().includes(q) || (cmd.hint || '').toLowerCase().includes(q))
        .map(cmd => ({ ...cmd, _globalIdx: globalIdx++ }));
      return { label: group.label, items };
    })
    .filter(g => g.items.length > 0);
});

const totalVisible = computed(() => filteredGroups.value.reduce((s, g) => s + g.items.length, 0));

// ── Keyboard navigation ────────────────────────
function moveUp() {
  activeIdx.value = activeIdx.value > 0 ? activeIdx.value - 1 : totalVisible.value - 1;
  scrollActive();
}
function moveDown() {
  activeIdx.value = activeIdx.value < totalVisible.value - 1 ? activeIdx.value + 1 : 0;
  scrollActive();
}
function scrollActive() {
  nextTick(() => {
    if (activeEl.value) activeEl.value.scrollIntoView?.({ block: 'nearest' });
  });
}

function getActiveCmd() {
  for (const g of filteredGroups.value) {
    for (const cmd of g.items) {
      if (cmd._globalIdx === activeIdx.value) return cmd;
    }
  }
  return null;
}
function runSelected() {
  const cmd = getActiveCmd();
  if (cmd) run(cmd);
}
function run(cmd) {
  cmd.action();
}

// Reset selection when query changes
watch(query, () => { activeIdx.value = 0; });

// ── Focus input on mount ───────────────────────
onMounted(() => {
  nextTick(() => inputRef.value?.focus());
});
</script>

<style scoped>
/* ── Backdrop ─────────────────────────────────── */
.cp-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: 3000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 12vh;
}

/* ── Modal card ───────────────────────────────── */
.cp-modal {
  width: min(600px, calc(100vw - 2rem));
  background: rgba(4, 8, 5, 0.97);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--r-xl);
  box-shadow: 0 32px 80px rgba(0,0,0,0.9), 0 0 0 1px rgba(16, 185, 129, 0.05);
  overflow: hidden;
  animation: cpSlide 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes cpSlide {
  from { opacity: 0; transform: translateY(-12px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Search row ───────────────────────────────── */
.cp-search-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(0,255,65,0.07);
}
.cp-search-icon {
  font-size: 1rem;
  color: rgba(0,255,65,0.5);
  flex-shrink: 0;
}
.cp-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: 400;
  caret-color: var(--color-primary);
}
.cp-input::placeholder { color: rgba(255,255,255,0.2); }
.cp-esc {
  font-size: 0.62rem;
  color: rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 5px;
  padding: 2px 6px;
  flex-shrink: 0;
}

/* ── Results ──────────────────────────────────── */
.cp-results {
  max-height: 340px;
  overflow-y: auto;
  padding: 0.4rem 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(0,255,65,0.15) transparent;
}

.cp-group-label {
  font-size: 0.62rem;
  font-weight: 700;
  color: rgba(255,255,255,0.2);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.5rem 1.25rem 0.25rem;
}

.cp-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1.25rem;
  cursor: pointer;
  transition: background 0.1s;
  border-radius: 0;
}
.cp-item:hover,
.cp-item.is-active {
  background: rgba(0,255,65,0.07);
}
.cp-item.is-active {
  background: rgba(0,255,65,0.09);
}
.cp-item.is-active .cp-item-label {
  color: #fff;
}
.cp-item.is-active .cp-item-icon {
  filter: brightness(1.3);
}

.cp-item-icon {
  font-size: 1rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}
.cp-item-label {
  flex: 1;
  font-size: 0.88rem;
  color: rgba(255,255,255,0.75);
  font-weight: 500;
}
.cp-item-hint {
  font-size: 0.7rem;
  color: rgba(0,255,65,0.35);
  font-family: monospace;
}
.cp-item-kbd {
  font-size: 0.62rem;
  color: rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 5px;
  padding: 2px 6px;
}

.cp-empty {
  padding: 2rem 1.25rem;
  text-align: center;
  color: rgba(255,255,255,0.25);
  font-size: 0.85rem;
}
.cp-empty strong { color: rgba(255,255,255,0.4); }

/* ── Footer ───────────────────────────────────── */
.cp-footer {
  display: flex;
  gap: 1.25rem;
  padding: 0.6rem 1.25rem;
  border-top: 1px solid rgba(0,255,65,0.06);
  background: rgba(0,0,0,0.3);
}
.cp-footer span {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.67rem;
  color: rgba(255,255,255,0.2);
}
.cp-footer kbd {
  font-size: 0.6rem;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 4px;
  padding: 1px 5px;
  color: rgba(255,255,255,0.3);
}
</style>
