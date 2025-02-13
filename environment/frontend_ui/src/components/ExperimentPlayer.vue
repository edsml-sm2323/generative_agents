<template>
  <div class="simulation-container">
    <!-- 加载状态 -->
    <transition name="fade">
      <div 
        v-if="isLoading"
        class="loading-overlay"
      >
        <progress-spinner 
          :size="48"
          :stroke-width="3"
          :progress="loadProgress"
        />
        <span class="loading-text">播放器加载中 ({{ loadProgress }}%)</span>
      </div>
    </transition>
 
    <!-- 主播放器 -->
    <div class="simulation-wrapper">
      <iframe 
        ref="playerFrame"
        :src="playerUrl"
        frameborder="0"
        allowfullscreen 
        class="simulation-frame"
        @load="handlePlayerLoad"
      ></iframe>
 
      <!-- 控制面板 -->
      <div class="control-panel">
        <!-- 主控制区 -->
        <div class="primary-controls">
          <async-button 
            @click="togglePlayback"
            :variant="isPlaying ? 'secondary' : 'primary'"
            :title="isPlaying ? '暂停模拟' : '开始模拟'"
          >
            <template #default>
              <icon :name="isPlaying ? 'pause' : 'play'" />
            </template>
          </async-button>
 
          <time-display 
            :current-time="currentTime"
            :total-time="totalTime"
          />
        </div>
 
        <!-- 辅助控制 -->
        <div class="secondary-controls">
          <speed-control 
            v-model:playback-speed="playbackSpeed"
            class="speed-slider"
          />
          
          <button 
            class="icon-button"
            @click="toggleFullscreen"
            :title="isFullscreen ? '退出全屏' : '全屏显示'"
          >
            <icon :name="isFullscreen ? 'compress' : 'expand'" />
          </button>
        </div>
      </div>
    </div>
 
    <!-- 错误提示 -->
    <transition name="slide-up">
      <error-banner 
        v-if="errorMessage"
        :message="errorMessage"
        @close="errorMessage = null"
      />
    </transition>
  </div>
</template>
 
<script setup>
import { ref, computed, onMounted, onUnmounted, defineProps } from 'vue'
import { useFullscreen } from '@vueuse/core'
import AsyncButton from '@/components/AsyncButton.vue' 
import ErrorBanner from '@/components/ErrorBanner.vue' 
import SpeedControl from '@/components/SpeedControl.vue' 
import TimeDisplay from '@/components/TimeDisplay.vue' 
import ProgressSpinner from '@/components/ProgressSpinner.vue' 
 
const props = defineProps({
  experimentId: {
    type: String,
    required: true,
    validator: id => /^EXP-\d{4}-\d{6}$/.test(id)
  }
})
 
// 响应式状态 
const playerFrame = ref(null)
const isPlaying = ref(false)
const playbackSpeed = ref(1.0)
const isLoading = ref(true)
const loadProgress = ref(0)
const currentTime = ref(0)
const totalTime = ref(0)
const errorMessage = ref(null)
 
// 全屏控制 
const { isFullscreen, toggle: toggleFullscreen } = useFullscreen(playerFrame)
 
// 播放器URL 
const playerUrl = computed(() => {
  return `${import.meta.env.VITE_API_BASE}/stanford-town/player/${props.experimentId}?t=${Date.now()}` 
})
 
// 播放器通信 
const postMessage = (type, payload = {}) => {
  playerFrame.value?.contentWindow?.postMessage({ 
    type: `STANFORD_PLAYER_${type}`,
    experimentId: props.experimentId, 
    ...payload 
  }, '*')
}
 
// 事件处理 
const handlePlayerLoad = () => {
  // 初始化消息监听 
  window.addEventListener('message',  handlePlayerMessage)
  // 请求初始状态 
  postMessage('INIT')
}
 
const handlePlayerMessage = (event) => {
  if (event.origin  !== import.meta.env.VITE_API_ORIGIN)  return 
 
  switch (event.data.type)  {
    case 'STANFORD_PLAYER_PROGRESS':
      loadProgress.value  = Math.min(100,  event.data.progress) 
      break 
    case 'STANFORD_PLAYER_READY':
      isLoading.value  = false 
      totalTime.value  = event.data.duration  
      break 
    case 'STANFORD_PLAYER_UPDATE':
      currentTime.value  = event.data.currentTime  
      break 
    case 'STANFORD_PLAYER_ERROR':
      handlePlayerError(event.data.error) 
      break 
  }
}
 
// 控制方法 
const togglePlayback = () => {
  isPlaying.value  = !isPlaying.value  
  postMessage(isPlaying.value  ? 'PLAY' : 'PAUSE', {
    speed: playbackSpeed.value  
  })
}
 
const handlePlayerError = (error) => {
  errorMessage.value  = `播放器错误: ${error.message}` 
  isLoading.value  = false 
  console.error('[Player  Error]', error)
}
 
// 生命周期 
onMounted(() => {
  // 初始化加载进度模拟 
  const interval = setInterval(() => {
    if (!isLoading.value)  {
      clearInterval(interval)
      return 
    }
    loadProgress.value  = Math.min(loadProgress.value  + 10, 90)
  }, 500)
 
  onUnmounted(() => {
    clearInterval(interval)
    window.removeEventListener('message',  handlePlayerMessage)
  })
})
</script>
 
<style scoped>
.simulation-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  background: #1a1a1a;
  aspect-ratio: 16/9;
}
 
.simulation-wrapper {
  position: relative;
  height: 100%;
}
 
.simulation-frame {
  width: 100%;
  height: 100%;
  background: #000;
}
 
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  z-index: 10;
}
 
.loading-text {
  color: #fff;
  font-size: 0.9rem;
}
 
.control-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
 
.primary-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
 
.secondary-controls {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
 
.icon-button {
  background: rgba(255,255,255,0.1);
  border: none;
  padding: 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
 
.icon-button:hover {
  background: rgba(255,255,255,0.2);
}
 
/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
 
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
 
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
 
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>