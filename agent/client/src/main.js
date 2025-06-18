import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
app.provide('$router', router)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
