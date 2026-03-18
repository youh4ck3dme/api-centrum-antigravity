<script setup>
import { ref, watch } from 'vue';
import { HardDrive, Server, Plus, X, RefreshCcw, Trash2, Shield, Lock } from 'lucide-vue-next';

const props = defineProps({
  selectedDomain: { type: String, default: null },
  selectedDomainObj: { type: Object, default: null },
  ftpAccounts: { type: Array, default: () => [] },
  ftpLoading: { type: Boolean, default: false },
  savingAccount: { type: Boolean, default: false }
});

const emit = defineEmits(['add-account', 'delete-account']);

const showAddForm = ref(false);
const newAcc = ref({ 
  login: "", 
  password: "", 
  dir: "/", 
  disabled: false, 
  ftpEnabled: true, 
  sshEnabled: false,
  note: ""
});

watch(() => props.selectedDomain, () => {
  showAddForm.value = false;
  newAcc.value = { login: "", password: "", dir: "/", disabled: false, ftpEnabled: true, sshEnabled: false, note: "" };
});

const handleAdd = () => {
  if (!newAcc.value.login || !newAcc.value.password) return;
  emit('add-account', { ...newAcc.value });
};

defineExpose({
  closeAddForm: () => {
    showAddForm.value = false;
    newAcc.value = { login: "", password: "", dir: "/", disabled: false, ftpEnabled: true, sshEnabled: false, note: "" };
  }
});
</script>

