<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 40 40"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="gk-icon"
  >
    <defs>
      <radialGradient id="gkBg" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#1a3a0a" />
        <stop offset="100%" stop-color="#050e03" />
      </radialGradient>
      <radialGradient id="gkGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#00ff41" stop-opacity="0.3" />
        <stop offset="100%" stop-color="#00ff41" stop-opacity="0" />
      </radialGradient>
    </defs>

    <!-- Outer pulse ring -->
    <circle cx="20" cy="20" r="19" fill="url(#gkGlow)" class="pulse-ring" />

    <!-- Background circle -->
    <circle
      cx="20" cy="20" r="18"
      fill="url(#gkBg)"
      stroke="#00e040"
      stroke-width="0.8"
      stroke-opacity="0.55"
    />

    <!-- Rotating orbit ellipse -->
    <ellipse
      cx="20" cy="20" rx="13.5" ry="4.5"
      stroke="#00e040" stroke-width="0.6"
      stroke-opacity="0.35" fill="none"
      stroke-dasharray="3 2.5"
      class="orbit"
    />

    <!-- Corn cob + leaves (floating) -->
    <g class="corn-float">
      <!-- Husk leaves -->
      <path d="M16.5 14.5 Q12.5 10.5 13.5 7.5 Q17 12 16.5 14.5Z" fill="#00e040" opacity="0.75" />
      <path d="M23.5 14.5 Q27.5 10.5 26.5 7.5 Q23 12 23.5 14.5Z" fill="#00e040" opacity="0.75" />

      <!-- Cob body -->
      <rect x="16.5" y="12.5" width="7" height="13.5" rx="3.5" fill="#aaff00" opacity="0.92" />

      <!-- Corn kernels (3 rows × 2 cols) -->
      <circle cx="18.2" cy="15.5" r="1.05" fill="#1a4a00" opacity="0.75" />
      <circle cx="21.8" cy="15.5" r="1.05" fill="#1a4a00" opacity="0.75" />
      <circle cx="18.2" cy="18.5" r="1.05" fill="#1a4a00" opacity="0.75" />
      <circle cx="21.8" cy="18.5" r="1.05" fill="#1a4a00" opacity="0.75" />
      <circle cx="18.2" cy="21.5" r="1.05" fill="#1a4a00" opacity="0.75" />
      <circle cx="21.8" cy="21.5" r="1.05" fill="#1a4a00" opacity="0.75" />

      <!-- Silk threads -->
      <line x1="19.2" y1="12.5" x2="18.4" y2="9"   stroke="#ccff33" stroke-width="0.55" opacity="0.65" />
      <line x1="20"   y1="12.5" x2="20"   y2="8.2"  stroke="#ccff33" stroke-width="0.55" opacity="0.65" />
      <line x1="20.8" y1="12.5" x2="21.6" y2="9"   stroke="#ccff33" stroke-width="0.55" opacity="0.65" />
    </g>

    <!-- Online status dot (top-right, pulsing) -->
    <circle cx="29" cy="11" r="2.8" fill="#020c02" />
    <circle cx="29" cy="11" r="2.2" fill="#00ff41">
      <animate attributeName="opacity" values="1;0.35;1" dur="1.8s" repeatCount="indefinite" />
    </circle>
  </svg>
</template>

<script setup>
defineProps({
  size: { type: Number, default: 32 },
});
</script>

<style scoped>
.gk-icon {
  display: inline-block;
  flex-shrink: 0;
}

/* Outer glow pulse */
.pulse-ring {
  transform-origin: 20px 20px;
  animation: gk-pulse 2.6s ease-in-out infinite;
}
@keyframes gk-pulse {
  0%, 100% { transform: scale(0.92); opacity: 0.35; }
  50%       { transform: scale(1.1);  opacity: 1; }
}

/* Orbit ring slow spin */
.orbit {
  transform-origin: 20px 20px;
  animation: gk-spin 9s linear infinite;
}
@keyframes gk-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* Corn floating up-down */
.corn-float {
  transform-origin: 20px 19px;
  animation: gk-float 2.4s ease-in-out infinite;
}
@keyframes gk-float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-1.8px); }
}
</style>
