<template>
  <div class="sentinel-audit">
    <div class="header-section">
      <div class="header-info">
        <h3>🛡️ AI DNS Sentinel</h3>
        <p>Proaktívny strážca bezpečnosti tvojej domény</p>
      </div>
      <div>
        <button v-if="!loading && !auditData" @click="runAudit" class="btn-primary">
          Spustiť analýzu
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="empty-state">
      <div class="spinner"></div>
      <span>Analyzujem DNS záznamy...</span>
    </div>

    <!-- Audit Results -->
    <div v-if="auditData && !loading" class="audit-results">
      <div class="score-card">
        <ScoreGauge :score="auditData.security_score" />
        <div class="score-details">
          <h4 :class="`text-${auditData.color}-400`">{{ auditData.status }}</h4>
          <p>{{ auditData.message }}</p>
        </div>
      </div>

      <div class="security-features">
        <div class="feature-item" :class="{ 'active': auditData.details.spf_active }">
          <span class="icon">{{ auditData.details.spf_active ? '✅' : '❌' }}</span>
          <div class="info">
            <h5>SPF Záznam</h5>
            <p>Zabraňuje falšovaniu odosielateľa</p>
          </div>
        </div>
        <div class="feature-item" :class="{ 'active': auditData.details.dmarc_active }">
          <span class="icon">{{ auditData.details.dmarc_active ? '✅' : '❌' }}</span>
          <div class="info">
            <h5>DMARC Politika</h5>
            <p>Reporty a striktná kontrola e-mailov</p>
          </div>
        </div>
        <div class="feature-item" :class="{ 'active': auditData.details.dkim_active }">
          <span class="icon">{{ auditData.details.dkim_active ? '✅' : '❌' }}</span>
          <div class="info">
            <h5>DKIM Kľúč</h5>
            <p>Kryptografický podpis e-mailov</p>
          </div>
        </div>
      </div>

      <!-- Actionable Fixes -->
      <div v-if="auditData.fixes_available && auditData.fixes_available.length > 0" class="fixes-section">
        <div class="fixes-header">
          <h4>Vylepšenia bezpečnosti</h4>
          <span class="badge">{{ auditData.fixes_available.length }} nájdené</span>
        </div>
        <div class="fix-list">
          <div v-for="(fix, idx) in auditData.fixes_available" :key="idx" class="fix-item">
            <div class="fix-code">
              <span class="type">{{ fix.type }}</span>
              <code>{{ fix.name || '@' }} -> {{ fix.content }}</code>
            </div>
          </div>
        </div>
        <button @click="applyFixes" class="btn-autofix" :disabled="fixing">
          <span class="magic-icon">✨</span>
          {{ fixing ? 'Aplikujem úpravy...' : 'Auto-Fix (1 Clik)' }}
        </button>
      </div>
      <div v-else class="perfect-state">
        <span class="magic-icon">🎉</span>
        <p>Všetko je perfektne nastavené. Žiadne kritické zraniteľnosti nenájdené.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import ScoreGauge from '../ui/ScoreGauge.vue';
import api from '../../api/api';

const props = defineProps({
  domainName: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['fixed']);

const loading = ref(false);
const fixing = ref(false);
const auditData = ref(null);

const runAudit = async () => {
  if (!props.domainName) return;
  loading.value = true;
  auditData.value = null;
  
  try {
    const res = await api.get(`/domains/${props.domainName}/audit`);
    auditData.value = res.data;
  } catch (err) {
    console.error("Audit failed", err);
  } finally {
    loading.value = false;
  }
};

const applyFixes = async () => {
  if (!auditData.value || !auditData.value.fixes_available.length) return;
  fixing.value = true;
  try {
    const payload = auditData.value.fixes_available;
    await api.post(`/domains/${props.domainName}/autofix`, payload);
    
    // Re-run the audit to show the updated score
    await runAudit();
    
    // Notify parent that DNS changed
    emit('fixed');
  } catch (err) {
    console.error("Auto-Fix failed", err);
  } finally {
    fixing.value = false;
  }
};

// Run on mount or domain change
watch(() => props.domainName, () => {
  runAudit();
});

onMounted(() => {
  runAudit();
});
</script>

<style scoped>
.sentinel-audit {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0.5rem 0;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1rem;
}
.header-info h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 250, 0.9);
  margin-bottom: 0.2rem;
}
.header-info p {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #fff;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  color: rgba(255, 255, 255, 0.4);
}
.spinner {
  width: 24px; height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.audit-results {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.score-card {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1.5rem;
  background: linear-gradient(145deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
}

.score-details h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
}
.score-details p {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.4;
}

/* Tailwind-ish color overrides if tailwind isn't active on these classes */
.text-green-400 { color: #4ade80; }
.text-orange-400 { color: #fbbf24; }
.text-red-400 { color: #f87171; }

.security-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  opacity: 0.5;
  transition: all 0.3s;
}
.feature-item.active {
  opacity: 1;
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
}
.feature-item .icon { font-size: 1.2rem; }
.feature-item h5 { font-size: 0.8rem; font-weight: 600; color: rgba(255, 255, 250, 0.9); margin-bottom: 0.2rem; }
.feature-item p { font-size: 0.7rem; color: rgba(255, 255, 255, 0.4); }

.fixes-section {
  padding: 1.5rem;
  background: rgba(255, 165, 0, 0.05); /* very subtle orange tint */
  border: 1px solid rgba(255, 165, 0, 0.1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fixes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.fixes-header h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 250, 0.8);
}
.badge {
  padding: 0.2rem 0.5rem;
  background: rgba(255, 165, 0, 0.2);
  color: #fbbf24;
  border-radius: 99px;
  font-size: 0.7rem;
  font-weight: 600;
}

.fix-list { display: flex; flex-direction: column; gap: 0.5rem; }
.fix-item {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.03);
}
.fix-code {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.fix-code .type {
  font-size: 0.65rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}
.fix-code code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  word-break: break-all;
}

.btn-autofix {
  margin-top: 0.5rem;
  padding: 0.8rem;
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(234, 179, 8, 0.05));
  border: 1px solid rgba(234, 179, 8, 0.3);
  border-radius: 12px;
  color: #fbbf24;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s;
  box-shadow: 0 4px 20px rgba(234, 179, 8, 0.1);
}
.btn-autofix:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.3), rgba(234, 179, 8, 0.1));
  box-shadow: 0 4px 25px rgba(234, 179, 8, 0.2);
  transform: translateY(-1px);
}
.btn-autofix:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.magic-icon { font-size: 1.1rem; }

.perfect-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem;
  background: rgba(74, 222, 128, 0.05);
  border: 1px solid rgba(74, 222, 128, 0.1);
  border-radius: 16px;
  text-align: center;
  gap: 0.5rem;
}
.perfect-state p { color: rgba(74, 222, 128, 0.8); font-size: 0.9rem; }
</style>
