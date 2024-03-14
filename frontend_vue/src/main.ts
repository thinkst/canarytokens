import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
//@ts-ignore
import registertBaseComponents from '@/components/base/_index.js';
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faBars, faXmark, faLink, faQuestion, faCircleQuestion, faAngleLeft, faArrowRight } from '@fortawesome/free-solid-svg-icons';
import { createVfm } from 'vue-final-modal'
import 'vue-final-modal/style.css'


const app = createApp(App)

app.component('FontAwesomeIcon', FontAwesomeIcon)
library.add(faBars, faXmark, faLink, faQuestion, faCircleQuestion, faAngleLeft, faArrowRight)

const vfm = createVfm()
app.use(vfm)

registertBaseComponents(app);
app.use(router)

app.mount('#app')
