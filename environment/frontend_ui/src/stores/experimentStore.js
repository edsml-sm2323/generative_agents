// src/stores/experimentStore.js  
import { defineStore } from 'pinia'
import experimentAPI from '@/api/experiments'
import {useNotification} from '@/utils/helpers' 

// 轮询间隔配置 
const POLL_INTERVAL = 3000 
const MAX_POLL_ATTEMPTS = 20 
 
export const useExperimentStore = defineStore('experiments', {
  state: () => ({
    experiments: [],
    currentExperiment: null,
    loading: false,
    activePollers: new Map(), // 跟踪活动轮询器 
    error: null 
  }),
  
  actions: {
    async fetchExperiments() {
      this.loading  = true 
      this.error  = null 
      try {
        const { data } = await experimentAPI.getAll() 
        this.experiments  = data.map(exp  => ({
          ...exp,
          lastUpdated: new Date().toISOString()
        }))
      } catch (error) {
        this.handleError(' 获取实验列表失败', error)
      } finally {
        this.loading  = false 
      }
    },
    
    async startExperiment(id) {
      try {
        await experimentAPI.start(id) 
        this.startStatusPolling(id) 
        this.updateExperiment(id,  { status: 'starting' })
      } catch (error) {
        this.handleError(' 启动实验失败', error)
      }
    },
 
    startStatusPolling(id) {
      if (this.activePollers.has(id))  return 
 
      const controller = new AbortController()
      let attempts = 0 
      
      const poll = async () => {
        if (attempts++ >= MAX_POLL_ATTEMPTS) {
          this.stopPolling(id) 
          return 
        }
 
        try {
          const { data: status } = await experimentAPI.getStatus(id,  {
            signal: controller.signal  
          })
          
          this.updateExperiment(id,  {
            ...status,
            lastUpdated: new Date().toISOString()
          })
 
          if (!['running', 'pending'].includes(status.state))  {
            this.stopPolling(id) 
            if (status.state  === 'completed') {
              this.handleExperimentComplete(id,  status.results) 
            }
          } else {
            setTimeout(poll, POLL_INTERVAL)
          }
        } catch (error) {
          if (error.name  !== 'AbortError') {
            this.handleError(' 状态更新失败', error)
          }
        }
      }
 
      this.activePollers.set(id,  controller)
      poll()
    },
 
    stopPolling(id) {
      const controller = this.activePollers.get(id) 
      if (controller) {
        controller.abort() 
        this.activePollers.delete(id) 
      }
    },
 
    updateExperiment(id, payload) {
      const index = this.experiments.findIndex(e  => e.id  === id)
      if (index >= 0) {
        this.experiments[index]  = { 
          ...this.experiments[index],  
          ...payload 
        }
      }
      
      if (this.currentExperiment?.id  === id) {
        this.currentExperiment  = { ...this.currentExperiment,  ...payload }
      }
    },
 
    handleExperimentComplete(id, results) {
      const { showSuccess } = useNotification()
      showSuccess('实验完成', `实验 ${id} 已完成并生成结果`)
      this.updateExperiment(id,  {
        results,
        completedAt: new Date().toISOString()
      })
    },
 
    handleError(context, error) {
      const { showError } = useNotification()
      this.error  = error.message  
      showError(context, error.response?.data?.message  || error.message) 
      console.error(`${context}:`,  error)
    }
  },
  
  getters: {
    activeExperiments: (state) => 
      state.experiments.filter(e  => e.status  === 'running'),
    experimentById: (state) => (id) => 
      state.experiments.find(e  => e.id  === id)
  }
})