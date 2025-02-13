<template>
  <div class="stanford-town-view">
    <!-- 项目介绍板块 -->
    <section class="project-intro">
      <h1 class="title">斯坦福小镇模拟平台</h1>
      <div class="intro-content">
        <div class="text-section">
          <h3>平台简介</h3>
          <p>
            本平台基于斯坦福小镇实验框架构建，支持创建多智能体社会模拟实验。主要功能包括：
          </p>
          <ul>
            <li>🔄 自定义虚拟人物属性和行为模式</li>
            <li>🗺️ 可视化地图编辑与路径规划</li>
            <li>📊 实时实验数据监控与分析</li>
            <li>🎥 实验过程回放与三维可视化</li>
          </ul>
        </div>
        <div class="quick-start">
          <h3>快速开始</h3>
          <ol>
            <li>点击"创建新实验"按钮初始化场景</li>
            <li>在右侧面板配置人物参数</li>
            <li>保存并启动实验</li>
            <li>在监控面板观察实时数据</li>
          </ol>
        </div>
      </div>
    </section>

    <!-- 主功能面板 -->
    <div class="main-panel">
      <!-- 左侧实验管理 -->
      <div class="management-section">
        <ExperimentList 
          @select-experiment="handleSelectExperiment"
          @create-new="showCreationForm = true"
        />

        <ExperimentControl 
          v-if="selectedExperimentId"
          :experiment-id="selectedExperimentId"
          class="control-section"
        />
      </div>

      <!-- 右侧可视化区域 -->
      <div class="visualization-section">
        <div v-if="selectedExperimentId" class="simulation-container">
          <ExperimentPlayer 
            :experiment-id="selectedExperimentId"
            class="player-wrapper"
          />

          <ExperimentDataPanel 
            :experiment-id="selectedExperimentId"
            class="data-panel"
          />
        </div>

        <div v-else class="empty-state">
          <img src="@/assets/select-experiment.png"  alt="请选择实验" />
          <p>请从左侧列表选择或创建新实验</p>
        </div>
      </div>
    </div>

    <!-- 实验创建模态框 -->
    <ExperimentFormModal 
      v-model="showCreationForm"
      @submit="handleFormSubmit"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useExperimentStore } from '@/stores/experimentStore'
import ExperimentList from './components/ExperimentList.vue' 
import ExperimentControl from './components/ExperimentControl.vue' 
import ExperimentPlayer from './components/ExperimentPlayer.vue' 
import ExperimentDataPanel from './components/ExperimentDataPanel.vue' 
import ExperimentFormModal from './components/ExperimentFormModal.vue' 

const store = useExperimentStore()
const selectedExperimentId = ref(null)
const showCreationForm = ref(false)

// 初始化加载实验列表 
onMounted(async () => {
  await store.fetchExperiments() 
})

const handleSelectExperiment = (id) => {
  selectedExperimentId.value  = id 
  store.setCurrentExperiment(id) 
}

const handleFormSubmit = async (formData) => {
  try {
    await store.createExperiment(formData) 
    showCreationForm.value  = false 
  } catch (error) {
    console.error(' 创建实验失败:', error)
  }
}
</script>

<style scoped>
.stanford-town-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
  background: #f5f7fa;
}

.project-intro {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.title {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 12px;
  margin-bottom: 20px;
}

.intro-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.main-panel {
  flex: 1;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
}

.management-section {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.visualization-section {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.simulation-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.player-wrapper {
  flex: 2;
  min-height: 400px;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.data-panel {
  flex: 1;
  max-height: 300px;
  overflow-y: auto;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0.6;

  img {
    width: 200px;
    margin-bottom: 20px;
  }
}
</style>