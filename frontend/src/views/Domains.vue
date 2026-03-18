<script setup>
import { ref, computed, onMounted } from "vue";
import { RefreshCcw } from 'lucide-vue-next';
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
  <div class="flex-1 p-6 lg:p-10 overflow-y-auto custom-scrollbar relative animate-in fade-in slide-in-from-bottom-4 duration-700">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-12">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-black/5 border border-black/10 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-primary-indigo shadow-[0_0_8px_rgba(0,113,227,0.3)] anim-pulse"></span>
            <span class="text-[9px] uppercase font-black text-text-dim tracking-[0.2em]">Registry Mesh: Optimized</span>
          </div>
          <span v-if="domains.length" class="text-text-dim text-[9px] uppercase tracking-widest font-bold">
            {{ wsDomains.length }} Websupport · {{ forpsiDomains.length }} Forpsi
          </span>
        </div>
        <h1 class="text-4xl lg:text-7xl font-black text-text-main tracking-tighter leading-none">Správa Domén</h1>
        <p class="text-text-dim text-lg font-medium tracking-tight mt-2">
          Komplexná správa DNS záznamov a portfólia sieťových identít.
        </p>
      </div>

      <div class="mt-8 md:mt-0 flex items-center gap-4">
        <div class="flex p-1.5 glass-panel rounded-2xl border border-black/5 shadow-premium overflow-hidden h-14 items-center">
          <button 
            class="px-8 h-10 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
            :class="mainView === 'domains' ? 'bg-primary-indigo text-white shadow-lg' : 'text-text-dim hover:text-text-main'"
            @click="mainView = 'domains'"
          >
            Nódy
          </button>
          <button 
            class="px-8 h-10 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
            :class="mainView === 'portfolio' ? 'bg-primary-indigo text-white shadow-lg' : 'text-text-dim hover:text-text-main'"
            @click="switchToPortfolio"
          >
            Portfolio
          </button>
        </div>

        <button 
          @click="mainView === 'domains' ? fetchDomains() : switchToPortfolio(true)" 
          class="w-14 h-14 flex items-center justify-center rounded-2xl glass-panel text-text-dim hover:text-text-main transition-all shadow-premium hover:scale-105 active:scale-95 group"
          :disabled="loading || portfolioLoading"
        >
          <RefreshCcw 
            class="w-5 h-5 transition-colors"
            :class="{ 'animate-spin': loading || portfolioLoading }"
          />
        </button>
      </div>
    </header>

    <!-- ── Domains view ── -->
    <template v-if="mainView === 'domains'">
      <div v-if="loading && !domains.length" class="flex flex-col items-center justify-center p-32 gap-6">
        <div class="w-12 h-12 border-4 border-black/5 border-t-primary-indigo rounded-full animate-spin"></div>
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
          
          <div v-if="selectedDomain && !selectedDomainObj?.readonly" class="border-t border-black/5 bg-black/[0.02] p-4">
             <div class="flex items-center gap-4 justify-center">
                <span class="text-[9px] font-bold text-text-dim uppercase tracking-widest">Doplnkové moduly</span>
                <div class="h-[1px] flex-1 bg-black/5"></div>
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
