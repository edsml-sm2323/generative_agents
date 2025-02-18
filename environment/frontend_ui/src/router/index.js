import { createRouter, createWebHistory } from 'vue-router'
import StanfordTownView from '@/views/StanfordTownView.vue' 
import TestView from '@/views/TestView.vue'
 
const routes = [
  {
    path: '/stanford-town',
    name: 'StanfordTown',
    component: StanfordTownView,
    meta: { title: '斯坦福小镇模拟' }
  },
  {
    path: '/test',
    name: 'test',
    component: TestView,
    meta: { title: 'api测试页面' }
  }
]
 
const router = createRouter({
  history: createWebHistory(),
  routes 
})
 
// 动态设置页面标题 
router.beforeEach((to)  => {
  document.title  = to.meta.title  || '生成式智能体平台'
})
 
export default router 