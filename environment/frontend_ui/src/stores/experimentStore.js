import { defineStore } from 'pinia'
import experimentAPI from '@/api/experiments'

export const useExperimentStore = defineStore('experiments', {
  state: () => ({
    experiments: [],
    currentExperiment: null,
    loading: false
  }),
  
  actions: {
    async fetchExperiments() {
      this.loading  = true
      try {
        const res = await experimentAPI.getAll() 
        this.experiments  = res.data 
      } finally {
        this.loading  = false
      }
    },
    
    async startExperiment(id) {
      await experimentAPI.start(id) 
      this.pollStatus(id) 
    },
    
    async pollStatus(id) {
      const interval = setInterval(async () => {
        const res = await experimentAPI.getStatus(id) 
        if (['completed', 'stopped'].includes(res.status))  {
          clearInterval(interval)
        }
        this.updateExperimentStatus(id,  res)
      }, 3000)
    }
  }
})