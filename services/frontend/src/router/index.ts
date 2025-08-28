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
import Settings from '@/views/Settings.vue'
import Login from '@/views/Login.vue'
// AI Views
import AIDashboard from '@/views/AIDashboard.vue'
import AISentiment from '@/views/AISentiment.vue'
import AITesting from '@/views/AITesting.vue'
// Gamification Views
import GamificationDashboard from '@/views/GamificationDashboard.vue'
import GamificationUsers from '@/views/GamificationUsers.vue'
import GamificationAnalytics from '@/views/GamificationAnalytics.vue'
// Social Views
import SocialDashboard from '@/views/SocialDashboard.vue'
import SocialComments from '@/views/SocialComments.vue'
import SocialUsers from '@/views/SocialUsers.vue'
// Chat Views
import ChatDashboard from '@/views/ChatDashboardSmart.vue'
import ChatRooms from '@/views/ChatRoomsSimple.vue'
import ChatModeration from '@/views/ChatModerationSimple.vue'

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
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: 'Configurações - Mark Foot',
      requiresAuth: true
    }
  },
  // AI Management Routes
  {
    path: '/ai-dashboard',
    name: 'AIDashboard',
    component: AIDashboard,
    meta: {
      title: 'Dashboard IA - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/ai-sentiment',
    name: 'AISentiment',
    component: AISentiment,
    meta: {
      title: 'Análise de Sentimento - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/ai-testing',
    name: 'AITesting',
    component: AITesting,
    meta: {
      title: 'Testes IA - Mark Foot',
      requiresAuth: true
    }
  },
  // Gamification Routes
  {
    path: '/gamification',
    name: 'GamificationDashboard',
    component: GamificationDashboard,
    meta: {
      title: 'Gamificação - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/gamification/users',
    name: 'GamificationUsers',
    component: GamificationUsers,
    meta: {
      title: 'Gestão de Usuários - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/gamification/analytics',
    name: 'GamificationAnalytics',
    component: GamificationAnalytics,
    meta: {
      title: 'Analytics - Mark Foot',
      requiresAuth: true
    }
  },
  // Social Management Routes
  {
    path: '/social',
    name: 'SocialDashboard',
    component: SocialDashboard,
    meta: {
      title: 'Social Dashboard - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/social/comments',
    name: 'SocialComments',
    component: SocialComments,
    meta: {
      title: 'Gestão de Comentários - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/social/users',
    name: 'SocialUsers',
    component: SocialUsers,
    meta: {
      title: 'Usuários Sociais - Mark Foot',
      requiresAuth: true
    }
  },
  // Chat Management Routes
  {
    path: '/chat',
    name: 'ChatDashboard',
    component: ChatDashboard,
    meta: {
      title: 'Chat Dashboard - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/chat/rooms',
    name: 'ChatRooms',
    component: ChatRooms,
    meta: {
      title: 'Gerenciar Salas - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/chat/moderation',
    name: 'ChatModeration',
    component: ChatModeration,
    meta: {
      title: 'Moderação de Chat - Mark Foot',
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

// Authentication guard
router.beforeEach(async (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
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
