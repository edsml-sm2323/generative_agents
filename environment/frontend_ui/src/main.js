import { createApp } from 'vue'
import App from './App.vue' 
import router from './router'
import { createPinia } from 'pinia'
 
// 初始化应用 
const app = createApp(App)
 
// 安装插件 
app.use(createPinia()) 
app.use(router) 
 
// 挂载到DOM 
app.mount('#app') 