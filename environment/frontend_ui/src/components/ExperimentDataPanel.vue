<template>
  <div class="data-panel">
    <!-- 头部控制栏 -->
    <div class="panel-header">
      <h3 class="title">实验数据监控 - {{ experimentId }}</h3>
      <div class="controls">
        <button 
          class="refresh-btn"
          @click="fetchData"
          :disabled="loading"
        >
          <span v-if="!loading">🔄 刷新</span>
          <span v-else>🔃 更新中...</span>
        </button>
        <label class="realtime-toggle">
          <input 
            type="checkbox"
            v-model="realtimeEnabled"
          >
          实时模式 ({{ refreshInterval }}s)
        </label>
      </div>
    </div>

    <!-- 状态提示 -->
    <div class="status-message">
      <transition name="fade">
        <div 
          v-if="errorMessage"
          class="error-banner"
        >
          ❗ {{ errorMessage }}
        </div>
      </transition>
    </div>

    <!-- 数据展示区 -->
    <div class="data-container">
      <transition name="fade" mode="out-in">
        <div :key="loading ? 'loading' : 'content'">
        <div v-if="loading" class="loading-indicator">
          <div class="loader"></div>
          <p>正在获取实验数据...</p>
        </div>

        <template v-else>
          <!-- 数据可视化卡片 -->
          <div class="data-card">
            <h4>智能体状态概览</h4>
            <div class="agent-grid">
              <div 
                v-for="agent in agents"
                :key="agent.id" 
                class="agent-card"
                @click="toggleDetails(agent)"
              >
                <div class="agent-header">
                  <span class="agent-id">#{{ agent.id  }}</span>
                  <status-indicator :status="agent.status"  />
                </div>
                <div class="position-info">
                  <span class="coordinate">X: {{ agent.position.x  }}</span>
                  <span class="coordinate">Y: {{ agent.position.y  }}</span>
                </div>
                <transition name="slide">
                  <div 
                    v-if="expandedAgent === agent.id" 
                    class="agent-details"
                  >
                    <div class="detail-item">
                      <label>动作状态:</label>
                      <span class="action-badge">{{ agent.action  }}</span>
                    </div>
                    <div class="detail-item">
                      <label>传感器数据:</label>
                      <pre>{{ agent.sensors  }}</pre>
                    </div>
                  </div>
                </transition>
              </div>
            </div>
          </div>

          <!-- 原始数据面板 -->
          <div class="raw-data">
            <div class="data-toolbar">
              <button 
                class="toggle-raw"
                @click="showRawData = !showRawData"
              >
                {{ showRawData ? '隐藏' : '显示' }}原始数据 
              </button>
            </div>
            <transition name="slide">
              <vue-json-pretty 
                v-if="showRawData"
                :data="experimentData"
                :deep="2"
                class="json-viewer"
              />
            </transition>
          </div>
        </template>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted, defineProps } from 'vue'
import VueJsonPretty from 'vue-json-pretty'
import 'vue-json-pretty/lib/styles.css' 

const props = defineProps({
  experimentId: {
    type: String,
    required: true,
    validator: id => /^EXP-\d{4}-\d{4}$/.test(id)
  },
  refreshInterval: {
    type: Number,
    default: 5,
    validator: value => value >= 1 && value <= 60 
  }
})

// 响应式状态 
const loading = ref(false)
const errorMessage = ref(null)
const experimentData = ref(null)
const realtimeEnabled = ref(false)
const showRawData = ref(false)
const expandedAgent = ref(null)
let refreshTimer = null 

// 计算属性 
const agents = computed(() => 
  experimentData.value?.agents?.map(agent  => ({
    ...agent,
    status: calculateStatus(agent)
  })) || []
)

// 生命周期 
onUnmounted(() => clearInterval(refreshTimer))

// 监听实验ID变化 
watch(() => props.experimentId,  (newId) => {
  if (newId) {
    resetState()
    fetchData()
  }
}, { immediate: true })

// 实时模式监听 
watch(realtimeEnabled, (enabled) => {
  clearInterval(refreshTimer)
  if (enabled) {
    refreshTimer = setInterval(fetchData, props.refreshInterval  * 1000)
  }
})

// 方法实现 
const fetchData = async () => {
  try {
    loading.value  = true 
    errorMessage.value  = null 

    const response = await fetch(`/api/experiments/${props.experimentId}/data`) 
    if (!response.ok)  throw new Error('数据获取失败')

    experimentData.value  = await response.json() 
  } catch (err) {
    errorMessage.value  = `监控数据更新失败: ${err.message}` 
    console.error(' 数据获取错误:', err)
  } finally {
    loading.value  = false 
  }
}

const toggleDetails = (agent) => {
  expandedAgent.value  = expandedAgent.value  === agent.id  ? null : agent.id  
}

const calculateStatus = (agent) => {
  if (agent.position.x  < 0 || agent.position.y  < 0) return 'error'
  if (agent.action  === 'idle') return 'idle'
  return 'active'
}

const resetState = () => {
  experimentData.value  = null 
  expandedAgent.value  = null 
  clearInterval(refreshTimer)
}
</script>

<style scoped>
.data-panel {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.refresh-btn {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: #e9ecef;
}

.realtime-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.error-banner {
  background: #fff3f3;
  color: #dc3545;
  padding: 0.8rem;
  border-radius: 4px;
  margin: 1rem 0;
  border: 1px solid rgba(220, 53, 69, 0.3);
}

.loading-indicator {
  text-align: center;
  padding: 2rem;
}

.loader {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.agent-card {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.position-info {
  display: flex;
  gap: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.agent-details {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #eee;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.action-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.raw-data {
  margin-top: 2rem;
  border-top: 1px solid #eee;
  padding-top: 1rem;
}

.json-viewer {
  max-height: 400px;
  overflow: auto;
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active {
  transition: all 0.3s ease-out;
}

.slide-leave-active {
  transition: all 0.3s ease-in;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>