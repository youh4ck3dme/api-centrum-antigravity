<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <h3>🚀 Aktivácia Licencie</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      <div class="modal-body">
        <p class="modal-desc">Zadajte váš licenčný kľúč na odomknutie neobmedzených funkcií (Unlimited Plan).</p>
        <div class="input-group">
          <label>Licenčný kľúč</label>
          <input 
            v-model="licenseKey" 
            type="text" 
            placeholder="XXXX-XXXX-XXXX-XXXX" 
            class="license-input"
            @keyup.enter="handleActivate"
          />
        </div>
        <div v-if="error" class="error-msg">{{ error }}</div>
        <div v-if="success" class="success-msg">{{ success }}</div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="$emit('close')">Zrušiť</button>
        <button 
          class="submit-btn" 
          :disabled="loading || !licenseKey" 
          @click="handleActivate"
        >
          {{ loading ? 'Aktivujem...' : 'Aktivovať' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  loading: Boolean,
  error: String,
  success: String
});

const emit = defineEmits(['close', 'activate']);
const licenseKey = ref('');

function handleActivate() {
  if (licenseKey.value) {
    emit('activate', licenseKey.value);
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 2000;
  background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.modal-card {
  width: 100%; max-width: 400px;
  background: #121212; border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px; overflow: hidden;
  box-shadow: 0 32px 64px rgba(0,0,0,0.5);
}
.modal-header {
  padding: 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.05);
  display: flex; align-items: center; justify-content: space-between;
}
.modal-header h3 { font-size: 1.1rem; color: #f1f5f9; font-weight: 700; }
.close-btn { background: none; border: none; color: #64748b; cursor: pointer; font-size: 1.1rem; }
.close-btn:hover { color: #f1f5f9; }

.modal-body { padding: 1.25rem; }
.modal-desc { font-size: 0.85rem; color: #94a3b8; margin-bottom: 1.25rem; line-height: 1.5; }

.input-group { display: flex; flex-direction: column; gap: 0.5rem; }
.input-group label { font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.license-input {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px; padding: 0.75rem; color: #f1f5f9; font-family: monospace; font-size: 1rem;
  outline: none; transition: border-color 0.2s;
}
.license-input:focus { border-color: #6366f1; }

.error-msg { margin-top: 1rem; color: #f87171; font-size: 0.8rem; background: rgba(239,68,68,0.1); padding: 0.5rem; border-radius: 6px; }
.success-msg { margin-top: 1rem; color: #4ade80; font-size: 0.8rem; background: rgba(34,197,94,0.1); padding: 0.5rem; border-radius: 6px; }

.modal-footer { padding: 1.25rem; display: flex; justify-content: flex-end; gap: 0.75rem; background: rgba(255,255,255,0.02); }
.cancel-btn { background: none; border: none; color: #64748b; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.submit-btn {
  background: #6366f1; color: white; border: none; padding: 0.6rem 1.25rem; border-radius: 10px;
  font-weight: 600; cursor: pointer; font-size: 0.85rem; transition: background 0.2s;
}
.submit-btn:hover:not(:disabled) { background: #4f46e5; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
