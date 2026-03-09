<template>
  <div class="license-status" :class="{ 'is-unlimited': isUnlimited }">
    <div class="label">{{ isUnlimited ? 'Plán' : 'Tvoj paušál' }}</div>
    
    <div class="badge">
      <div class="badge-content">
        <span class="badge-icon">{{ isUnlimited ? '👑' : '🛡️' }}</span>
        <span class="badge-text">{{ isUnlimited ? 'PRO UNLIMITED' : 'FREE VERSION' }}</span>
      </div>
      <div v-if="isUnlimited" class="pulse-ring"></div>
    </div>

    <button v-if="!isUnlimited" @click="$emit('open-modal')" class="activate-btn">
      <span>Upgrade na PRO</span>
      <span class="btn-arrow">→</span>
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
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin: 1rem 0;
  transition: all 0.3s ease;
}

.label {
  font-size: 0.65rem;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.2);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ── Badge ─────────────────────── */
.badge {
  position: relative;
  padding: 0.6rem 1rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.badge-content {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  z-index: 2;
}

.badge-icon { font-size: 0.9rem; }
.badge-text {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: rgba(255, 255, 255, 0.6);
}

.is-unlimited .license-status {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(168, 85, 247, 0.05));
  border-color: rgba(99, 102, 241, 0.15);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.is-unlimited .badge {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
  border-color: rgba(99, 102, 241, 0.25);
}

.is-unlimited .badge-text {
  color: #a5b4fc;
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
}

/* ── Pulse Animation ───────────── */
.pulse-ring {
  position: absolute;
  width: 100%; height: 100%;
  border: 1px solid rgba(99, 102, 241, 0.4);
  border-radius: 12px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  100% { transform: scale(1.15); opacity: 0; }
}

/* ── Button ────────────────────── */
.activate-btn {
  margin-top: 0.25rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  border-radius: 10px;
  color: white;
  padding: 0.6rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.activate-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.btn-arrow { opacity: 0.7; font-size: 0.9rem; }

/* Sidebar context */
@media (max-width: 1023px) {
  .license-status { margin: 1rem; }
}
</style>
