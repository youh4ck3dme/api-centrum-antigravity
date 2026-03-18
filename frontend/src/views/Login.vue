<template>
  <div class="login-root bg-slate-950 flex items-center justify-center p-6 relative overflow-hidden">
    <!-- Atmospheric Ambient Glow -->
    <div class="absolute top-[-10%] right-[-10%] w-[60%] h-[60%] bg-primary-indigo/10 blur-[120px] rounded-full animate-pulse-slow"></div>
    <div class="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary-cyan/10 blur-[100px] rounded-full animate-pulse-slow" style="animation-delay: -2s"></div>
    
    <!-- Central Mesh Grid -->
    <div class="absolute inset-0 opacity-20 pointer-events-none" style="background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.05) 1px, transparent 0); background-size: 40px 40px;"></div>

    <div class="main-card glass-panel w-full max-w-[460px] p-10 lg:p-12 rounded-[48px] shadow-2xl relative z-10 animate-in fade-in zoom-in-95 duration-1000">
      <!-- Logo section -->
      <div class="flex flex-col items-center mb-12">
        <div class="w-20 h-20 p-4 bg-white/5 border border-white/10 rounded-[28px] shadow-2xl mb-6 group hover:scale-110 transition-transform duration-500">
          <img src="/pwa-192x192.png" alt="Logo" class="w-full h-full object-contain filter drop-shadow-2xl" />
        </div>
        <h1 class="text-4xl font-black text-white tracking-tighter leading-none mb-2">API CENTRUM</h1>
        <p class="text-[10px] font-black text-white/30 uppercase tracking-[0.4em]">Nexus Control Interface v4.0</p>
      </div>

      <!-- Avatar selection (Polish) -->
      <div class="relative flex justify-center mb-10">
        <button 
          @click="showPicker = !showPicker"
          class="w-20 h-20 rounded-full glass-card border border-white/10 flex items-center justify-center text-4xl shadow-2xl hover:scale-110 active:scale-95 transition-all relative group"
        >
          <div class="absolute inset-0 bg-primary-indigo/10 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <span class="relative z-10">{{ currentAvatar }}</span>
        </button>
        
        <transition 
          enter-active-class="transition duration-400 ease-[cubic-bezier(0.16,1,0.3,1)]"
          enter-from-class="transform scale-95 opacity-0 -translate-y-4"
          enter-to-class="transform scale-100 opacity-100 translate-y-0"
          leave-active-class="transition duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
          leave-from-class="transform scale-100 opacity-100 translate-y-0"
          leave-to-class="transform scale-95 opacity-0 -translate-y-4"
        >
          <div v-if="showPicker" class="absolute top-24 z-50 glass-panel p-4 grid grid-cols-4 gap-3 rounded-3xl shadow-2xl border border-white/10 backdrop-blur-3xl">
            <button
              v-for="e in AVATARS"
              :key="e"
              @click="selectAvatar(e)"
              class="w-12 h-12 flex items-center justify-center text-2xl rounded-2xl hover:bg-white/10 transition-all hover:scale-110 active:scale-90"
              :class="{ 'bg-primary-indigo/20 border border-primary-indigo/30 shadow-lg': currentAvatar === e }"
            >
              {{ e }}
            </button>
          </div>
        </transition>
      </div>

      <form @submit.prevent="login" class="space-y-6">
        <!-- Email Input -->
        <div class="space-y-2">
          <label class="text-[10px] font-black text-white/30 uppercase tracking-[0.3em] ml-2">Access Identifier</label>
          <div class="relative group">
            <Mail class="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 group-focus-within:text-primary-cyan transition-colors" />
            <input
              v-model="email"
              type="email"
              required
              class="w-full bg-slate-950/50 border border-white/10 rounded-2xl py-4.5 pl-14 pr-5 text-white placeholder-white/10 outline-none focus:border-primary-cyan/50 focus:ring-1 focus:ring-primary-cyan/20 transition-all shadow-inner font-medium text-sm"
              placeholder="vasho@meno.com"
            />
          </div>
        </div>

        <!-- Password Input -->
        <div class="space-y-2">
          <label class="text-[10px] font-black text-white/30 uppercase tracking-[0.3em] ml-2">Encrypted Sequence</label>
          <div class="relative group">
            <Lock class="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 group-focus-within:text-primary-indigo transition-colors" />
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              class="w-full bg-slate-950/50 border border-white/10 rounded-2xl py-4.5 pl-14 pr-14 text-white placeholder-white/10 outline-none focus:border-primary-indigo/50 focus:ring-1 focus:ring-primary-indigo/20 transition-all shadow-inner font-password tracking-widest text-sm"
              placeholder="••••••••"
            />
            <button 
              type="button" 
              @click="showPassword = !showPassword"
              class="absolute right-5 top-1/2 -translate-y-1/2 text-white/10 hover:text-white transition-colors outline-none"
            >
              <Eye v-if="!showPassword" class="w-4 h-4" />
              <EyeOff v-else class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Error Feedback -->
        <transition 
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="transform -translate-y-2 opacity-0"
          enter-to-class="transform translate-y-0 opacity-100"
        >
          <div v-if="error" class="bg-accent-rose/10 border border-accent-rose/20 rounded-2xl p-4 flex items-start gap-4 shadow-lg">
            <AlertCircle class="w-5 h-5 text-accent-rose mt-0.5 shrink-0" />
            <span class="text-xs text-rose-100/70 font-bold leading-relaxed">{{ error }}</span>
          </div>
        </transition>

        <!-- Login Button -->
        <button 
          type="submit" 
          :disabled="loading" 
          class="w-full py-5 bg-white text-slate-950 font-black text-xs uppercase tracking-[0.2em] rounded-2xl shadow-2xl hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100 transition-all flex items-center justify-center gap-3 relative overflow-hidden group mt-4"
        >
          <div v-if="!loading" class="flex items-center gap-2 relative z-10 font-black">
            Authorize Entry
            <ArrowRight class="w-4 h-4 group-hover:translate-x-1.5 transition-transform duration-500" />
          </div>
          <div v-else class="flex items-center gap-3 relative z-10 font-black">
            <RefreshCcw class="w-4 h-4 animate-spin" />
            Decrypting...
          </div>
          <!-- Shimmer -->
          <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-[200%] group-hover:animate-shimmer-fast"></div>
        </button>
      </form>

      <!-- Footer Info -->
      <footer class="mt-12 pt-8 border-t border-white/5 flex flex-col items-center gap-6">
        <div class="flex items-center gap-3 px-4 py-2 rounded-full bg-white/[0.03] border border-white/5">
          <ShieldCheck class="w-3.5 h-3.5 text-accent-green shadow-accent-green" />
          <span class="text-[9px] font-black text-white/20 uppercase tracking-[0.2em]">Quant-Cipher Protection: Active</span>
        </div>
        <div class="flex items-center gap-4 text-[9px] font-black text-white/10 uppercase tracking-widest">
           <span class="h-px w-8 bg-white/5"></span>
           Nexify Studio OS © 2026
           <span class="h-px w-8 bg-white/5"></span>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Mail, Lock, Eye, EyeOff, ArrowRight, AlertCircle, ShieldCheck, RefreshCcw } from 'lucide-vue-next';
import api from '../api/api';

const emit = defineEmits(['logged-in']);

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const showPassword = ref(false);

const AVATARS = ['🦊', '🐺', '🤖', '🦅', '⚡', '🔥', '🎯', '🦁', '🐉', '🌙', '🧬', '🔮'];
const showPicker = ref(false);
const savedAvatar = localStorage.getItem('user-avatar');
const currentAvatar = ref(savedAvatar && AVATARS.includes(savedAvatar) ? savedAvatar : AVATARS[0]);

function selectAvatar(e) {
  currentAvatar.value = e;
  localStorage.setItem('user-avatar', e);
  showPicker.value = false;
}

const login = async () => {
  error.value = '';
  loading.value = true;
  try {
    const res = await api.post('/auth/login', { email: email.value, password: password.value });
    localStorage.setItem('access_token', res.data.access_token);
    emit('logged-in');
  } catch (err) {
    error.value = err.response?.data?.detail || 'Prihlásenie zlyhalo. Skontrolujte prístupové tokeny.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.animate-pulse-slow {
  animation: pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.15; transform: scale(1); }
  50% { opacity: 0.25; transform: scale(1.1); }
}
</style>
