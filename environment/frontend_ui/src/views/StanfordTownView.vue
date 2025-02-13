<template>
  <div class="stanford-town-view">
    <!-- 项目介绍板块 -->
    <section class="project-intro">
      <h1 class="title">
        <span class="title-icon">🌐</span>
        斯坦福小镇模拟平台 
        <span class="beta-tag">Beta</span>
      </h1>
      <div class="intro-content">
        <feature-card class="text-section">
          <template #icon>📌</template>
          <h3>平台特性</h3>
          <ul class="feature-list">
            <li v-for="(feature, index) in features" :key="index">
              <span class="feature-icon">{{ feature.icon  }}</span>
              {{ feature.text  }}
            </li>
          </ul>
        </feature-card>

        <quick-start-card @create="showCreationForm = true" />
      </div>
    </section>

    <!-- 主功能面板 -->
    <div class="main-panel">
      <!-- 左侧实验管理 -->
      <div class="management-section">
        <experiment-list 
          :selected-id="selectedExperimentId"
          @select-experiment="handleSelectExperiment"
          @create-new="showCreationForm = true"
          class="experiment-list"
        />

        <transition name="slide-up">
          <experiment-control 
            v-if="selectedExperimentId"
            :experiment-id="selectedExperimentId"
            class="control-section"
            @error="handleControlError"
          />
        </transition>

        <button class="default" @click="showCreationForm = true">
          创建新实验
        </button>
      </div>

      <!-- 右侧可视化区域 -->
      <div class="visualization-section">
        <template v-if="selectedExperimentId">
          <div class="simulation-container">
            <experiment-player 
              :key="playerKey"
              :experiment-id="selectedExperimentId"
              class="player-wrapper"
              @loading-change="handlePlayerLoading"
            />

            <experiment-data-panel 
              :experiment-id="selectedExperimentId"
              :loading="playerLoading"
              class="data-panel"
            />
          </div>
        </template>
        <empty-state v-else />
      </div>
    </div>

    <!-- 实验创建模态框 -->
    <experiment-form-modal 
      v-model="showCreationForm"
      :loading="creatingExperiment"
      @submit="handleFormSubmit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useExperimentStore } from '@/stores/experimentStore'
import {useNotification} from '@/utils/helpers'
import QuickStartCard from '@/components/QuickStartCard.vue'
import ExperimentList from '@/components/ExperimentList.vue'
import ExperimentControl from '@/components/ExperimentControl.vue'
import ExperimentFormModal from '@/components/ExperimentFormModal.vue'
import ExperimentPlayer from '@/components/ExperimentPlayer.vue'
import ExperimentDataPanel from '@/components/ExperimentDataPanel.vue'
 
const { showError } = useNotification()

const store = useExperimentStore()

// 响应式状态 
const selectedExperimentId = ref(null)
const showCreationForm = ref(false)
const creatingExperiment = ref(false)
const playerLoading = ref(true)
const playerKey = ref(0)

// 平台特性列表 
const features = ref([
  { icon: '🤖', text: '支持25+智能体并行交互' },
  { icon: '🌍', text: '三维可视化环境构建' },
  { icon: '📈', text: '实时数据监控与预测分析' },
  { icon: '🔍', text: '实验过程追溯与回放' }
])

// 计算属性 
const hasExperiments = computed(() => store.experiments.length  > 0)

// 生命周期钩子 
onMounted(async () => {
  try {
    await store.fetchExperiments() 
    if (hasExperiments.value)  {
      selectedExperimentId.value  = store.currentExperimentId  
    }
  } catch (error) {
    showError('初始化失败', error.message) 
  }
})

// 事件处理 
const handleSelectExperiment = async (id) => {
  try {
    selectedExperimentId.value  = id 
    await store.loadExperimentDetails(id) 
    playerKey.value++  // 强制重新加载播放器 
  } catch (error) {
    showError('加载实验失败', error.message) 
  }
}

const handleFormSubmit = async (formData) => {
  try {
    creatingExperiment.value  = true 
    const newId = await store.createExperiment(formData) 
    selectedExperimentId.value  = newId 
    showCreationForm.value  = false 
  } catch (error) {
    showError('创建失败', error.message) 
  } finally {
    creatingExperiment.value  = false 
  }
}

const handleControlError = (error) => {
  showError('控制指令错误', error.message) 
}

const handlePlayerLoading = (loading) => {
  playerLoading.value  = loading 
}
</script>

<style scoped>
.stanford-town-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8fafc;
  overflow: hidden;
}

.project-intro {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border-bottom: 1px solid #e2e8f0;
}

.title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #1e293b;
  font-size: 1.75rem;
  margin-bottom: 1.5rem;

  .title-icon {
    font-size: 1.2em;
  }

  .beta-tag {
    background: #3b82f6;
    color: white;
    font-size: 0.6em;
    padding: 0.2em 0.6em;
    border-radius: 1em;
    margin-left: 0.5em;
  }
}

.intro-content {
  display: grid;
  grid-template-columns: minmax(300px, 2fr) minmax(250px, 1fr);
  gap: 2rem;
}

.main-panel {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(300px, 320px) 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow: hidden;
}

.management-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.visualization-section {
  position: relative;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  overflow: hidden;
}

.simulation-container {
  display: grid;
  grid-template-rows: minmax(400px, 65vh) minmax(200px, 35vh);
  height: calc(100vh - 240px);
  gap: 1rem;
}

.player-wrapper {
  border-radius: 0.5rem;
  overflow: hidden;
  background: #1e1e2d;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.data-panel {
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

/* 过渡动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s ease-out;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@media (max-width: 1024px) {
  .main-panel {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .simulation-container {
    grid-template-rows: 60vh auto;
    height: auto;
  }
}
</style>