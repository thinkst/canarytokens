import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
//@ts-ignore
import registertBaseComponents from '@/components/base/_index.js';
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faBars, faXmark, faLink } from '@fortawesome/free-solid-svg-icons';

const app = createApp(App)

app.component('font-awesome-icon', FontAwesomeIcon)
library.add(faBars, faXmark, faLink)

registertBaseComponents(app);
app.use(router)

app.mount('#app')
