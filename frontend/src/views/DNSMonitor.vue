<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import api from '../api/api';
import useWebSocket from '../composables/useWebSocket';

// Sub-components
import MonitorStats from '../components/dns/MonitorStats.vue';
import ProvisionModal from '../components/dns/ProvisionModal.vue';
import AiAuditPanel from '../components/dns/AiAuditPanel.vue';
import LiveFeed from '../components/dns/LiveFeed.vue';

const feed = ref([]);
const wsStatus = ref('disconnected');
const domainCount = ref(0);
const threatsToday = ref(0);
const lastScan = ref(0);
const auditLoading = ref(false);
const aiAuditResult = ref(null);
const auditedDomain = ref('');
const fixingIndex = ref(-1);
const showProvision = ref(false);

const token = localStorage.getItem('access_token');
const proto = location.protocol === 'https:' ? 'wss' : 'ws';
const wsUrl = `${proto}://${location.host}/api/dns-monitor/ws?token=${token}`;

const { connect, disconnect } = useWebSocket({
  url: wsUrl,
  onMessage(msg) {
    feed.value.unshift(msg);
    if (feed.value.length > 300) feed.value.splice(300);

    if (msg.type === 'snapshot') {
      domainCount.value = msg.domain_count ?? 0;
      threatsToday.value = msg.threats_today ?? 0;
      lastScan.value = msg.last_scan ?? 0;
    } else if (msg.type === 'heartbeat') {
      domainCount.value = msg.domains_checked ?? domainCount.value;
      threatsToday.value = msg.threats_today ?? threatsToday.value;
      lastScan.value = msg.timestamp ?? lastScan.value;
    } else if (msg.type === 'threat') {
      threatsToday.value += 1;
    }
  },
  onStatusChange(s) {
    wsStatus.value = s;
  },
});

onMounted(connect);
onBeforeUnmount(disconnect);

const statusLabel = computed(() => ({
  connected: 'Systém v poriadku',
  connecting: 'Pripájam k sieti...',
  disconnected: 'Odpojený od Matrixu',
}[wsStatus.value] ?? 'Mimo prevádzky'));

const lastScanLabel = computed(() => {
  if (!lastScan.value) return 'čakám...';
  const diff = Math.floor(Date.now() / 1000 - lastScan.value);
  if (diff < 5) return 'práve teraz';
  if (diff < 60) return `pred ${diff}s`;
  if (diff < 3600) return `pred ${Math.floor(diff / 60)}m`;
  return `pred ${Math.floor(diff / 3600)}h`;
});

// AI Logic
async function startGlobalAudit() {
  auditLoading.value = true;
  try {
    const listRes = await api.get('/domains'); 
    const firstDomain = listRes.data.domains?.[0]?.name;
    if (!firstDomain) throw new Error("Žiadne domény na analýzu");

    auditedDomain.value = firstDomain;
    const res = await api.post(`/ai/audit/${firstDomain}`);
    aiAuditResult.value = res.data;
  } catch (err) {
    console.error(err);
    alert("AI Audit zlyhal.");
  } finally {
    auditLoading.value = false;
  }
}

async function applyAiFix(rec) {
  if (!confirm(`Naozaj chcete pridať tento ${rec.type} záznam pre ${auditedDomain.value}?`)) return;
  const idx = aiAuditResult.value.recommendations.indexOf(rec);
  fixingIndex.value = idx;
  try {
    await api.post('/ai/fix', {
      domain: auditedDomain.value,
      record: { type: rec.type, name: rec.name, content: rec.content, ttl: 3600 }
    });
    aiAuditResult.value.recommendations.splice(idx, 1);
  } catch (err) {
    console.error(err);
    alert("Oprava zlyhala.");
  } finally {
    fixingIndex.value = -1;
  }
}
</script>

<template>
  <div class="dns-orchestrator p-6 lg:p-10 space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
    
    <!-- Header -->
    <header class="flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div class="space-y-1">
        <h1 class="text-3xl lg:text-5xl font-black text-white tracking-tighter leading-none mb-2">LIVE DNS MONITOR</h1>
        <div class="flex items-center gap-2">
           <div class="w-2 h-2 rounded-full" :class="wsStatus === 'connected' ? 'bg-accent-green animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-accent-rose'"></div>
           <p class="text-white/40 font-bold tracking-widest text-[10px] uppercase">{{ statusLabel }} · {{ domainCount }} aktívnych monitoringov</p>
        </div>
      </div>
      <button 
        @click="showProvision = true" 
        class="group relative px-8 py-4 bg-primary-indigo text-white font-black text-xs rounded-2xl shadow-2xl hover:translate-y-[-2px] active:translate-y-[0px] transition-all overflow-hidden flex items-center gap-3 uppercase tracking-widest"
      >
        <span class="relative z-10">🖥️ Nový server</span>
        <div class="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
      </button>
    </header>

    <!-- Stat Cards -->
    <MonitorStats 
      :domainCount="domainCount"
      :threatsToday="threatsToday"
      :lastScanLabel="lastScanLabel"
      :feedLength="feed.length"
    />

    <!-- AI Audit -->
    <AiAuditPanel 
      :aiAuditResult="aiAuditResult"
      :auditedDomain="auditedDomain"
      :fixingIndex="fixingIndex"
      @close="aiAuditResult = null"
      @apply-fix="applyAiFix"
    />

    <!-- Main Feed -->
    <LiveFeed 
      :feed="feed"
      :wsStatus="wsStatus"
      :auditLoading="auditLoading"
      @clear-feed="feed = []"
      @global-audit="startGlobalAudit"
    />

    <!-- Modals -->
    <ProvisionModal 
      :show="showProvision"
      @close="showProvision = false"
    />
  </div>
</template>
