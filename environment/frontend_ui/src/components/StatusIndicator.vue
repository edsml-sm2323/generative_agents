<!-- StatusIndicator.vue  -->
<template>
    <span class="status-indicator" :class="status">
      <span class="status-dot"></span>
      {{ statusLabel }}
    </span>
</template>
   
<script setup>
import { props, defineProps } from 'vue'

defineProps({
  status: {
    type: String,
    validator: value => ['active', 'idle', 'error'].includes(value),
    default: 'idle'
  }
})
 
const statusLabel = {
  active: '运行中',
  idle: '待机',
  error: '异常'
}[props.status]
</script>
 
<style scoped>
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
}
 
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}
 
.active { color: #4caf50; }
.idle { color: #ffc107; }
.error { color: #f44336; }
</style>