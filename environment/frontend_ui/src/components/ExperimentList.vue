<template>
  <div class="experiment-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载实验数据...</p>
    </div>
 
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <span class="icon">⚠️</span>
      <p>{{ error }}</p>
      <button @click="loadExperiments">重试</button>
    </div>
 
    <!-- 空状态 -->
    <div v-else-if="!experiments.length"  class="empty-state">
      <img src="@/assets/empty-experiment.png"  alt="无实验" />
      <p>暂无实验项目</p>
      <button @click="openCreateForm" class="create-button">
        + 创建第一个实验 
      </button>
    </div>
 
    <!-- 数据列表 -->
    <TransitionGroup v-else name="list" tag="div" class="experiment-grid">
      <article 
        v-for="exp in sortedExperiments"
        :key="exp.id" 
        class="experiment-card"
        :class="{ 'active': exp.id  === selectedId }"
        @click.self="selectExperiment(exp)" 
      >
        <header class="card-header">
          <h3 class="title">{{ exp.name  }}</h3>
          <span class="timestamp">{{ formatDate(exp.createdAt)  }}</span>
        </header>
        
        <div class="card-body">
          <p class="description">{{ truncate(exp.description,  100) }}</p>
          
          <div class="metadata">
            <span class="agent-count">
              👥 {{ exp.agents?.length  || 0 }}个智能体 
            </span>
            <span class="duration">
              ⏱️ {{ formatDuration(exp.duration)  }}
            </span>
          </div>
        </div>
 
        <footer class="card-footer">
          <div class="status">
            <span 
              class="status-indicator" 
              :class="exp.status" 
              :title="getStatusLabel(exp.status)" 
            ></span>
            {{ getStatusLabel(exp.status)  }}
          </div>
          <div class="actions">
            <button 
              @click.stop="selectExperiment(exp)" 
              aria-label="查看详情"
            >
              🔍 详情 
            </button>
            <button 
              @click.stop="$emit('clone',  exp)"
              v-if="exp.status  === 'completed'"
              class="clone-btn"
              aria-label="克隆实验"
            >
              ⎘ 克隆 
            </button>
          </div>
        </footer>
      </article>
    </TransitionGroup>
 
    <!-- 创建按钮 -->
    <button 
      @click="openCreateForm"
      class="create-new-button"
      v-show="!loading && !error"
    >
      <span class="plus-icon">+</span>
      创建新实验 
    </button>
  </div>
</template>
 
<script setup>
import { ref, computed, onMounted, defineProps, defineEmits, defineExpose } from 'vue'
import { useExperimentStore } from '@/stores/experimentStore'
import { formatDate, truncate, formatDuration } from '@/utils/helpers'
 
defineProps({
  selectedId: String  
})
 
defineEmits(['select-experiment', 'create-new', 'clone'])
 
const store = useExperimentStore()
const loading = ref(true)
const error = ref(null)
 
// 计算属性排序实验 
const sortedExperiments = computed(() => {
  return [...store.experiments].sort((a,  b) => 
    new Date(b.createdAt)  - new Date(a.createdAt) 
  )
})
 
// 加载实验数据 
const loadExperiments = async () => {
  try {
    loading.value  = true 
    error.value  = null 
    await store.fetchExperiments() 
  } catch (err) {
    error.value  = '数据加载失败: ' + err.message  
    console.error(' 加载错误:', err)
  } finally {
    loading.value  = false 
  }
}
 
// 状态标签映射 
const getStatusLabel = (status) => {
  const statusMap = {
    draft: '草稿',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    archived: '已归档'
  }
  return statusMap[status] || '未知状态'
}
 
// 初始化加载 
onMounted(() => {
  loadExperiments()
})
 
// 暴露公共方法 
defineExpose({ refresh: loadExperiments })
</script>
 
<style scoped>
.experiment-list {
  position: relative;
  min-height: 300px;
}
 
/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}
 
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #eee;
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
 
@keyframes spin {
  to { transform: rotate(360deg); }
}
 
/* 错误状态 */
.error-state {
  text-align: center;
  padding: 2rem;
  color: #e74c3c;
}
 
.error-state .icon {
  font-size: 2.5rem;
}
 
/* 空状态 */
.empty-state {
  text-align: center;
  padding: 2rem;
}
 
.empty-state img {
  width: 200px;
  opacity: 0.8;
  margin-bottom: 1rem;
}
 
/* 卡片网格布局 */
.experiment-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  padding: 1rem;
}
 
.experiment-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
 
.experiment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
 
.experiment-card.active  {
  border: 2px solid #3498db;
}
 
/* 卡片内部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
}
 
.title {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
}
 
.timestamp {
  font-size: 0.9rem;
  color: #7f8c8d;
}
 
.description {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.4;
  margin: 0.5rem 0;
}
 
.metadata {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 1rem 0;
}
 
/* 状态指示器 */
.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 0.5rem;
}
 
.status-indicator.draft  { background: #95a5a6; }
.status-indicator.running  { background: #2ecc71; }
.status-indicator.paused  { background: #f1c40f; }
.status-indicator.completed  { background: #3498db; }
.status-indicator.archived  { background: #e74c3c; }
 
/* 操作按钮 */
.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
 
button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: #3498db;
  color: white;
  cursor: pointer;
  transition: opacity 0.2s;
}
 
button:hover {
  opacity: 0.9;
}
 
.clone-btn {
  background: #2ecc71;
}
 
.create-new-button {
  margin: 2rem auto;
  display: block;
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
}
 
.plus-icon {
  margin-right: 0.5rem;
}
 
/* 过渡动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
 
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style>