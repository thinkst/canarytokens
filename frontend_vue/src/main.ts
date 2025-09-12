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
  faChevronLeft,
  faChevronRight,
  faCopy,
  faCloudArrowUp,
  faRotateRight,
  faHands,
  faRobot,
  faArrowLeft,
  faArrowDown,
  faChevronUp,
  faPlus,
  faMinus,
  faBell,
  faGear,
  faMagnifyingGlass,
  faFileExcel,
  faFile,
  faQuoteLeft,
  faArrowUpRightFromSquare,
  faCreditCard,
  faLock,
  faCalendarDay,
  faIdCard,
  faCircleCheck,
  faTrash,
} from '@fortawesome/free-solid-svg-icons';
import { createVfm } from 'vue-final-modal';
import { vTooltip } from 'floating-vue';
import VueGoogleMaps from 'vue-google-maps-community-fork';
import vSelect from 'vue-select';
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
  faRotateRight,
  faHands,
  faRobot,
  faArrowLeft,
  faArrowDown,
  faChevronUp,
  faPlus,
  faMinus,
  faBell,
  faGear,
  faMagnifyingGlass,
  faFileExcel,
  faFile,
  faQuoteLeft,
  faArrowUpRightFromSquare,
  faCreditCard,
  faLock,
  faCalendarDay,
  faIdCard,
  faCircleCheck,
  faTrash,
  faChevronLeft,
  faChevronRight
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
app.component('VSelect', vSelect);

app.use(router);

app.mount('#app');
