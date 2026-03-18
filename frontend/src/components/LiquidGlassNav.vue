<template>
  <nav class="liquid-glass-nav" :class="[className, `theme-${theme}`]">
    <div class="nav-container">
      <div 
        v-for="item in items" 
        :key="item.id"
        class="nav-item"
        :class="{ 'is-active': activeId === item.id }"
        @click="$emit('select', item)"
      >
        <div class="nav-item-bg" v-if="activeId === item.id"></div>
        <div class="nav-content">
          <component :is="item.icon" class="nav-icon" :size="20" stroke-width="2.5" />
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  activeId: {
    type: String,
    default: ''
  },
  theme: {
    type: String,
    default: 'dark' // Use 'dark' or 'light' for dark mode fallback
  },
  className: {
    type: String,
    default: ''
  }
});

defineEmits(['select']);
</script>

<style scoped>
/* Core Glassmorphism Base */
.liquid-glass-nav {
  --nav-bg: rgba(4, 4, 4, 0.5);
  --nav-border: rgba(255, 255, 255, 0.06);
  --item-bg-active: rgba(0, 255, 65, 0.07);
  --item-text: rgba(255, 255, 255, 0.4);
  --item-text-active: var(--color-text-primary);
  --item-glow: rgba(0, 255, 65, 0.25);

  position: relative;
  border-radius: 24px;
  background: var(--nav-bg);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid var(--nav-border);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  padding: 0.75rem;
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.liquid-glass-nav.theme-light {
  --nav-bg: rgba(255, 255, 255, 0.6);
  --nav-border: rgba(0, 0, 0, 0.05);
  --item-bg-active: rgba(0, 0, 0, 0.05);
  --item-text: rgba(0, 0, 0, 0.5);
  --item-text-active: rgba(0, 0, 0, 0.9);
  --item-glow: rgba(0,255,65,0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.nav-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Individual Item */
.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 0.85rem 1.1rem;
  border-radius: var(--r-lg);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  user-select: none;
  color: var(--item-text);
  overflow: hidden;
}

.nav-item:hover:not(.is-active) {
  color: var(--item-text-active);
  background: rgba(0, 255, 65, 0.03);
}
.liquid-glass-nav.theme-light .nav-item:hover:not(.is-active) {
  background: rgba(0, 0, 0, 0.03);
}

.nav-item.is-active {
  color: var(--item-text-active);
}

/* Liquid Active Background */
.nav-item-bg {
  position: absolute;
  inset: 0;
  border-radius: var(--r-lg);
  background: var(--item-bg-active);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1), 0 0 20px var(--item-glow);
  z-index: 0;
  animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.nav-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-icon {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.nav-item.is-active .nav-icon {
  transform: scale(1.15);
  color: var(--color-primary);
  filter: drop-shadow(0 0 6px rgba(0, 255, 65, 0.6));
}
.liquid-glass-nav.theme-light .nav-item.is-active .nav-icon {
  color: var(--color-primary-active);
}

.nav-label {
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

/* Horizontal mode for top navbar on desktop if needed */
@media (min-width: 1024px) {
  .liquid-glass-nav.horizontal .nav-container {
    flex-direction: row;
    gap: 0.2rem;
  }
}

/* Narrow desktop: tighter labels */
@media (min-width: 1024px) and (max-width: 1280px) {
  .liquid-glass-nav.horizontal .nav-label { font-size: 0.82rem; }
  .liquid-glass-nav.horizontal .nav-item  { padding: 0.65rem 0.8rem; }
}
</style>
