<script setup>
const props = defineProps({
  aiAuditResult: { type: Object, default: null },
  auditedDomain: { type: String, default: '' },
  fixingIndex: { type: Number, default: -1 }
});

const emit = defineEmits(['close', 'apply-fix']);

const scoreColor = (s) => {
  if (s > 80) return 'var(--color-primary-indigo)';
  if (s > 50) return 'var(--color-warning)';
  return 'var(--color-accent-rose)';
};
</script>

<template>
  <div v-if="aiAuditResult" class="ai-panel glass-panel rounded-[40px] p-1 border-primary-indigo/30 bg-primary-indigo/5 mb-8 animate-in slide-in-from-top-4 duration-700 relative overflow-hidden shadow-2xl">
    <div class="absolute inset-0 bg-gradient-to-br from-primary-indigo/10 to-transparent pointer-events-none"></div>
    
    <div class="p-8 space-y-8 relative z-10">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-2xl animate-pulse">✨</div>
          <div>
            <h3 class="text-2xl font-black text-white tracking-tighter leading-none mb-1.5 uppercase">AI Sentinel Hub</h3>
            <p class="text-[10px] font-bold text-white/40 uppercase tracking-[0.3em] leading-none">Vektorová Analýza • {{ auditedDomain }}</p>
          </div>
        </div>
        <button @click="emit('close')" class="w-10 h-10 flex items-center justify-center rounded-xl bg-white/5 border border-white/5 text-white/40 hover:text-white transition-all active:scale-95 outline-none">✕</button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-[200px_1fr] gap-10">
        <!-- Score section -->
        <div class="flex flex-col items-center gap-6 p-8 glass-panel rounded-[32px] bg-white/[0.03] shadow-inner">
          <div class="relative group">
            <div class="w-32 h-32 rounded-full border-[6px] border-white/5 flex flex-col items-center justify-center transition-all duration-700 group-hover:scale-110 shadow-2xl" :style="{ borderColor: scoreColor(aiAuditResult.score) }">
              <span class="text-4xl font-black text-white tracking-tighter">{{ aiAuditResult.score }}</span>
              <span class="text-[9px] font-bold text-white/30 uppercase tracking-widest mt-1">Health</span>
            </div>
            <div class="absolute -inset-4 bg-white/5 blur-2xl rounded-full -z-10 group-hover:bg-primary-indigo/10 transition-all"></div>
          </div>
          <div class="space-y-3 w-full">
            <p v-for="(issue, i) in aiAuditResult.issues" :key="i" class="text-[10px] font-bold text-accent-rose bg-accent-rose/5 border border-accent-rose/10 p-2 rounded-xl text-center shadow-sm">
              {{ issue }}
            </p>
          </div>
        </div>

        <!-- Recommendations Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="(rec, i) in aiAuditResult.recommendations" :key="i" class="glass-card p-6 rounded-[28px] border-white/5 flex flex-col gap-4 shadow-xl">
            <div class="flex items-center justify-between">
              <span class="px-3 py-1 rounded-lg bg-primary-indigo/10 text-primary-indigo border border-primary-indigo/20 text-[10px] font-black uppercase tracking-widest">{{ rec.type }}</span>
              <span v-if="rec.is_fixable" class="text-[9px] font-bold text-primary-cyan uppercase tracking-widest flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-primary-cyan animate-pulse"></span> Auto-Fix Ready
              </span>
            </div>
            <p class="text-sm text-white/70 font-medium leading-relaxed italic">"{{ rec.reason }}"</p>
            <div class="bg-black/40 p-4 rounded-xl border border-white/5 shadow-inner">
               <code class="text-[10px] font-bold text-primary-cyan/70 tracking-tight break-all">{{ rec.name }} IN {{ rec.type }} {{ rec.content }}</code>
            </div>
            <button 
              v-if="rec.is_fixable" 
              @click="emit('apply-fix', rec)" 
              class="w-full mt-auto py-3 rounded-xl bg-white text-slate-950 font-black text-[10px] uppercase tracking-widest shadow-xl hover:translate-y-[-2px] active:translate-y-[0px] transition-all disabled:opacity-50"
              :disabled="fixingIndex === i"
            >
              {{ fixingIndex === i ? 'Injektáž...' : 'Aplikovať AI Opravu' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
