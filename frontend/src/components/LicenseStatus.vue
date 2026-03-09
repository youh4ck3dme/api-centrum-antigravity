<template>
  <div class="license-status" :class="{ 'is-unlimited': isUnlimited }">
    <div class="status-indicator">
      <span class="status-dot"></span>
      <span class="status-text">{{ isUnlimited ? 'PRO UNLIMITED' : 'FREE PLAN' }}</span>
    </div>
    <button v-if="!isUnlimited" @click="$emit('open-modal')" class="activate-btn">
      Aktivovať Pro
    </button>
  </div>
</template>

<script setup>
defineProps({
  isUnlimited: Boolean
});
defineEmits(['open-modal']);
</script>

<style scoped>
.license-status {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: auto;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.4);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #64748b;
}

.is-unlimited .status-indicator {
  color: #818cf8;
}

.is-unlimited .status-dot {
  background: #818cf8;
  box-shadow: 0 0 8px #6366f1;
}

.activate-btn {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border: none;
  border-radius: 8px;
  color: white;
  padding: 0.4rem;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.activate-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

/* Sidebar context adjustments */
@media (max-width: 1023px) {
  .license-status {
    margin: 1rem;
  }
}
</style>
