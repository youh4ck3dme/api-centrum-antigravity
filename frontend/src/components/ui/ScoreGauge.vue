<template>
  <div class="relative w-32 h-32 flex items-center justify-center">
    <!-- Background Track -->
    <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
      <circle
        class="text-neutral-800 stroke-current"
        stroke-width="8"
        cx="50"
        cy="50"
        r="40"
        fill="transparent"
      ></circle>
      <!-- Progress Bar -->
      <circle
        class="stroke-current transition-all duration-1000 ease-out"
        :class="colorClass"
        stroke-width="8"
        stroke-linecap="round"
        cx="50"
        cy="50"
        r="40"
        fill="transparent"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        style="filter: drop-shadow(0 0 8px currentColor);"
      ></circle>
    </svg>
    <!-- Score Text -->
    <div class="absolute flex flex-col items-center justify-center">
      <span class="text-3xl font-bold text-white tracking-tighter">{{ displayScore }}</span>
      <span class="text-[10px] text-neutral-400 font-medium uppercase tracking-widest">Score</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  score: {
    type: Number,
    required: true,
    default: 0
  }
});

const displayScore = ref(0);
const radius = 40;
const circumference = 2 * Math.PI * radius;

const dashOffset = computed(() => {
  return circumference - (displayScore.value / 100) * circumference;
});

const colorClass = computed(() => {
  if (props.score >= 80) return 'text-emerald-400';
  if (props.score >= 50) return 'text-amber-400';
  return 'text-rose-500';
});

const animateScore = () => {
  const duration = 1500;
  const start = 0;
  const end = props.score;
  const startTime = performance.now();

  const easeOutQuart = (x) => 1 - Math.pow(1 - x, 4);

  const update = (currentTime) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easedProgress = easeOutQuart(progress);
    
    displayScore.value = Math.round(start + (end - start) * easedProgress);

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      displayScore.value = end;
    }
  };

  requestAnimationFrame(update);
};

onMounted(() => {
  setTimeout(animateScore, 300);
});

watch(() => props.score, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    animateScore();
  }
});
</script>
