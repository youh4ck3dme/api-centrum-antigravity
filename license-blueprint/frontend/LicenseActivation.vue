<template>
  <div class="license-activation-card">
    <h3>License Management</h3>
    
    <div v-if="currentPlan === 'license'" class="status-badge active">
      <span class="icon">💎</span>
      <div>
        <strong>Unlimited Plan Active</strong>
        <p>Your business has no restrictions.</p>
      </div>
    </div>

    <div v-else class="activation-form">
      <p>Enter your 32-character license key to unlock the unlimited plan.</p>
      <div class="input-group">
        <input 
          v-model="licenseKey" 
          type="text" 
          placeholder="XXXX-XXXX-XXXX-XXXX-XXXX"
          :disabled="loading"
        />
        <button @click="handleActivate" :disabled="loading || !licenseKey">
          {{ loading ? 'Activating...' : 'Activate' }}
        </button>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { getFunctions, httpsCallable } from 'firebase/functions';

const props = defineProps({
  businessId: {
    type: String,
    required: true
  },
  businessData: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['activated']);

const licenseKey = ref('');
const loading = ref(false);
const error = ref(null);

const currentPlan = computed(() => props.businessData?.plan || 'free');

const handleActivate = async () => {
  if (!licenseKey.value) return;
  
  loading.value = true;
  error.value = null;

  try {
    const functions = getFunctions();
    const activateLicenseFn = httpsCallable(functions, 'activateLicense');
    
    const result = await activateLicenseFn({
      key: licenseKey.value,
      business_id: props.businessId
    });

    if (result.data.plan === 'license') {
      emit('activated', result.data);
      licenseKey.value = '';
    }
  } catch (err) {
    console.error('Activation failed:', err);
    error.value = err.message || 'Failed to activate license. Please check your key.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.license-activation-card {
  padding: 1.5rem;
  border-radius: 12px;
  background: v-bind("currentPlan === 'license' ? '#f0fdf4' : '#ffffff'");
  border: 1px solid v-bind("currentPlan === 'license' ? '#bbf7d0' : '#e5e7eb'");
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #166534;
}

.icon {
  font-size: 2rem;
}

.input-group {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-family: monospace;
}

button {
  padding: 0.75rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-msg {
  color: #dc2626;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}
</style>
