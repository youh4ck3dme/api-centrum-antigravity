<script setup>
const props = defineProps({
  domainCount: { type: Number, default: 0 },
  threatsToday: { type: Number, default: 0 },
  lastScanLabel: { type: String, default: 'čakám...' },
  feedLength: { type: Number, default: 0 }
});
</script>

<template>
  <div class="stats-row grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div class="stat-card glass-card p-6 rounded-[32px] flex items-center gap-6">
      <div class="stat-icon w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-2xl shadow-xl">🌐</div>
      <div class="stat-body">
        <p class="stat-label text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mb-1">Monitorované domény</p>
        <p class="stat-value text-3xl font-bold text-white tracking-tighter">{{ domainCount }}</p>
      </div>
    </div>
    
    <div class="stat-card glass-card p-6 rounded-[32px] flex items-center gap-6">
      <div class="stat-icon w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-2xl shadow-xl">⚠️</div>
      <div class="stat-body">
        <p class="stat-label text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mb-1">Hrozby dnes</p>
        <p class="stat-value text-3xl font-bold tracking-tighter" :class="threatsToday > 0 ? 'text-accent-rose' : 'text-accent-green'">
          {{ threatsToday }}
        </p>
      </div>
    </div>

    <div class="stat-card glass-card p-6 rounded-[32px] flex items-center gap-6">
      <div class="stat-icon w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-2xl shadow-xl">🕐</div>
      <div class="stat-body">
        <p class="stat-label text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mb-1">Posledný scan</p>
        <p class="stat-value text-xl font-bold text-white/70 tracking-tight">{{ lastScanLabel }}</p>
      </div>
    </div>

    <div class="stat-card glass-card p-6 rounded-[32px] flex items-center gap-6">
      <div class="stat-icon w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-2xl shadow-xl">📡</div>
      <div class="stat-body">
        <p class="stat-label text-[10px] font-bold text-white/30 uppercase tracking-[0.2em] mb-1">Udalosti v logu</p>
        <p class="stat-value text-3xl font-bold text-white tracking-tighter">{{ feedLength }}</p>
      </div>
    </div>
  </div>
</template>
