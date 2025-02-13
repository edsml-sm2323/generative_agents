import axios from 'axios'
 
const instance = axios.create({ 
  baseURL: process.env.VUE_APP_API_BASE  || '/api',
  timeout: 10000 
})
 
// 请求拦截器 
instance.interceptors.request.use(config  => {
  return config 
})
 
// 响应拦截器 
instance.interceptors.response.use( 
  response => response.data, 
  error => {
    console.error('API  Error:', error)
    return Promise.reject(error) 
  }
)
 
export default instance 