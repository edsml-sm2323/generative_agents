<template>
  <div class="experiment-list">
    <div v-for="exp in experiments" :key="exp.id"  class="experiment-card">
      <h3>{{ exp.name  }}</h3>
      <p>{{ exp.description  }}</p>
      <div class="status-indicator" :class="exp.status"></div> 
      <button @click="selectExperiment(exp)">查看详情</button>
    </div>
    <button @click="openCreateForm">创建新实验</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useExperimentStore } from '@/stores/experimentStore'

const store = useExperimentStore()
const experiments = ref([])

const loadExperiments = async () => {
  experiments.value  = await store.fetchExperiments() 
}

// 初始化加载
loadExperiments()
</script>