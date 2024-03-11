import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'Generate New Canary Token',
      },
    },
    {
      path: '/manage',
      name: 'manage',
      component: () => import('../views/ManageView.vue'),
      meta: {
        title: 'Manage Token',
      },
    }
  ]
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title}`
  next()
})

export default router
