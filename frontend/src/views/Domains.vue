<template>
  <div class="domains-root">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">Správa Domén</h2>
        <p class="page-sub">Websupport DNS manager — {{ domains.length }} domén</p>
      </div>
      <button @click="fetchDomains" class="btn-ghost" :disabled="loading">
        <span :style="loading ? 'display:inline-block;animation:spin .7s linear infinite' : ''">🔄</span>
        {{ loading ? 'Načítavam...' : 'Obnoviť' }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading && !domains.length" class="empty-state">
      <div class="spinner"></div>
      <span>Načítavam domény z Websupport...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!domains.length && !loading" class="empty-state">
      <span style="font-size:2rem">🌐</span>
      <span>Žiadne domény nenájdené</span>
    </div>

    <!-- Two-panel layout -->
    <div v-else class="two-panel">

      <!-- Domain list -->
      <div class="panel domain-list-panel">
        <div class="panel-header">
          <span class="panel-title">Domény</span>
          <span class="count-badge">{{ domains.length }}</span>
        </div>
        <ul class="domain-ul">
          <li
            v-for="d in domains"
            :key="d.id"
            class="domain-item"
            :class="{ selected: selectedDomain === d.name }"
            @click="selectDomain(d)"
          >
            <div class="domain-icon">🌐</div>
            <div class="domain-body">
              <p class="domain-name">{{ d.name }}</p>
              <p class="domain-sub">{{ formatExpiry(d.expireTime) }}</p>
            </div>
            <span class="status-dot" :class="d.status === 'active' ? 'green' : 'red'"></span>
          </li>
        </ul>
      </div>

      <!-- DNS Records panel -->
      <div class="panel dns-panel">
        <div v-if="!selectedDomain" class="empty-state" style="height:100%">
          <span style="font-size:2rem">👈</span>
          <span>Vyber doménu zo zoznamu</span>
        </div>

        <template v-else>
          <div class="panel-header" style="flex-direction: column; align-items: stretch; gap: 0.8rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="panel-title">{{ selectedDomain }}</span>
              <button v-if="activeTab === 'dns'" class="btn-add" @click="showAddForm = !showAddForm">
                {{ showAddForm ? '✕ Zrušiť' : '+ Pridať záznam' }}
              </button>
            </div>
            <div class="tabs-container">
              <button class="tab-btn" :class="{ active: activeTab === 'dns' }" @click="activeTab = 'dns'">DNS Záznamy</button>
              <button class="tab-btn ai-tab" :class="{ active: activeTab === 'sentinel' }" @click="activeTab = 'sentinel'">
                <span style="font-size: 0.9em; margin-right: 4px;">🛡️</span> AI Sentinel
              </button>
            </div>
          </div>

          <!-- DNS Tab Content -->
          <div v-if="activeTab === 'dns'" style="display: flex; flex-direction: column; flex: 1; min-height: 0;">

          <!-- Add DNS form -->
          <div v-if="showAddForm" class="add-form">
            <div class="form-row">
              <select v-model="newRec.type" class="form-select">
                <option>A</option><option>AAAA</option><option>CNAME</option>
                <option>MX</option><option>TXT</option><option>NS</option>
              </select>
              <input v-model="newRec.name" class="form-input" placeholder="Meno (napr. api)" />
            </div>
            <div class="form-row">
              <input v-model="newRec.content" class="form-input flex-1" placeholder="Hodnota (IP / hostname / text)" />
              <input v-model.number="newRec.ttl" type="number" class="form-input ttl-input" placeholder="TTL" />
            </div>
            <button @click="addRecord" class="btn-save" :disabled="savingRecord">
              {{ savingRecord ? 'Ukladám...' : 'Uložiť záznam' }}
            </button>
          </div>

          <!-- DNS loading -->
          <div v-if="dnsLoading" class="empty-state">
            <div class="spinner"></div>
            <span>Načítavam DNS záznamy...</span>
          </div>

          <!-- DNS table -->
          <div v-else class="dns-scroll">
            <table class="dns-table">
              <thead>
                <tr>
                  <th>Typ</th><th>Meno</th><th>Hodnota</th><th>TTL</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="rec in dnsRecords" :key="rec.id" class="dns-row">
                  <td><span class="type-badge" :class="rec.type.toLowerCase()">{{ rec.type }}</span></td>
                  <td class="mono">{{ rec.name }}</td>
                  <td class="mono content-cell">{{ rec.content }}</td>
                  <td class="ttl-cell">{{ rec.ttl }}s</td>
                  <td>
                    <button class="del-btn" @click="deleteRecord(rec)" title="Zmazať">🗑</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          </div>

          <!-- Sentinel Tab Content -->
          <div v-else-if="activeTab === 'sentinel'" style="flex: 1; overflow-y: auto; padding: 0.5rem 1rem;">
            <SentinelAudit :domainName="selectedDomain" @fixed="handleSentinelFixed" />
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/api";
import SentinelAudit from "../components/domains/SentinelAudit.vue";

const domains = ref([]);
const loading = ref(false);
const selectedDomain = ref(null);
const dnsRecords = ref([]);
const dnsLoading = ref(false);
const showAddForm = ref(false);
const savingRecord = ref(false);
const newRec = ref({ type: "A", name: "", content: "", ttl: 600 });
const activeTab = ref('dns');

const fetchDomains = async () => {
  loading.value = true;
  try {
    const res = await api.get("/domains");
    domains.value = res.data.domains || [];
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const selectDomain = async (d) => {
  if (selectedDomain.value !== d.name) {
    activeTab.value = 'dns'; // Reset tab on domain change
  }
  selectedDomain.value = d.name;
  showAddForm.value = false;
  dnsLoading.value = true;
  dnsRecords.value = [];
  try {
    const res = await api.get(`/domains/${d.name}/dns`);
    dnsRecords.value = res.data.records || [];
  } catch (err) {
    console.error(err);
  } finally {
    dnsLoading.value = false;
  }
};

const handleSentinelFixed = async () => {
  // Silent refresh of DNS records after auto-fix
  try {
    const res = await api.get(`/domains/${selectedDomain.value}/dns`);
    dnsRecords.value = res.data.records || [];
  } catch (err) {
    console.error(err);
  }
};

const addRecord = async () => {
  if (!newRec.value.name || !newRec.value.content) return;
  savingRecord.value = true;
  try {
    await api.post(`/domains/${selectedDomain.value}/dns`, { ...newRec.value });
    newRec.value = { type: "A", name: "", content: "", ttl: 600 };
    showAddForm.value = false;
    // Refresh
    const res = await api.get(`/domains/${selectedDomain.value}/dns`);
    dnsRecords.value = res.data.records || [];
  } catch (err) {
    console.error(err);
  } finally {
    savingRecord.value = false;
  }
};

const deleteRecord = async (rec) => {
  if (!confirm(`Zmazať ${rec.type} záznam "${rec.name}"?`)) return;
  try {
    await api.delete(`/domains/${selectedDomain.value}/dns/${rec.id}`);
    dnsRecords.value = dnsRecords.value.filter(r => r.id !== rec.id);
  } catch (err) {
    console.error(err);
  }
};

const formatExpiry = (ts) => {
  if (!ts) return '';
  const d = new Date(ts * 1000);
  return 'Platí do: ' + d.toLocaleDateString('sk-SK');
};

onMounted(fetchDomains);
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }

.domains-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; height: 100%; }

/* Header */
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
.page-title { font-size: 1.35rem; font-weight: 700; color: rgba(255,255,250,0.92); letter-spacing: -0.02em; }
.page-sub { font-size: 0.78rem; color: rgba(255,255,255,0.3); margin-top: 0.2rem; }

.btn-ghost {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 0.9rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  color: rgba(255,255,250,0.6);
  font-size: 0.8rem; font-weight: 500;
  cursor: pointer; transition: all 0.18s;
  white-space: nowrap;
}
.btn-ghost:hover { background: rgba(255,255,255,0.09); color: rgba(255,255,250,0.9); }
.btn-ghost:disabled { opacity: 0.4; cursor: not-allowed; }

/* Two-panel */
.two-panel { display: grid; grid-template-columns: 280px 1fr; gap: 1rem; flex: 1; min-height: 0; }
@media (max-width: 640px) { .two-panel { grid-template-columns: 1fr; } }

/* Panel */
.panel {
  border-radius: 20px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(16px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 4px 24px rgba(0,0,0,0.3);
  display: flex; flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.panel-title { font-size: 0.82rem; font-weight: 600; color: rgba(255,255,250,0.8); }
.count-badge {
  font-size: 0.7rem; font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.4);
  border: 1px solid rgba(255,255,255,0.07);
}

/* Tabs */
.tabs-container {
  display: flex; gap: 0.5rem;
  padding: 0.2rem;
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.04);
}
.tab-btn {
  flex: 1; padding: 0.4rem 0;
  border-radius: 8px; border: none; background: transparent;
  color: rgba(255,255,250,0.5); font-size: 0.75rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s ease;
}
.tab-btn:hover { color: rgba(255,255,250,0.8); }
.tab-btn.active {
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,250,0.95);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.ai-tab.active {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.15), rgba(234, 179, 8, 0.05));
  color: #fbbf24;
  border: 1px solid rgba(234, 179, 8, 0.2);
}

