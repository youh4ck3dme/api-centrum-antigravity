<script setup>
import { ref, computed, onMounted } from "vue";
import { RefreshCcw, Globe } from 'lucide-vue-next';
import api from "../api/api";

// Sub-components
import DomainList from "../components/domains/DomainList.vue";
import DnsPanel from "../components/domains/DnsPanel.vue";
import FTPPanel from "../components/domains/FTPPanel.vue";
import PortfolioView from "../components/domains/PortfolioView.vue";

const mainView = ref('domains');
const domains = ref([]);
const loading = ref(false);
const selectedDomain = ref(null);
const selectedDomainObj = ref(null);
const dnsRecords = ref([]);
const dnsLoading = ref(false);
const savingRecord = ref(false);

const ftpAccounts = ref([]);
const ftpLoading = ref(false);
const savingAccount = ref(false);

// Portfolio
const portfolioData = ref(null);
const portfolioLoading = ref(false);

const fetchPortfolio = async () => {
  portfolioLoading.value = true;
  try {
    const res = await api.get('/domains/portfolio');
    portfolioData.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    portfolioLoading.value = false;
  }
};

const switchToPortfolio = (force = false) => {
  mainView.value = 'portfolio';
  if (!portfolioData.value || force) fetchPortfolio();
};

const wsDomains = computed(() => domains.value.filter(d => !d.readonly));
const forpsiDomains = computed(() => domains.value.filter(d => d.readonly));

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
  selectedDomain.value = d.name;
  selectedDomainObj.value = d;
  dnsRecords.value = [];
  ftpAccounts.value = [];

  if (d.readonly) return;

  dnsLoading.value = true;
  ftpLoading.value = true;
  
  try {
    const [dnsRes, ftpRes] = await Promise.allSettled([
        api.get(`/domains/${d.name}/dns`),
        api.get(`/domains/${d.name}/ftp`)
    ]);
    
    if (dnsRes.status === 'fulfilled') dnsRecords.value = dnsRes.value.data.records || [];
    if (ftpRes.status === 'fulfilled') ftpAccounts.value = ftpRes.value.data.accounts || [];
    
  } catch (err) {
    console.error(err);
  } finally {
    dnsLoading.value = false;
    ftpLoading.value = false;
  }
};

const handleSentinelFixed = async () => {
  try {
    const res = await api.get(`/domains/${selectedDomain.value}/dns`);
    dnsRecords.value = res.data.records || [];
  } catch (err) {
    console.error(err);
  }
};

const fetchFtp = async (domainName) => {
  ftpLoading.value = true;
  try {
    const res = await api.get(`/domains/${domainName}/ftp`);
    ftpAccounts.value = res.data.accounts || [];
  } catch (err) {
    console.error(err);
  } finally {
    ftpLoading.value = false;
  }
};

const ftpPanelRef = ref(null);

const addFtpAccount = async (accData) => {
  savingAccount.value = true;
  try {
    await api.post(`/domains/${selectedDomain.value}/ftp`, accData);
    if (ftpPanelRef.value) ftpPanelRef.value.closeAddForm();
    await fetchFtp(selectedDomain.value);
  } catch (err) {
    console.error(err);
  } finally {
    savingAccount.value = false;
  }
};

const deleteFtpAccount = async (acc) => {
  if (!confirm(`Zmazať FTP účet "${acc.login}"?`)) return;
  try {
    await api.delete(`/domains/${selectedDomain.value}/ftp/${acc.id}`);
    ftpAccounts.value = ftpAccounts.value.filter(a => a.id !== acc.id);
  } catch (err) {
    console.error(err);
  }
};

const dnsPanelRef = ref(null);

