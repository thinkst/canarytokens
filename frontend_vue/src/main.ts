import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
//@ts-ignore
import registertBaseComponents from '@/components/base/_index.js';

const app = createApp(App)
registertBaseComponents(app);
app.use(router)

app.mount('#app')
