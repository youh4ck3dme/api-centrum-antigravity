<template>
  <div class="settings-root">

    <div class="page-header">
      <div>
        <h2 class="page-title">Nastavenia</h2>
        <p class="page-sub">Prispôsob vzhľad aplikácie</p>
      </div>
    </div>

    <!-- Font Picker -->
    <div class="glass-card section-card">
      <h3 class="section-title">
        <span class="section-icon">Aa</span>
        Písmo aplikácie
        <span class="section-hint">Zmena sa prejaví okamžite v celej appke</span>
      </h3>

      <div class="font-grid">
        <button
          v-for="font in FONTS"
          :key="font.key"
          class="font-card"
          :class="{ selected: currentFont === font.key }"
          @click="selectFont(font.key)"
        >
          <div class="font-preview" :style="{ fontFamily: font.family }">
            Aa 0123
          </div>
          <div class="font-info">
            <span class="font-name">{{ font.label }}</span>
            <span class="font-badge" :class="font.type">{{ font.type }}</span>
          </div>
          <span v-if="currentFont === font.key" class="font-check">✓</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';

const FONTS = [
  { key: 'system',          label: 'System Default',   type: 'sans',  family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" },
  { key: 'jetbrains-mono',  label: 'JetBrains Mono',   type: 'mono',  family: "'JetBrains Mono', monospace" },
  { key: 'fira-code',       label: 'Fira Code',        type: 'mono',  family: "'Fira Code', monospace" },
  { key: 'source-code-pro', label: 'Source Code Pro',  type: 'mono',  family: "'Source Code Pro', monospace" },
  { key: 'share-tech-mono', label: 'Share Tech Mono',  type: 'mono',  family: "'Share Tech Mono', monospace" },
  { key: 'vt323',           label: 'VT323',            type: 'retro', family: "'VT323', monospace" },
  { key: 'orbitron',        label: 'Orbitron',         type: 'sci-fi',family: "'Orbitron', sans-serif" },
  { key: 'oxanium',         label: 'Oxanium',          type: 'cyber', family: "'Oxanium', sans-serif" },
  { key: 'ibm-plex-mono',   label: 'IBM Plex Mono',    type: 'mono',  family: "'IBM Plex Mono', monospace" },
  { key: 'space-mono',      label: 'Space Mono',       type: 'mono',  family: "'Space Mono', monospace" },
  { key: 'inconsolata',     label: 'Inconsolata',      type: 'mono',  family: "'Inconsolata', monospace" },
];

const GOOGLE_KEYS = {
  'jetbrains-mono':  'JetBrains+Mono',
  'fira-code':       'Fira+Code',
  'source-code-pro': 'Source+Code+Pro',
  'share-tech-mono': 'Share+Tech+Mono',
  'vt323':           'VT323',
  'orbitron':        'Orbitron',
  'oxanium':         'Oxanium',
  'ibm-plex-mono':   'IBM+Plex+Mono',
  'space-mono':      'Space+Mono',
  'inconsolata':     'Inconsolata',
};

const currentFont = ref(localStorage.getItem('app-font') || 'system');

function selectFont(key) {
  currentFont.value = key;
  localStorage.setItem('app-font', key);
  // Load Google Font if not yet loaded
  const gk = GOOGLE_KEYS[key];
  if (gk && !document.getElementById(`gf-${key}`)) {
    const link = document.createElement('link');
    link.id = `gf-${key}`; link.rel = 'stylesheet';
    link.href = `https://fonts.googleapis.com/css2?family=${gk}:wght@400;500;700&display=swap`;
    document.head.appendChild(link);
  }
  // Notify App.vue via custom event
  window.dispatchEvent(new CustomEvent('font-change', { detail: key }));
}
</script>

<style scoped>
.settings-root {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}



.section-card { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.section-title {
  display: flex; align-items: center; gap: 0.6rem;
  font-size: 0.95rem; font-weight: 700; color: var(--color-text-primary); margin: 0;
}
.section-icon {
  width: 28px; height: 28px;
  background: rgba(0,255,65,0.15); border: 1px solid rgba(0,255,65,0.3);
  border-radius: 7px; display: flex; align-items: center; justify-content: center;
  font-size: var(--fs-sm); font-weight: 800; color: var(--color-accent);
}
.section-hint {
  font-size: 0.72rem; font-weight: 400; color: var(--color-text-secondary); margin-left: auto;
}

/* Font grid */
.font-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.font-card {
  position: relative;
  padding: 1rem 0.9rem 0.75rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
  display: flex; flex-direction: column; gap: 0.5rem;
}
.font-card:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(0,255,65,0.3);
  transform: translateY(-1px);
}
.font-card.selected {
  background: rgba(0,255,65,0.08);
  border-color: rgba(0,255,65,0.55);
  box-shadow: 0 0 12px rgba(0,255,65,0.15);
}

.font-preview {
  font-size: 1.5rem;
  color: var(--color-text-primary);
  line-height: 1;
  letter-spacing: -0.01em;
}

.font-info {
  display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;
}
.font-name {
  font-size: 0.72rem; font-weight: 600; color: var(--color-text-secondary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 100px;
}

.font-badge {
  font-size: var(--fs-xs); font-weight: 700; text-transform: uppercase;
  padding: 0.1rem 0.35rem; border-radius: var(--r-xs); letter-spacing: 0.04em;
}
.font-badge.mono   { background: rgba(34,211,238,0.12); color: #22d3ee; }
.font-badge.sans   { background: rgba(74,222,128,0.12); color: var(--color-secondary); }
.font-badge.retro  { background: rgba(250,204,21,0.12); color: var(--color-warning); }
.font-badge.sci-fi { background: rgba(192,132,252,0.12); color: var(--color-purple); }
.font-badge.cyber  { background: rgba(251,146,60,0.12); color: #fb923c; }

.font-check {
  position: absolute; top: 0.5rem; right: 0.6rem;
  font-size: var(--fs-sm); color: var(--color-secondary); font-weight: 800;
}
</style>