<template>
  <!-- Using the same glass-panel style as DnsPanel -->
  <div class="flex-1 flex flex-col min-h-0 overflow-hidden">
    <!-- Header / Add Button -->
    <div class="p-8 border-b border-black/5 space-y-4 bg-black/[0.01]">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-primary-indigo/10 border border-primary-indigo/20 flex items-center justify-center text-xl shadow-sm">
              📂
            </div>
            <div>
              <h3 class="text-xl font-bold text-text-main tracking-tight leading-none mb-1">FTP Akonty</h3>
              <p class="text-[10px] font-bold text-text-dim uppercase tracking-[0.2em]">Správa súborových prístupov</p>
            </div>
          </div>
          <button 
            v-if="!selectedDomainObj?.readonly" 
            @click="showAddForm = !showAddForm"
            class="px-5 py-2.5 rounded-xl bg-primary-indigo text-white text-[10px] font-bold uppercase tracking-widest shadow-premium hover:translate-y-[-2px] transition-all flex items-center gap-2 group/btn"
          >
            <Plus v-if="!showAddForm" class="w-3.5 h-3.5" />
            <X v-else class="w-3.5 h-3.5" />
            {{ showAddForm ? 'Zrušiť' : 'Nový Účet' }}
          </button>
        </div>
    </div>

    <!-- Add FTP form -->
    <transition 
      enter-active-class="transition duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
      enter-from-class="transform -translate-y-8 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-400 ease-[cubic-bezier(0.16,1,0.3,1)]"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-8 opacity-0"
    >
      <div v-if="showAddForm" class="p-8 bg-black/[0.02] border-b border-black/5 space-y-6 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-primary-indigo/5 to-transparent pointer-events-none"></div>
        <div class="grid grid-cols-2 gap-6 relative z-10">
          <div class="space-y-2">
            <label class="text-[10px] font-bold text-text-dim uppercase tracking-widest ml-1">Login</label>
            <input v-model="newAcc.login" class="w-full bg-white border border-black/10 rounded-2xl py-3.5 px-5 text-text-main text-sm outline-none focus:border-primary-indigo transition-all font-mono shadow-sm" placeholder="napr. admin" />
          </div>
          <div class="space-y-2">
            <label class="text-[10px] font-bold text-text-dim uppercase tracking-widest ml-1">Heslo</label>
            <input v-model="newAcc.password" type="password" class="w-full bg-white border border-black/10 rounded-2xl py-3.5 px-5 text-text-main text-sm outline-none focus:border-primary-indigo transition-all font-mono shadow-sm" placeholder="********" />
          </div>
        </div>
        <div class="grid grid-cols-[1fr_200px] gap-6 relative z-10">
          <div class="space-y-2">
            <label class="text-[10px] font-bold text-text-dim uppercase tracking-widest ml-1">Domovský Adresár</label>
            <input v-model="newAcc.dir" class="w-full bg-white border border-black/10 rounded-2xl py-3.5 px-5 text-text-main text-sm outline-none focus:border-primary-indigo transition-all font-mono shadow-sm" placeholder="/" />
          </div>
          <div class="flex items-center gap-6 pt-6">
            <label class="flex items-center gap-3 cursor-pointer group">
                <input type="checkbox" v-model="newAcc.sshEnabled" class="hidden" />
                <div class="w-10 h-6 rounded-full border border-black/10 p-1 transition-all" :class="newAcc.sshEnabled ? 'bg-primary-indigo' : 'bg-black/5'">
                    <div class="w-4 h-4 rounded-full bg-white transition-all shadow-sm" :class="{ 'translate-x-4': newAcc.sshEnabled }"></div>
                </div>
                <span class="text-[10px] font-bold uppercase tracking-widest" :class="newAcc.sshEnabled ? 'text-text-main' : 'text-text-dim'">SSH</span>
            </label>
          </div>
        </div>
        <button 
          @click="handleAdd" 
          class="w-full py-4 bg-primary-indigo text-white font-bold rounded-2xl shadow-premium hover:scale-[1.01] transition-all disabled:opacity-50 relative z-10 flex items-center justify-center gap-3"
          :disabled="savingAccount"
        >
          <RefreshCcw class="w-5 h-5 animate-spin" v-if="savingAccount" />
          <span v-else>Vytvoriť FTP Prístup</span>
        </button>
      </div>
    </transition>

    <!-- Content / Table -->
    <div v-if="ftpLoading" class="flex-1 flex flex-col items-center justify-center gap-6">
      <div class="w-10 h-10 border-2 border-black/5 border-t-primary-indigo rounded-full animate-spin"></div>
      <span class="text-[10px] font-bold text-text-dim uppercase tracking-[0.4em]">Načítavam FTP kľúče...</span>
    </div>

    <div v-else class="flex-1 overflow-x-auto custom-scrollbar">
      <table class="w-full text-left border-collapse">
        <thead class="sticky top-0 bg-white/90 backdrop-blur-xl z-20">
          <tr>
            <th class="p-6 text-[9px] font-bold text-text-dim uppercase tracking-[0.2em] border-b border-black/5">Login</th>
            <th class="p-6 text-[9px] font-bold text-text-dim uppercase tracking-[0.2em] border-b border-black/5">Directory</th>
            <th class="p-6 text-[9px] font-bold text-text-dim uppercase tracking-[0.2em] border-b border-black/5">Capabilities</th>
            <th class="p-6 border-b border-black/5"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-black/[0.03]">
          <tr v-for="acc in ftpAccounts" :key="acc.id" class="group hover:bg-black/[0.01] transition-colors relative">
            <td class="p-6 whitespace-nowrap">
              <div class="flex items-center gap-3">
                 <div class="w-8 h-8 rounded-lg bg-black/5 flex items-center justify-center text-text-dim group-hover:bg-primary-indigo/10 group-hover:text-primary-indigo transition-all">
                    <Server class="w-4 h-4" />
                 </div>
                 <span class="text-xs font-bold text-text-main tracking-wide">{{ acc.login }}</span>
              </div>
            </td>
            <td class="p-6 font-mono text-xs text-text-dim">{{ acc.dir }}</td>
            <td class="p-6">
              <div class="flex items-center gap-2">
                <span v-if="acc.ftpEnabled" class="px-2 py-0.5 rounded-md bg-accent-green/10 text-accent-green text-[8px] font-black uppercase border border-accent-green/20">FTP</span>
                <span v-if="acc.sshEnabled" class="px-2 py-0.5 rounded-md bg-primary-indigo/10 text-primary-indigo text-[8px] font-black uppercase border border-primary-indigo/20">SSH</span>
                <span v-if="acc.disabled" class="px-2 py-0.5 rounded-md bg-accent-rose/10 text-accent-rose text-[8px] font-black uppercase border border-accent-rose/20">Disabled</span>
              </div>
            </td>
            <td class="p-6 text-right">
              <button @click="emit('delete-account', acc)" class="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-accent-rose/10 text-text-dim hover:text-accent-rose transition-all group/del">
                 <Trash2 class="w-4 h-4" />
              </button>
            </td>
          </tr>
          <tr v-if="!ftpAccounts.length">
            <td colspan="4" class="p-20 text-center">
              <p class="text-[10px] font-bold text-text-dim uppercase tracking-[0.2em]">Žiadne FTP účty nenájdené</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
