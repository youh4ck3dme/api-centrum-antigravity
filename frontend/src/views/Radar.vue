<template>
  <div class="flex-1 p-4 lg:p-8 overflow-y-auto custom-scrollbar relative">
    
    <!-- Hero Header -->
    <header class="relative z-10 flex flex-col md:flex-row md:items-end justify-between mb-10 animate-in fade-in slide-in-from-top-4 duration-700">
      <div class="space-y-3">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-2.5 py-1 rounded-md bg-white/5 border border-white/5 shadow-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-danger shadow-[0_0_8px_rgba(239,68,68,0.6)] animate-pulse"></span>
            <span class="text-[8px] font-mono text-gray-600 uppercase tracking-widest">Threat Detection: ACTIVE</span>
          </div>
          <span v-if="data" class="text-gray-600 text-[8px] font-mono uppercase tracking-widest">
            Signals: {{ data.shadow_count }} Shadow Targets
          </span>
        </div>
        <h1 class="text-4xl lg:text-6xl font-bold text-white tracking-tight leading-none italic">Shadow Radar</h1>
        <p class="text-gray-600 text-sm font-medium tracking-tight">Detekcia nezdokumentovaných API endpointov.</p>
      </div>

      <div class="mt-6 md:mt-0 flex flex-wrap gap-3">
        <button 
          @click="seed" 
          class="btn-industrial btn-industrial-secondary text-[10px] uppercase tracking-widest gap-2"
          :disabled="seeding"
        >
          <Database class="w-3.5 h-3.5" :class="{ 'animate-pulse text-brand-success': seeding }" />
          <span>{{ seeding ? 'Seeding...' : 'Seed Matrix' }}</span>
        </button>

        <button 
          @click="scan" 
          class="btn-industrial btn-industrial-secondary text-[10px] uppercase tracking-widest gap-2"
          :disabled="scanning"
        >
          <Search class="w-3.5 h-3.5" :class="{ 'animate-spin text-brand-accent': scanning }" />
          <span>{{ scanning ? 'Scanning...' : 'Scan Node' }}</span>
        </button>

        <button 
          @click="fetchEndpoints" 
          class="w-12 h-12 rounded-xl bg-white/5 hover:bg-white/10 text-gray-600 hover:text-white transition-all border border-white/5 flex items-center justify-center"
          :disabled="loading"
        >
          <RefreshCcw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-4 mb-10" v-if="data">
      <div v-for="(stat, sIdx) in [
        { label: 'Total Observed', value: data.total, icon: Radio, color: 'white' },
        { label: 'Shadow Endpoints', value: data.shadow_count, icon: ShieldAlert, color: 'brand-danger', isShadow: true },
        { label: 'Documented Base', value: data.known_count, icon: ShieldCheck, color: 'brand-success' }
      ]" :key="sIdx"
        class="group bg-[#0B0C0E] p-6 rounded-2xl border border-white/5 transition-all hover:border-white/20 relative overflow-hidden"
      >
        <div class="flex items-center gap-4 mb-4 relative z-10">
          <div class="w-10 h-10 rounded-lg bg-white/5 border border-white/5 flex items-center justify-center transition-all bg-white/5">
            <component :is="stat.icon" class="w-4 h-4" :class="`text-${stat.color}`" />
          </div>
          <h3 class="text-[8px] font-mono text-gray-600 uppercase tracking-widest leading-none">{{ stat.label }}</h3>
        </div>
        <div class="relative z-10">
          <p class="text-4xl font-bold text-white tracking-tight" :class="stat.isShadow ? 'text-brand-danger animate-pulse' : ''">
            {{ stat.value }}
          </p>
        </div>
      </div>
    </div>

    <!-- Main List Panel -->
    <div class="relative z-10 bg-[#0B0C0E] rounded-3xl border border-white/5 overflow-hidden shadow-2xl">
      <div class="p-6 border-b border-white/5 flex flex-col sm:flex-row sm:items-center justify-between bg-white/[0.01] gap-4">
        <div>
          <h2 class="text-xl font-bold text-white tracking-tight">Signal Stream</h2>
          <p class="text-gray-600 text-[10px] font-mono mt-1 uppercase tracking-widest">Real-time Intercept v4.0</p>
        </div>
        <div class="flex items-center gap-4">
           <label class="flex items-center gap-2 cursor-pointer group">
             <input type="checkbox" v-model="showShadowOnly" class="w-4 h-4 rounded bg-white/5 border-white/10 text-brand-danger focus:ring-brand-danger transition-all" />
             <span class="text-[9px] font-mono uppercase tracking-widest transition-colors" :class="showShadowOnly ? 'text-brand-danger' : 'text-gray-600'">Shadow Only</span>
           </label>
           <span class="px-3 py-1 bg-white/5 rounded-lg text-gray-600 text-[9px] font-mono uppercase tracking-widest border border-white/5">
            {{ filteredEndpoints.length }} SIGNALS
          </span>
        </div>
      </div>

      <div class="table-wrap custom-scrollbar overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-white/[0.02]">
              <th class="p-4 py-3 text-[8px] font-mono text-gray-600 uppercase tracking-widest first:pl-6">Method</th>
              <th class="p-4 py-3 text-[8px] font-mono text-gray-600 uppercase tracking-widest">Resource Path</th>
              <th class="p-4 py-3 text-[8px] font-mono text-gray-600 uppercase tracking-widest text-center">Freq</th>
              <th class="p-4 py-3 text-[8px] font-mono text-gray-600 uppercase tracking-widest">Last Intercept</th>
              <th class="p-4 py-3 text-[8px] font-mono text-gray-600 uppercase tracking-widest last:pr-6">State</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr v-for="e in filteredEndpoints" :key="e.id" 
              class="group transition-colors duration-200"
              :class="e.is_shadow ? 'bg-brand-danger/[0.03] hover:bg-brand-danger/[0.05]' : 'hover:bg-white/[0.02]'"
            >
              <td class="p-4 py-4 first:pl-6">
                 <span 
                  class="px-2 py-0.5 rounded text-[8px] font-mono uppercase tracking-widest border"
                  :class="methodStyle(e.method)"
                >
                  {{ e.method }}
                </span>
              </td>
              <td class="p-4 py-4">
                <div class="flex flex-col">
                  <span class="text-sm font-bold text-white tracking-tight group-hover:text-brand-accent transition-colors font-mono">{{ e.endpoint }}</span>
                  <span v-if="e.is_shadow" class="text-[7px] font-mono text-brand-danger uppercase tracking-widest animate-pulse mt-1">Unauthorized Access</span>
                </div>
              </td>
              <td class="p-4 py-4 text-center">
                <span class="text-sm font-bold font-mono text-gray-600">{{ e.count }}</span>
              </td>
              <td class="p-4 py-4">
                <span class="text-[9px] font-mono text-gray-600 uppercase tracking-widest">
                  {{ e.last_seen ? formatTime(e.last_seen) : 'NULL' }}
                </span>
              </td>
              <td class="p-4 py-4 last:pr-6">
                <div class="flex items-center gap-2">
                  <component :is="e.is_shadow ? AlertTriangle : CheckCircle2" 
                    class="w-3.5 h-3.5" 
                    :class="e.is_shadow ? 'text-brand-danger' : 'text-brand-success'" 
                  />
                  <span class="text-[9px] font-mono uppercase tracking-widest" :class="e.is_shadow ? 'text-brand-danger' : 'text-brand-success'">
                    {{ e.is_shadow ? 'SHADOW' : 'NOMINAL' }}
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- AI Copilot Floating Chat (Industrial Style) -->
    <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3 pointer-events-none">
      <transition 
        enter-active-class="duration-300 ease-out" 
        enter-from-class="opacity-0 scale-95 translate-y-4" 
        enter-to-class="opacity-100 scale-100 translate-y-0"
        leave-active-class="duration-200 ease-in"
      >
        <div v-if="showChat" class="w-[360px] h-[500px] bg-[#0B0C0E] rounded-2xl shadow-2xl border border-white/10 flex flex-col overflow-hidden pointer-events-auto">
          <!-- Chat Header -->
          <div class="p-5 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-lg bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center relative shadow-inner">
                <span class="text-lg">🌽</span>
                <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-brand-success rounded-full border-2 border-black"></span>
              </div>
              <div>
                <h3 class="text-xs font-bold text-white tracking-tight">GENERAL KUKURICA</h3>
                <p class="text-[8px] font-mono text-brand-success uppercase tracking-widest mt-0.5">Industrial AI // ONLINE</p>
              </div>
            </div>
            <button @click="showChat = false" class="p-1.5 rounded-lg text-gray-600 hover:text-white transition-all">
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Messages Area -->
          <div ref="messageBox" class="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar bg-black/40">
            <div v-for="(msg, mIdx) in chatHistory" :key="mIdx" 
              class="flex flex-col gap-1.5"
              :class="msg.role === 'user' ? 'items-end' : 'items-start'"
            >
              <div class="p-3.5 rounded-xl text-[12px] leading-relaxed max-w-[90%] font-medium"
                :class="msg.role === 'user' 
                  ? 'bg-white text-black rounded-tr-none' 
                  : 'bg-white/5 border border-white/5 text-gray-200 rounded-tl-none font-mono'"
              >
                {{ msg.content }}
              </div>
              <span class="text-[7px] font-mono text-gray-600 uppercase tracking-widest px-1">
                {{ msg.role === 'user' ? 'SESSION_USER' : 'NODE_KUKURICA' }}
              </span>
            </div>

            <div v-if="isTyping" class="flex gap-1.5 items-center p-2 opacity-30">
               <div class="w-1 h-1 bg-white rounded-full animate-bounce"></div>
               <div class="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:0.1s]"></div>
               <div class="w-1 h-1 bg-white rounded-full animate-bounce [animation-delay:0.2s]"></div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="p-4 border-t border-white/5 bg-white/[0.01]">
            <form @submit.prevent="sendChatMessage" class="relative">
              <input 
                v-model="newMessage"
                placeholder="Príkaz..." 
                class="w-full bg-white/5 border border-white/5 rounded-xl py-3 pl-4 pr-12 text-[12px] font-mono text-white placeholder-gray-700 outline-none focus:border-brand-accent/40 transition-all shadow-inner"
              />
              <button 
                type="submit"
                :disabled="!newMessage.trim() || isTyping"
                class="absolute right-1.5 top-1.5 bottom-1.5 w-9 h-9 rounded-lg bg-brand-accent text-black flex items-center justify-center transition-all hover:scale-105 active:scale-95 disabled:opacity-10"
              >
                <Send class="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      </transition>

      <!-- Toggle Button -->
      <button 
        @click="showChat = !showChat"
        class="w-14 h-14 rounded-2xl bg-brand-accent text-black flex items-center justify-center shadow-xl hover:scale-110 active:scale-90 transition-all pointer-events-auto border-2 border-black relative group"
      >
        <transition mode="out-in">
          <MessageSquare v-if="!showChat" class="w-6 h-6" />
          <X v-else class="w-6 h-6" />
        </transition>
        <span class="absolute -top-1 -right-1 w-4 h-4 bg-brand-success rounded-full border-2 border-black shadow-lg"></span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  Radio, ShieldAlert, ShieldCheck, Database, Search, 
  RefreshCcw, AlertTriangle, CheckCircle2, Zap,
  MessageSquare, X, Send
} from 'lucide-vue-next';
import api from '../api/api';
import { nextTick } from 'vue';

