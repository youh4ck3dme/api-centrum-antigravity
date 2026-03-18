<script setup>
import { ref } from 'vue';
import { X, Server, RefreshCcw } from 'lucide-vue-next';

const props = defineProps({
  show: { type: Boolean, default: false }
});

const emit = defineEmits(['close']);

const provLoading = ref(false);
const provStatus = ref('');
const provStatusClass = ref('');
const prov = ref({ name: '', provider: 'hetzner', region: '', domain: '' });

async function startProvision() {
  provLoading.value = true;
  provStatus.value = 'Vytvára sa server...';
  provStatusClass.value = 'status-info';
  try {
    const res = await fetch('/api/dns-monitor/provision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(prov.value),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Chyba pri vytváraní');
    provStatus.value = `Job spustený: ${data.job_id}`;
    provStatusClass.value = 'status-ok';
    pollJobStatus(data.job_id);
  } catch (e) {
    provStatus.value = `Chyba: ${e.message}`;
    provStatusClass.value = 'status-err';
  } finally {
    provLoading.value = false;
  }
}

async function pollJobStatus(jobId) {
  let attempts = 0;
  const poll = setInterval(async () => {
    attempts++;
    if (attempts > 60) {
      clearInterval(poll);
      provStatus.value = 'Timeout — skontrolujte stav manuálne';
      provStatusClass.value = 'status-err';
      return;
    }
    try {
      const res = await fetch(`/api/dns-monitor/provision/${jobId}`);
      const data = await res.json();
      provStatus.value = `[${data.progress ?? 0}%] ${data.step ?? 'neznámy krok'}`;
      if (data.status === 'completed') {
        clearInterval(poll);
        provStatus.value = `✅ Server vytvorený! IP: ${data.server_ip ?? 'neznáme'}`;
        provStatusClass.value = 'status-ok';
      } else if (data.status === 'failed') {
        clearInterval(poll);
        provStatus.value = `❌ Zlyhalo: ${data.error ?? 'neznáma chyba'}`;
        provStatusClass.value = 'status-err';
      } else {
        provStatusClass.value = 'status-info';
      }
    } catch {
      // ignore poll errors
    }
  }, 3000);
}
</script>

<template>
  <div v-if="show" class="modal-overlay fixed inset-0 z-[4000] bg-black/60 backdrop-blur-xl flex items-center justify-center p-6" @click.self="emit('close')">
    <div class="modal-card glass-panel w-full max-w-[480px] rounded-[40px] overflow-hidden shadow-2xl animate-in zoom-in-95 duration-500">
      <div class="modal-header p-8 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-primary-indigo/10 border border-primary-indigo/20 flex items-center justify-center shadow-lg">
             <Server class="w-6 h-6 text-primary-indigo" />
          </div>
          <h3 class="text-xl font-bold text-white tracking-tight">Provisioning Centrála</h3>
        </div>
        <button class="modal-close w-10 h-10 flex items-center justify-center rounded-xl hover:bg-white/5 transition-all outline-none" @click="emit('close')">
          <X class="w-5 h-5 text-white/40" />
        </button>
      </div>
      
      <div class="modal-body p-8 space-y-6">
        <div class="space-y-4">
          <div class="space-y-2">
            <label class="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] ml-1">Názov Severa</label>
            <input v-model="prov.name" class="w-full bg-slate-950/50 border border-white/10 rounded-2xl py-3.5 px-5 text-white text-sm outline-none focus:border-primary-cyan/50 transition-all shadow-inner" placeholder="napr. production-01" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] ml-1">Cloud Provider</label>
              <select v-model="prov.provider" class="w-full bg-slate-950/50 border border-white/10 rounded-2xl py-3.5 px-5 text-white text-sm outline-none focus:border-primary-cyan/50 transition-all cursor-pointer shadow-inner">
                <option value="hetzner">Hetzner Cloud</option>
                <option value="digitalocean">DigitalOcean</option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] ml-1">Datacenter Region</label>
              <input v-model="prov.region" class="w-full bg-slate-950/50 border border-white/10 rounded-2xl py-3.5 px-5 text-white text-sm outline-none focus:border-primary-cyan/50 transition-all shadow-inner" placeholder="napr. nbg1" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] ml-1">Cieľová Doména (A)</label>
            <input v-model="prov.domain" class="w-full bg-slate-950/50 border border-white/10 rounded-2xl py-3.5 px-5 text-white text-sm outline-none focus:border-primary-cyan/50 transition-all shadow-inner font-mono" placeholder="app.example.com" />
          </div>
        </div>

        <div v-if="provStatus" class="prov-status p-4 rounded-2xl border transition-all text-xs font-bold tracking-tight shadow-lg flex items-center gap-3" :class="[
          provStatusClass === 'status-info' ? 'bg-primary-indigo/10 border-primary-indigo/30 text-primary-indigo' : '',
          provStatusClass === 'status-ok' ? 'bg-accent-green/10 border-accent-green/30 text-accent-green' : '',
          provStatusClass === 'status-err' ? 'bg-accent-rose/10 border-accent-rose/30 text-accent-rose' : ''
        ]">
          <RefreshCcw v-if="provLoading" class="w-4 h-4 animate-spin flex-shrink-0" />
          {{ provStatus }}
        </div>
      </div>

      <div class="modal-footer p-8 pt-0 flex gap-4">
        <button class="flex-1 py-4 rounded-2xl bg-white/5 border border-white/5 text-white/40 font-bold text-sm hover:bg-white/10 transition-all active:scale-95" @click="emit('close')">Zrušiť</button>
        <button class="flex-2 py-4 rounded-2xl bg-primary-indigo text-white font-black text-sm shadow-xl hover:translate-y-[-2px] active:translate-y-[0px] transition-all disabled:opacity-50 flex items-center justify-center gap-2" @click="startProvision" :disabled="provLoading">
          <RefreshCcw v-if="provLoading" class="w-4 h-4 animate-spin" />
          {{ provLoading ? 'Provisioning...' : 'Inicializovať Server' }}
        </button>
      </div>
    </div>
  </div>
</template>
