<!-- src/components/Feedback/ProgressSpinner.vue  -->
<template>
    <div 
      class="progress-spinner"
      :style="{
        width: `${size}px`,
        height: `${size}px`
      }"
      role="progressbar"
      :aria-valuenow="progress"
    >
      <svg viewBox="0 0 100 100">
        <circle 
          class="progress-track"
          cx="50"
          cy="50"
          :r="radius"
          :stroke-width="strokeWidth"
        />
        <circle 
          class="progress-indicator"
          cx="50"
          cy="50"
          :r="radius"
          :stroke-width="strokeWidth"
          :style="indicatorStyle"
        />
      </svg>
    </div>
  </template>
   
  <script setup>
  import { computed, defineProps } from 'vue'
   
  const props = defineProps({
    size: { type: Number, default: 48 },
    strokeWidth: { type: Number, default: 4 },
    progress: { type: Number, default: 0 }
  })
   
  const radius = computed(() => 50 - props.strokeWidth  / 2)
  const circumference = computed(() => 2 * Math.PI * radius.value) 
  const indicatorStyle = computed(() => ({
    strokeDasharray: circumference.value, 
    strokeDashoffset: circumference.value  * (1 - props.progress  / 100)
  }))
  </script>
   
  <style scoped>
  .progress-spinner {
    position: relative;
    animation: rotate 1.4s linear infinite;
  }
   
  @keyframes rotate {
    100% { transform: rotate(360deg); }
  }
   
  .progress-track {
    stroke: rgba(255,255,255,0.1);
    fill: none;
  }
   
  .progress-indicator {
    stroke: #3B82F6;
    fill: none;
    stroke-linecap: round;
    transition: stroke-dashoffset 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  </style>