const data = ref(null);
const loading = ref(false);
const scanning = ref(false);
const seeding = ref(false);
const showShadowOnly = ref(false);
const toast = ref('');
const showChat = ref(false);
const newMessage = ref('');
const isTyping = ref(false);
const chatHistory = ref([]);
const messageBox = ref(null);
const activeDomain = ref('nexify-studio.tech'); // Predvolená doména pre kontext

let toastTimer = null;
const showToast = (msg) => {
  toast.value = msg;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.value = ''; }, 3000);
};

const fetchEndpoints = async () => {
  loading.value = true;
  try {
    const res = await api.get('/radar/endpoints');
    data.value = res.data;
  } catch {
    showToast('Chyba pri nadväzovaní spojenia.');
  } finally {
    loading.value = false;
  }
};

const scan = async () => {
  scanning.value = true;
  try {
    const res = await api.post('/radar/scan');
    showToast(`Skenovanie hotové — ${res.data.scanned} endpointov.`);
    await fetchEndpoints();
  } catch {
    showToast('Chyba pri skenovaní.');
  } finally {
    scanning.value = false;
  }
};

const seed = async () => {
  seeding.value = true;
  try {
    const res = await api.post('/radar/seed');
    showToast(`Seed hotový — ${res.data.added} pridaných.`);
    await fetchEndpoints();
  } catch {
    showToast('Chyba pri seedovaní.');
  } finally {
    seeding.value = false;
  }
};

