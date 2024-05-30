import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import { ENV_MODE } from '../constants.ts';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/newuiwhodis/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'Generate New Canarytoken',
      },
    },
    {
      path: '/newuiwhodis/manage/:auth/:token',
      name: 'manage',
      component: () =>
        import('../views/ManageView.vue').catch(() => {
          router.push({ name: 'error' });
        }),
      meta: {
        title: 'Manage Token',
      },
      alias: '/manage/:auth/:token' // Handle old /manage/:auth/:token links
    },
    {
      path: '/newuiwhodis/history/:auth/:token',
      name: 'history',
      component: () =>
        import('../views/HistoryView.vue').catch(() => {
          router.push({ name: 'error' });
        }),
      meta: {
        title: 'Token History',
      },
      alias: '/history/:auth/:token' // Handle old /history/:auth/:token links
    },
    {
      path: '/newuiwhodis/legal',
      name: 'legal',
      component: () => import('../views/LegalView.vue'),
      meta: {
        title: 'Acceptable Use Policy',
      },
    },
    {
      path: '/newuiwhodis/error',
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
            path: '/newuiwhodis/components',
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
