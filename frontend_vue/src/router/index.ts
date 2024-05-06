import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'Generate New Canarytoken',
      },
    },
    {
      path: '/manage/:auth/:token',
      name: 'manage',
      component: () => import('../views/ManageView.vue'),
      meta: {
        title: 'Manage Token',
      },
    },
    {
      path: '/history/:auth/:token',
      name: 'history',
      component: () => import('../views/HistoryView.vue'),
      meta: {
        title: 'Token History',
      },
    },
    {
      path: '/components',
      name: 'components',
      component: () => import('../views/ComponentPreview.vue'),
      meta: {
        title: 'ComponentPreview',
      },
    },
  ],
});

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title}`;
  next();
});

export default router;