const filteredEndpoints = computed(() => {
  if (!data.value?.endpoints) return [];
  if (showShadowOnly.value) return data.value.endpoints.filter(e => e.is_shadow);
  return data.value.endpoints;
});

const methodStyle = (method) => ({
  'GET':    'bg-primary-indigo/10 text-primary-indigo border-primary-indigo/30',
  'POST':   'bg-accent-green/10 text-accent-green border-accent-green/30',
  'DELETE': 'bg-accent-rose/10 text-accent-rose border-accent-rose/30',
  'PUT':    'bg-primary-cyan/10 text-primary-cyan border-primary-cyan/30',
  'PATCH':  'bg-white/5 text-white border-white/20',
}[method] || 'bg-white/5 text-white/30 border-white/10');

const formatTime = (ts) => new Date(ts).toLocaleString('sk-SK', {
  day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
});

const scrollToBottom = async () => {
  await nextTick();
  if (messageBox.value) {
    messageBox.value.scrollTop = messageBox.value.scrollHeight;
  }
};

const sendChatMessage = async () => {
  if (!newMessage.value.trim() || isTyping.value) return;

  const userQuery = newMessage.value;
  chatHistory.value.push({ role: 'user', content: userQuery });
  newMessage.value = '';
  isTyping.value = true;
  await scrollToBottom();

  try {
    const res = await api.post('/ai/chat', {
      query: userQuery,
      domain: activeDomain.value,
      history: chatHistory.value.slice(-6) // Posielame posledných 6 správ pre kontext
    });
    
    chatHistory.value.push({ role: 'assistant', content: res.data.response });
  } catch (err) {
    chatHistory.value.push({ 
      role: 'assistant', 
      content: 'Ups, šéfe! Zdá sa, že moje kukuričné obvody majú nejaký skrat. Skúste to o chvíľu neskôr! 🌽🔧' 
    });
  } finally {
    isTyping.value = false;
    await scrollToBottom();
  }
};

onMounted(fetchEndpoints);
</script>

<style scoped>
.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translate(-50%, 20px) scale(0.9); }

table th, table td {
  white-space: nowrap;
}
</style>
