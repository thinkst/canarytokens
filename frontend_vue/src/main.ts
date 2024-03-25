import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import {
  faBars,
  faXmark,
  faLink,
  faQuestion,
  faCircleQuestion,
  faAngleLeft,
  faArrowRight,
  faCheck,
  faCopy,
} from '@fortawesome/free-solid-svg-icons';
import { createVfm } from 'vue-final-modal';
import { vTooltip } from 'floating-vue';
import VueGoogleMaps from '@fawmi/vue-google-maps';
import 'vue-final-modal/style.css';
import 'floating-vue/dist/style.css';
import './style.css';

const app = createApp(App);

app.component('FontAwesomeIcon', FontAwesomeIcon);
library.add(
  faBars,
  faXmark,
  faLink,
  faQuestion,
  faCircleQuestion,
  faAngleLeft,
  faArrowRight,
  faCheck,
  faCopy
);

const vfm = createVfm();
app.use(vfm);

app.use(VueGoogleMaps, {
  load: {
    key: 'ADD_KEY_HERE',
  },
});

app.directive('tooltip', vTooltip);

app.use(router);

app.mount('#app');
