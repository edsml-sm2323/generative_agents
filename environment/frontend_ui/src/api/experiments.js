import axios from '@/utils/axios'

const API_BASE = '/api/stanford-town/experiments'

export default {
  // 创建/修改实验
  saveExperiment: (data) => axios.post(`${API_BASE}/`,  data),
  
  // 启动实验
  startExperiment: (id) => axios.post(`${API_BASE}/${id}/start`), 
  
  // 获取实验状态
  getStatus: (id) => axios.get(`${API_BASE}/${id}/status`), 
  
  // 获取实验数据
  getDetails: (id) => axios.get(`${API_BASE}/${id}/details`), 
  
  // 终止实验
  stopExperiment: (id) => axios.post(`${API_BASE}/${id}/stop`) 
}