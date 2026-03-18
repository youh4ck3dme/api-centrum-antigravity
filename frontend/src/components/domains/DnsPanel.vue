<script setup>
import { ref, watch } from 'vue';
import { Globe, Zap, ShieldCheck, Plus, X, RefreshCcw, Trash2 } from 'lucide-vue-next';
import SentinelAudit from './SentinelAudit.vue';

const props = defineProps({
  selectedDomain: { type: String, default: null },
  selectedDomainObj: { type: Object, default: null },
  dnsRecords: { type: Array, default: () => [] },
  dnsLoading: { type: Boolean, default: false },
  savingRecord: { type: Boolean, default: false }
});

const emit = defineEmits(['add-record', 'delete-record', 'sentinel-fixed']);

const activeTab = ref('dns');
const showAddForm = ref(false);
const newRec = ref({ type: "A", name: "", content: "", ttl: 600 });

// Reset local state when domain changes
watch(() => props.selectedDomain, () => {
  activeTab.value = 'dns';
  showAddForm.value = false;
  newRec.value = { type: "A", name: "", content: "", ttl: 600 };
});

const handleAdd = () => {
  if (!newRec.value.name || !newRec.value.content) return;
  emit('add-record', { ...newRec.value });
};

// We expose a way to close the form from parent if needed, 
// but here we can just clear it after success if the parent uses a watcher or callback.
// For simplicity, let's keep the form state here and assume the parent will refresh props.
defineExpose({
  closeAddForm: () => {
    showAddForm.value = false;
    newRec.value = { type: "A", name: "", content: "", ttl: 600 };
  }
});
</script>

