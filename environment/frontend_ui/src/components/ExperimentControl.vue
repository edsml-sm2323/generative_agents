<template>
  <div class="control-panel">
    <div class="status-display">
      当前状态: {{ currentExperiment.status  }}
      <span v-if="isRunning" class="running-badge">运行中</span>
    </div>
    
    <div class="action-buttons">
      <button 
        @click="startExperiment"
        :disabled="!canStart"
      >启动实验</button>
      
      <button 
        @click="stopExperiment"
        :disabled="!isRunning"
      >终止实验</button>
    </div>

    <div v-if="showProgress" class="progress-bar">
      <progress :value="progress" max="100"></progress>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useExperimentStore } from '@/stores/experimentStore'

const store = useExperimentStore()

const currentExperiment = computed(() => store.currentExperiment) 
const isRunning = computed(() => currentExperiment.value.status  === 'running')
const canStart = computed(() => ['ready', 'stopped'].includes(currentExperiment.value.status)) 
</script>