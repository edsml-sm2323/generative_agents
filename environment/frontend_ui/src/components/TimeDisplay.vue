<!-- src/components/Display/TimeDisplay.vue  -->
<template>
    <div class="time-display">
      <span class="current">{{ formattedCurrent }}</span>
      <span class="separator">/</span>
      <span class="total">{{ formattedTotal }}</span>
    </div>
  </template>
   
  <script setup>
  import { computed, defineProps } from 'vue'
   
  const props = defineProps({
    currentTime: { type: Number, default: 0 }, // 秒数 
    totalTime: { type: Number, default: 0 }
  })
   
  const formatTime = (seconds) => {
    if (!seconds) return '00:00'
    const mins = Math.floor(seconds  / 60)
    const secs = Math.floor(seconds  % 60)
    return `${mins.toString().padStart(2,  '0')}:${secs.toString().padStart(2,  '0')}`
  }
   
  const formattedCurrent = computed(() => formatTime(props.currentTime)) 
  const formattedTotal = computed(() => formatTime(props.totalTime)) 
  </script>
   
  <style scoped>
  .time-display {
    font-family: 'Fira Code', monospace;
    color: #94A3B8;
    font-size: 0.9em;
    display: flex;
    gap: 4px;
  }
   
  .separator {
    opacity: 0.6;
  }
  </style>