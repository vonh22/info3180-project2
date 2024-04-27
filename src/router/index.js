import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/explore',
      name: 'explore',
      component: () => import('../views/ExploreView.vue'),
      requiresAuth: true
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/logout',
      name: 'logout',
      component: () => import('../views/LogoutView.vue')
    },
    {
      path: '/users/:id',
      name: 'users',
      component: () => import('../views/ProfileView.vue'),
      params: true,
    },
    {
      path: '/posts/new',
      name: 'post',
      component: () => import('../views/NewPostView.vue')
    },

  ]
})

const protectedRoutes = [
  "explore",
  "users",
  "post",
]
router.beforeEach( async (to, from, next) => {
  const isLoggedIn = async () => {
    const response = await fetch('/api/v1/loggedin')
    return response.json()
  }

  let loggedInStatus = await isLoggedIn();

  const isProtected = protectedRoutes.includes(to.name)
  if(isProtected && !loggedInStatus.logged_in){
      next({
          path: '/login',
          query: { redirect: to.fullPath }
      })
  }else next()
})

export default router
