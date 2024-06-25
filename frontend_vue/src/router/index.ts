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
        title: 'Create New Canarytoken',
      },
    },
    {
      path: '/create',
      name: 'create',
      component: HomeView,
      meta: {
        title: 'Create New Canarytoken',
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
      path: '/manage',
      name: 'manage-old',
      redirect: to => {
        return { path: `/manage/${to.query.auth}/${to.query.token}`, query: {}}
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
      path: '/history',
      name: 'history-old',
      redirect: to => {
        return { path: `/history/${to.query.auth}/${to.query.token}`, query: {}}
      },
    },
    {
      path: '/legal',
      name: 'legal',
      component: () => import('../views/LegalView.vue'),
      meta: {
        title: 'Acceptable Use Policy',
      },
    },
    {
      path: '/entra/:result',
      name: 'entra-id',
      component: () => import('../views/EntraIDResultView.vue'),
      meta: {
        title: 'Azure Entra ID',
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
