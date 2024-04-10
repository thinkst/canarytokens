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
  faCloudArrowUp,
  faRotateRight,
} from '@fortawesome/free-solid-svg-icons';
import { createVfm } from 'vue-final-modal';
import { vTooltip } from 'floating-vue';
import VueGoogleMaps from 'vue-google-maps-community-fork';
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
  faCopy,
  faCloudArrowUp,
  faRotateRight
);

const vfm = createVfm();
app.use(vfm);

app.use(VueGoogleMaps, {
  installComponents: true,
  load: {
    key: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  },
});

app.directive('tooltip', vTooltip);

app.use(router);

app.mount('#app');
