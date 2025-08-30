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
// Social Networks Views
import SocialNetworksDashboard from '@/views/SocialNetworksDashboard.vue'
import SocialSharingDashboard from '@/views/SocialSharingDashboard.vue'
import GroupsDashboard from '@/views/GroupsDashboard.vue'
import SocialNetworksSettings from '@/views/SocialNetworksSettings.vue'
// Chat Views
import ChatDashboard from '@/views/ChatDashboardSmart.vue'
import ChatRooms from '@/views/ChatRoomsSimple.vue'
import ChatModeration from '@/views/ChatModerationSimple.vue'
// Forum Views
import ForumDashboard from '@/views/ForumDashboard.vue'
import ForumCategories from '@/views/ForumCategories.vue'
import ForumTopics from '@/views/ForumTopics.vue'
import ForumModeration from '@/views/ForumModeration.vue'
import ForumReports from '@/views/ForumReports.vue'
// Content Views
import ContentDashboard from '@/views/ContentDashboard.vue'
import ArticlesManagement from '@/views/ArticlesManagement.vue'
import ContentCategories from '@/views/ContentCategories.vue'
import ContentReports from '@/views/ContentReports.vue'
// Polls Views
import PollsDashboard from '@/views/PollsDashboard.vue'
import PollsManagement from '@/views/PollsManagement.vue'

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
  {
    path: '/social/sharing',
    name: 'SocialSharingDashboard',
    component: SocialSharingDashboard,
    meta: {
      title: 'Compartilhamento Social - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/social/groups',
    name: 'GroupsDashboard',
    component: GroupsDashboard,
    meta: {
      title: 'Grupos Privados - Mark Foot',
      requiresAuth: true
    }
  },
  // Social Networks Routes
  {
    path: '/social-networks',
    name: 'SocialNetworksDashboard',
    component: SocialNetworksDashboard,
    meta: {
      title: 'Dashboard Redes Sociais - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/social-networks/sharing',
    name: 'SocialSharingDashboard',
    component: SocialSharingDashboard,
    meta: {
      title: 'Compartilhamento Social - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/social-networks/groups',
    name: 'GroupsDashboard', 
    component: GroupsDashboard,
    meta: {
      title: 'Grupos Privados - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/social-networks/settings',
    name: 'SocialNetworksSettings',
    component: SocialNetworksSettings,
    meta: {
      title: 'Configurações de Redes - Mark Foot',
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
  },
  // Forum Management Routes
  {
    path: '/forum',
    name: 'ForumDashboard',
    component: ForumDashboard,
    meta: {
      title: 'Fórum Dashboard - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/forum/categories',
    name: 'ForumCategories',
    component: ForumCategories,
    meta: {
      title: 'Gerenciar Categorias - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/forum/topics',
    name: 'ForumTopics',
    component: ForumTopics,
    meta: {
      title: 'Gerenciar Tópicos - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/forum/moderation',
    name: 'ForumModeration',
    component: ForumModeration,
    meta: {
      title: 'Moderação do Fórum - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/forum/reports',
    name: 'ForumReports',
    component: ForumReports,
    meta: {
      title: 'Relatórios do Fórum - Mark Foot',
      requiresAuth: true
    }
  },
  // Content Management Routes
  {
    path: '/content',
    name: 'ContentDashboard',
    component: ContentDashboard,
    meta: {
      title: 'Gestão de Conteúdo - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/content/articles',
    name: 'ArticlesManagement',
    component: ArticlesManagement,
    meta: {
      title: 'Gerenciar Artigos - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/content/categories',
    name: 'ContentCategories',
    component: ContentCategories,
    meta: {
      title: 'Categorias de Conteúdo - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/content/reports',
    name: 'ContentReports',
    component: ContentReports,
    meta: {
      title: 'Relatórios de Conteúdo - Mark Foot',
      requiresAuth: true
    }
  },
  // Polls Management Routes
  {
    path: '/polls',
    name: 'PollsDashboard',
    component: PollsDashboard,
    meta: {
      title: 'Dashboard Enquetes - Mark Foot',
      requiresAuth: true
    }
  },
  {
    path: '/polls/manage',
    name: 'PollsManagement',
    component: PollsManagement,
    meta: {
      title: 'Gerenciar Enquetes - Mark Foot',
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
