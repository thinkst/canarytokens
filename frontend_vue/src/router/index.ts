import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import { ENV_MODE } from '../constants.ts';

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
      component: () =>
        import('../views/ManageView.vue').catch(() => {
          router.push({ name: 'error' });
        }),
      meta: {
        title: 'Manage Token',
      },
    },
    {
      path: '/history/:auth/:token',
      name: 'history',
      component: () =>
        import('../views/HistoryView.vue').catch(() => {
          router.push({ name: 'error' });
        }),
      meta: {
        title: 'Token History',
      },
    },
    {
      path: '/error',
      name: 'error',
      component: () => import('../views/ErrorView.vue'),
      meta: {
        title: 'Oh no! Something went wrong!',
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: '404',
      component: () => import('../views/404View.vue'),
      meta: {
        title: '404',
      },
    },
    ...(import.meta.env.MODE === ENV_MODE.DEVELOPMENT
      ? [
          {
            path: '/components',
            name: 'components',
            component: () => import('../views/ComponentPreview.vue'),
            meta: {
              title: 'ComponentPreview',
            },
          },
        ]
      : []),
  ],
});

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title}`;
  next();
});

export default router;