<template>
  <div class="glass-panel rounded-[32px] overflow-hidden flex flex-col min-h-[600px] shadow-premium relative">
    <div v-if="!selectedDomain" class="flex-1 flex flex-col items-center justify-center gap-6 text-black/5 p-32">
      <div class="relative">
         <Globe class="w-20 h-20 opacity-5" />
         <div class="absolute inset-0 bg-primary-cyan/5 blur-2xl rounded-full"></div>
      </div>
      <span class="text-xs font-bold uppercase tracking-[0.4em] animate-pulse text-center leading-relaxed">Vyberte objekt pre <br/> detailnú konfiguráciu</span>
    </div>

    <template v-else>
      <div class="p-8 border-b border-white/5 space-y-8 bg-white/[0.01]">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-2xl bg-primary-indigo/10 border border-primary-indigo/20 flex items-center justify-center text-2xl shadow-sm">
              🌐
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-900 tracking-tighter leading-none mb-2">{{ selectedDomain }}</h3>
              <div class="flex items-center gap-2">
                 <span class="w-2 h-2 rounded-full bg-accent-green animate-pulse"></span>
                 <p v-if="selectedDomainObj?.readonly" class="text-[10px] font-bold text-accent-rose/70 uppercase tracking-widest">Read-Only Domain Hub</p>
                 <p v-else class="text-[10px] font-bold text-primary-indigo uppercase tracking-widest">Active Control Hub</p>
              </div>
            </div>
          </div>
          <button 
            v-if="activeTab === 'dns' && !selectedDomainObj?.readonly" 
            @click="showAddForm = !showAddForm"
            class="px-6 py-3 rounded-2xl bg-primary-indigo text-white text-xs font-bold shadow-premium hover:translate-y-[-2px] active:translate-y-[0px] transition-all flex items-center gap-3 group/btn"
          >
            <Plus v-if="!showAddForm" class="w-4 h-4 group-hover/btn:rotate-180 transition-transform duration-500" />
            <X v-else class="w-4 h-4" />
            {{ showAddForm ? 'Zrušiť Operáciu' : 'Nový DNS Záznam' }}
          </button>
        </div>

        <div v-if="!selectedDomainObj?.readonly" class="flex p-1.5 bg-black/[0.03] rounded-2xl border border-black/5 w-fit shadow-inner">
          <button 
            v-for="t in [ {id:'dns', label:'Záznamy', icon:Zap}, {id:'sentinel', label:'AI Sentinel', icon:ShieldCheck} ]"
            :key="t.id"
            @click="activeTab = t.id"
            class="px-6 py-2.5 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all flex items-center gap-2.5"
            :class="activeTab === t.id ? 'bg-white text-text-main shadow-sm border border-black/5' : 'text-text-dim hover:text-text-main'"
          >
            <component :is="t.icon" class="w-3.5 h-3.5" :class="activeTab === t.id ? 'text-primary-indigo' : ''" />
            {{ t.label }}
          </button>
        </div>
      </div>

      <!-- DNS Tab Content -->
      <div v-if="activeTab === 'dns'" class="flex-1 flex flex-col min-h-0 overflow-hidden">
        <!-- Add DNS form -->
        <transition 
          enter-active-class="transition duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
          enter-from-class="transform -translate-y-8 opacity-0"
          enter-to-class="transform translate-y-0 opacity-100"
          leave-active-class="transition duration-400 ease-[cubic-bezier(0.16,1,0.3,1)]"
          leave-from-class="transform translate-y-0 opacity-100"
          leave-to-class="transform -translate-y-8 opacity-0"
        >
          <div v-if="showAddForm" class="p-8 bg-primary-indigo/5 border-b border-white/5 space-y-6 relative overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-br from-primary-indigo/10 to-transparent pointer-events-none"></div>
            <div class="grid grid-cols-2 gap-6 relative z-10">
              <div class="space-y-2">
                <label class="text-[10px] font-bold text-text-dim uppercase tracking-widest ml-1">Typ Protokolu</label>
                <select v-model="newRec.type" class="w-full bg-white border border-black/10 rounded-2xl py-3.5 px-5 text-text-main text-sm outline-none focus:border-primary-indigo focus:ring-1 focus:ring-primary-indigo/20 transition-all cursor-pointer shadow-sm">
                  <option>A</option><option>AAAA</option><option>CNAME</option>
                  <option>MX</option><option>TXT</option><option>NS</option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-[10px] font-bold text-text-dim uppercase tracking-widest ml-1">Subdoména / Root</label>
                <input v-model="newRec.name" class="w-full bg-white border border-black/10 rounded-2xl py-3.5 px-5 text-text-main text-sm placeholder-black/10 outline-none focus:border-primary-indigo focus:ring-1 focus:ring-primary-indigo/20 transition-all font-mono shadow-sm" placeholder="napr. api" />
              </div>
            </div>
            <div class="grid grid-cols-[1fr_140px] gap-6 relative z-10">
              <div class="space-y-2">
                <label class="text-[10px] font-bold text-text-dim uppercase tracking-widest ml-1">Cieľová Hodnota</label>
                <input v-model="newRec.content" class="w-full bg-white border border-black/10 rounded-2xl py-3.5 px-5 text-text-main text-sm placeholder-black/10 outline-none focus:border-primary-indigo focus:ring-1 focus:ring-primary-indigo/20 transition-all font-mono shadow-sm" placeholder="IP adresa alebo cieľový host" />
              </div>
              <div class="space-y-2">
                <label class="text-[10px] font-bold text-text-dim uppercase tracking-widest ml-1">Time to Live</label>
                <input v-model.number="newRec.ttl" type="number" class="w-full bg-white border border-black/10 rounded-2xl py-3.5 px-5 text-text-main text-sm outline-none focus:border-primary-indigo transition-all shadow-sm" />
              </div>
            </div>
            <button 
              @click="handleAdd" 
              class="w-full py-4 bg-primary-indigo text-white font-bold rounded-2xl shadow-2xl hover:bg-indigo-600 hover:scale-[1.01] active:scale-[0.99] transition-all disabled:opacity-50 relative z-10 flex items-center justify-center gap-3"
              :disabled="savingRecord"
            >
              <Plus class="w-5 h-5" v-if="!savingRecord" />
              <RefreshCcw class="w-5 h-5 animate-spin" v-else />
              {{ savingRecord ? 'Inicializácia...' : 'Vytvoriť a Propagovať Záznam' }}
            </button>
          </div>
        </transition>

        <!-- DNS table -->
        <div v-if="dnsLoading" class="flex-1 flex flex-col items-center justify-center gap-6">
          <div class="w-10 h-10 border-2 border-black/5 border-t-primary-indigo rounded-full animate-spin"></div>
          <span class="text-[10px] font-bold text-text-dim uppercase tracking-[0.4em]">Querying Name Servers...</span>
        </div>

        <div v-else class="flex-1 overflow-x-auto custom-scrollbar">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 bg-white/90 backdrop-blur-xl z-20">
              <tr>
                <th class="p-6 text-[9px] font-bold text-text-dim uppercase tracking-[0.2em] border-b border-black/5">Type</th>
                <th class="p-6 text-[9px] font-bold text-text-dim uppercase tracking-[0.2em] border-b border-black/5">Identifier</th>
                <th class="p-6 text-[9px] font-bold text-text-dim uppercase tracking-[0.2em] border-b border-black/5">Destination</th>
                <th class="p-6 text-[9px] font-bold text-text-dim uppercase tracking-[0.2em] border-b border-black/5 text-right">TTL</th>
                <th class="p-6 border-b border-black/5"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-black/[0.03]">
              <tr v-for="rec in dnsRecords" :key="rec.id" class="group hover:bg-black/[0.01] transition-colors relative">
                <td class="p-6 whitespace-nowrap">
                  <span 
                    class="px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-widest border transition-all"
                    :class="{
                      'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/20': rec.type === 'A',
                      'bg-accent-green/10 text-accent-green border-accent-green/20': rec.type === 'AAAA',
                      'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/20': rec.type === 'CNAME',
                      'bg-warning/10 text-warning border-warning/20': rec.type === 'MX',
                      'bg-black/5 text-text-dim border-black/10': !['A','AAAA','CNAME','MX'].includes(rec.type)
                    }"
                  >
                    {{ rec.type }}
                  </span>
                </td>
                <td class="p-6 font-mono text-xs text-text-main">{{ rec.name }}</td>
                <td class="p-6 font-mono text-[11px] text-text-dim max-w-[300px] truncate" :title="rec.content">{{ rec.content }}</td>
                <td class="p-6 text-right font-mono text-[11px] text-text-dim">{{ rec.ttl }}s</td>
                <td class="p-6 text-right">
                  <button @click="emit('delete-record', rec)" class="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-accent-rose/10 text-text-dim hover:text-accent-rose transition-all group/del active:scale-90">
                     <Trash2 class="w-4 h-4 transition-transform group-hover/del:rotate-6" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Sentinel Tab Content -->
      <div v-else-if="activeTab === 'sentinel' && !selectedDomainObj?.readonly" class="flex-1 overflow-y-auto custom-scrollbar">
         <div class="p-8">
            <SentinelAudit :domainName="selectedDomain" @fixed="emit('sentinel-fixed')" />
         </div>
      </div>
    </template>
  </div>
</template>