const addRecord = async (recordData) => {
  savingRecord.value = true;
  try {
    await api.post(`/domains/${selectedDomain.value}/dns`, recordData);
    if (dnsPanelRef.value) dnsPanelRef.value.closeAddForm();
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

onMounted(fetchDomains);
</script>

<template>
  <div class="flex-1 p-4 lg:p-8 overflow-y-auto custom-scrollbar relative animate-in fade-in slide-in-from-bottom-4 duration-700">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-10">
      <div class="space-y-3">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-2.5 py-1 rounded-md bg-white/5 border border-white/5 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-accent shadow-[0_0_8px_rgba(245,158,11,0.4)] anim-pulse"></span>
            <span class="text-[8px] font-mono text-gray-600 uppercase tracking-widest">Registry Mesh: Optimized</span>
          </div>
          <span v-if="domains.length" class="text-gray-600 text-[8px] font-mono uppercase tracking-widest">
            {{ wsDomains.length }} Websupport · {{ forpsiDomains.length }} Forpsi
          </span>
        </div>
        <h1 class="text-4xl lg:text-6xl font-bold text-white tracking-tight leading-none italic">Správa Domén</h1>
        <p class="text-gray-600 text-sm font-medium tracking-tight mt-2">
          Komplexná správa DNS záznamov a sieťových identít.
        </p>
      </div>

      <div class="mt-6 md:mt-0 flex items-center gap-3">
        <div class="flex p-1 bg-white/5 rounded-xl border border-white/5 items-center">
          <button 
            class="px-5 py-2 rounded-lg text-[9px] font-bold uppercase tracking-widest transition-all"
            :class="mainView === 'domains' ? 'bg-white text-black shadow-lg' : 'text-gray-600 hover:text-white'"
            @click="mainView = 'domains'"
          >
            Nódy
          </button>
          <button 
            class="px-5 py-2 rounded-lg text-[9px] font-bold uppercase tracking-widest transition-all"
            :class="mainView === 'portfolio' ? 'bg-white text-black shadow-lg' : 'text-gray-600 hover:text-white'"
            @click="switchToPortfolio"
          >
            Portfolio
          </button>
        </div>

        <button 
          @click="mainView === 'domains' ? fetchDomains() : switchToPortfolio(true)" 
          class="w-12 h-12 flex items-center justify-center rounded-xl bg-white/5 text-gray-600 hover:text-white transition-all border border-white/5"
          :disabled="loading || portfolioLoading"
        >
          <RefreshCcw 
            class="w-4 h-4 transition-colors"
            :class="{ 'animate-spin': loading || portfolioLoading }"
          />
        </button>
      </div>
    </header>

    <!-- ── Domains view ── -->
    <template v-if="mainView === 'domains'">
      <div v-if="loading && !domains.length" class="flex flex-col items-center justify-center p-32 gap-6">
        <div class="w-12 h-12 border-4 border-border-subtle border-t-primary-indigo rounded-full animate-spin"></div>
        <span class="text-text-dim text-[10px] font-bold uppercase tracking-[0.3em]">Načítavam domény...</span>
      </div>

      <div v-else-if="!domains.length && !loading" class="glass-panel rounded-[40px] p-24 flex flex-col items-center gap-4 text-text-dim">
        <Globe class="w-16 h-16 opacity-10" />
        <span class="text-xs font-bold uppercase tracking-[0.2em]">Žiadne domény nenájdené</span>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-8 items-start">
        <DomainList 
          :domains="domains" 
          :selectedDomain="selectedDomain" 
          @select="selectDomain" 
        />
        
        <div class="glass-panel rounded-[32px] overflow-hidden flex flex-col min-h-[600px] shadow-premium relative">
          <DnsPanel 
            v-if="!selectedDomainObj || (selectedDomainObj && !ftpLoading && dnsRecords.length >= 0)"
            ref="dnsPanelRef"
            :selectedDomain="selectedDomain"
            :selectedDomainObj="selectedDomainObj"
            :dnsRecords="dnsRecords"
            :dnsLoading="dnsLoading"
            :savingRecord="savingRecord"
            @add-record="addRecord"
            @delete-record="deleteRecord"
            @sentinel-fixed="handleSentinelFixed"
          />
          
          <div v-if="selectedDomain && !selectedDomainObj?.readonly" class="border-t border-border-subtle bg-overlay-hover p-4">
             <div class="flex items-center gap-4 justify-center">
                <span class="text-[9px] font-bold text-text-dim uppercase tracking-widest">Doplnkové moduly</span>
                <div class="h-[1px] flex-1 bg-border-subtle"></div>
             </div>
             <div class="mt-4">
                <FTPPanel 
                  ref="ftpPanelRef"
                  :selectedDomain="selectedDomain"
                  :selectedDomainObj="selectedDomainObj"
                  :ftpAccounts="ftpAccounts"
                  :ftpLoading="ftpLoading"
                  :savingAccount="savingAccount"
                  @add-account="addFtpAccount"
                  @delete-account="deleteFtpAccount"
                />
             </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── Portfolio view ── -->
    <template v-else-if="mainView === 'portfolio'">
      <PortfolioView 
        :portfolioData="portfolioData"
        :portfolioLoading="portfolioLoading"
      />
    </template>
  </div>
</template>
