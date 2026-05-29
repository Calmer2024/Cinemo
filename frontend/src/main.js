import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)

app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.mount('#app')

// Enable dark mode
document.documentElement.classList.add('dark')
