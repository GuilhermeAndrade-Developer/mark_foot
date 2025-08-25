import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import views
import Dashboard from '@/views/Dashboard.vue'
import Teams from '@/views/Teams.vue'
import Players from '@/views/Players.vue'
import Matches from '@/views/Matches.vue'
import Competitions from '@/views/Competitions.vue'
import Standings from '@/views/Standings.vue'
import Statistics from '@/views/Statistics.vue'
import Login from '@/views/Login.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: 'Login - Mark Foot',
      requiresGuest: true
    }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/teams',
    name: 'Teams',
    component: Teams,
    meta: {
      title: 'Times - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/players',
    name: 'Players',
    component: Players,
    meta: {
      title: 'Jogadores - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/matches',
    name: 'Matches',
    component: Matches,
    meta: {
      title: 'Partidas - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/competitions',
    name: 'Competitions',
    component: Competitions,
    meta: {
      title: 'Competições - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/standings',
    name: 'Standings',
    component: Standings,
    meta: {
      title: 'Classificação - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics,
    meta: {
      title: 'Estatísticas - Mark Foot',
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

// Authentication guard
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth if not already done
  if (!authStore.isAuthenticated) {
    authStore.initializeAuth()
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Check if route requires guest (redirect authenticated users)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  // Update page title
  document.title = to.meta?.title as string || 'Mark Foot'
  
  next()
})

export default router
