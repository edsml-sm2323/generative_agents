<template>
  <!-- 添加路由视图容器 -->
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>
 
<script setup>
// 确保路由正确初始化 
import { useRouter } from 'vue-router'
 
const router = useRouter()
 
// 默认重定向到主界面 
router.replace('/stanford-town') 
</script>
 
<style>
/* 优化全局样式 */
#app {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
 
/* 添加页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
 
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
 
/* 修复默认边距问题 */
body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
}
</style>