/* Domain list */
.domain-ul { list-style: none; overflow-y: auto; flex: 1; }
.domain-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  cursor: pointer; transition: background 0.15s;
}
.domain-item:hover { background: rgba(255,255,255,0.04); }
.domain-item.selected { background: rgba(255,255,255,0.07); }
.domain-item:last-child { border-bottom: none; }
.domain-icon { font-size: 1rem; flex-shrink: 0; opacity: 0.6; }
.domain-body { flex: 1; min-width: 0; }
.domain-name { font-size: 0.82rem; font-weight: 600; color: rgba(255,255,250,0.85); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.domain-sub { font-size: 0.68rem; color: rgba(255,255,255,0.28); margin-top: 0.1rem; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.status-dot.green { background: #4ade80; box-shadow: 0 0 6px rgba(74,222,128,0.5); }
.status-dot.red { background: #f87171; }

/* DNS panel */
.dns-panel { min-height: 400px; }

.btn-add {
  font-size: 0.72rem; font-weight: 600;
  padding: 0.3rem 0.7rem;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,250,0.7);
  cursor: pointer; transition: all 0.18s;
}
.btn-add:hover { background: rgba(255,255,255,0.1); color: rgba(255,255,250,0.95); }

/* Add form */
.add-form {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex; flex-direction: column; gap: 0.6rem;
  flex-shrink: 0;
}
.form-row { display: flex; gap: 0.5rem; }
.form-select, .form-input {
  padding: 0.5rem 0.75rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: rgba(255,255,250,0.88);
  font-size: 0.82rem;
  outline: none;
  transition: border-color 0.2s;
}
.form-select { flex-shrink: 0; min-width: 80px; cursor: pointer; }
.form-input { flex: 1; }
.form-input.ttl-input { max-width: 90px; flex: none; }
.form-select:focus, .form-input:focus { border-color: rgba(255,255,250,0.3); }
.form-input::placeholder { color: rgba(255,255,255,0.2); }
.btn-save {
  align-self: flex-start;
  padding: 0.5rem 1.1rem;
  border-radius: 10px;
  border: 1px solid rgba(255,255,250,0.18);
  background: rgba(255,255,250,0.1);
  color: rgba(255,255,250,0.92);
  font-size: 0.82rem; font-weight: 600;
  cursor: pointer; transition: all 0.18s;
}
.btn-save:hover:not(:disabled) { background: rgba(255,255,250,0.15); }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }

/* DNS table */
.dns-scroll { flex: 1; overflow-y: auto; }
.dns-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.dns-table thead tr {
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.dns-table th {
  padding: 0.6rem 1rem;
  text-align: left;
  font-size: 0.65rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
  color: rgba(255,255,255,0.28);
}
.dns-row { border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.12s; }
.dns-row:hover { background: rgba(255,255,255,0.03); }
.dns-row:last-child { border-bottom: none; }
.dns-table td { padding: 0.6rem 1rem; color: rgba(255,255,250,0.75); vertical-align: middle; }
.mono { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.75rem; }
.content-cell { max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ttl-cell { color: rgba(255,255,255,0.3); font-size: 0.72rem; white-space: nowrap; }

/* Type badges */
.type-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.05em;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,250,0.55);
}
.type-badge.a    { background: rgba(96,165,250,0.12); color: #60a5fa; border-color: rgba(96,165,250,0.2); }
.type-badge.aaaa { background: rgba(129,140,248,0.12); color: #818cf8; border-color: rgba(129,140,248,0.2); }
.type-badge.cname{ background: rgba(52,211,153,0.12); color: #34d399; border-color: rgba(52,211,153,0.2); }
.type-badge.mx   { background: rgba(251,191,36,0.12); color: #fbbf24; border-color: rgba(251,191,36,0.2); }
.type-badge.txt  { background: rgba(167,139,250,0.12); color: #a78bfa; border-color: rgba(167,139,250,0.2); }
.type-badge.ns   { background: rgba(251,146,60,0.12); color: #fb923c; border-color: rgba(251,146,60,0.2); }

.del-btn {
  background: none; border: none; cursor: pointer;
  font-size: 0.85rem; opacity: 0.3; transition: opacity 0.18s;
  padding: 0.2rem 0.4rem;
}
.del-btn:hover { opacity: 0.9; }

/* Empty state */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.6rem; padding: 3rem; color: rgba(255,255,255,0.28); font-size: 0.85rem;
}
.spinner {
  width: 22px; height: 22px;
  border: 2px solid rgba(255,255,255,0.1);
  border-top-color: rgba(255,255,255,0.5);
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
</style>
