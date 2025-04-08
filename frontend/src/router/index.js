import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/Chat.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cards',
      name: 'cards',
      component: () => import('../views/Cards.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cards/:id',
      name: 'card-detail',
      component: () => import('../views/CardDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/compare',
      name: 'compare',
      component: () => import('../views/Compare.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/Profile.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 需要登录的路由
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 