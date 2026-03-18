<script setup>
import { Globe } from 'lucide-vue-next';

const props = defineProps({
  domains: { type: Array, required: true },
  selectedDomain: { type: String, default: null }
});

const emit = defineEmits(['select']);

const formatExpiry = (ts) => {
  if (!ts) return '';
  const d = new Date(ts * 1000);
  return 'Exp: ' + d.toLocaleDateString('sk-SK');
};
</script>

<template>
  <div class="glass-panel rounded-[32px] overflow-hidden flex flex-col max-h-[calc(100vh-280px)] shadow-2xl">
    <div class="p-6 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
      <span class="text-[10px] font-bold uppercase tracking-[0.3em] text-white/20">System Infrastructure</span>
      <span class="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[9px] font-bold text-white/40">{{ domains.length }}</span>
    </div>
    <div class="overflow-y-auto custom-scrollbar divide-y divide-white/[0.03]">
        <div
          v-for="d in domains"
          :key="d.name"
          @click="$emit('select', d)"
          class="p-5 rounded-2xl cursor-pointer transition-all border flex items-center justify-between group active:scale-95"
          :class="[
            selectedDomain === d.name
              ? 'bg-primary-indigo text-white shadow-lg border-primary-indigo'
              : 'bg-white border-black/5 text-text-main hover:border-black/10 hover:shadow-sm'
          ]"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center text-lg shadow-sm"
              :class="selectedDomain === d.name ? 'bg-white/20' : 'bg-black/5 text-text-dim'"
            >
              {{ d.readonly ? '🔒' : '🌐' }}
            </div>
            <div>
              <h4 class="font-bold text-sm tracking-tight leading-none mb-1.5">{{ d.name }}</h4>
              <div class="flex items-center gap-1.5">
                <span
                  class="w-1.5 h-1.5 rounded-full"
                  :class="d.readonly ? 'bg-accent-rose' : 'bg-accent-green'"
                ></span>
                <span class="text-[8px] font-black uppercase tracking-widest opacity-40">
                  {{ d.readonly ? 'Managed' : 'Control' }}
                </span>
              </div>
            </div>
          </div>
          <ChevronRight
            class="w-4 h-4 transition-transform group-hover:translate-x-1"
            :class="selectedDomain === d.name ? 'text-white' : 'text-text-dim'"
          />
        </div>
    </div>
  </div>
</template>
