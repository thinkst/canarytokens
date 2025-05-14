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
        title: 'Canarytokens',
      },
    },
    {
      path: '/generate',
      name: 'generate',
      component: HomeView,
      meta: {
        title: 'Create New Canarytoken',
      },
    },
    {
      path: '/generate/:tokentype',
      name: 'generate-custom',
      component: () => import('../views/CustomFlowView.vue'),
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
        title: 'Manage Canarytoken',
      },
    },
    {
      path: '/token-config/:tokentype',
      name: 'manage-custom',
      component: () => import('../views/CustomFlowView.vue'),
      meta: {
        title: 'Manage Canarytoken',
      },
    },
    {
      path: '/manage',
      name: 'manage-old',
      redirect: (to) => {
        return {
          path: `/manage/${to.query.auth}/${to.query.token}`,
          query: {},
        };
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
        title: 'Alerts History',
      },
    },
    {
      path: '/history',
      name: 'history-old',
      redirect: (to) => {
        return {
          path: `/history/${to.query.auth}/${to.query.token}`,
          query: {},
        };
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
        header:
          "We're sorry, but we couldn't find the token you're looking for.",
        description:
          'This could be because the authentication or Canarytoken provided is incorrect.',
        action: 'Please check your token details and try again.',
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/ErrorView.vue'),
      meta: {
        title: '404',
        header: " Oops! The page you're looking for can't be found.",
        description:
          'This might be because the URL is incorrect, or the page has been moved or deleted.',
        action:
          'Please check the URL or go back to the homepage and try again.',
      },
    },
    {
      path: '/404',
      name: '404',
      component: () => import('../views/ErrorView.vue'),
      meta: {
        title: '404',
        header: " Oops! The page you're looking for can't be found.",
        description:
          'This might be because the URL is incorrect, or the page has been moved or deleted.',
        action:
          'Please check the URL or go back to the homepage and try again.',
      },
    },
    {
      path: '/500',
      name: '500',
      component: () => import('../views/ErrorView.vue'),
      meta: {
        title: '500',
        header: 'Oops! Something went wrong on our end.',
        description:
          'This might be due to a temporary issue or an unexpected server error.',
        action:
          'Please try refreshing the page, or go back to the homepage and try again later.',
      },
    },
  ],
});

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title}`;
  next();
});

export default router;
