import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// Import views
import Dashboard from '@/views/Dashboard.vue'
import Teams from '@/views/Teams.vue'
import Players from '@/views/Players.vue'
import Matches from '@/views/Matches.vue'
import Competitions from '@/views/Competitions.vue'
import Standings from '@/views/Standings.vue'
import Statistics from '@/views/Statistics.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard - Mark Foot'
    }
  },
  {
    path: '/teams',
    name: 'Teams',
    component: Teams,
    meta: {
      title: 'Times - Mark Foot'
    }
  },
  {
    path: '/players',
    name: 'Players',
    component: Players,
    meta: {
      title: 'Jogadores - Mark Foot'
    }
  },
  {
    path: '/matches',
    name: 'Matches',
    component: Matches,
    meta: {
      title: 'Partidas - Mark Foot'
    }
  },
  {
    path: '/competitions',
    name: 'Competitions',
    component: Competitions,
    meta: {
      title: 'Competições - Mark Foot'
    }
  },
  {
    path: '/standings',
    name: 'Standings',
    component: Standings,
    meta: {
      title: 'Classificação - Mark Foot'
    }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics,
    meta: {
      title: 'Estatísticas - Mark Foot'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Update page title
router.beforeEach((to) => {
  document.title = to.meta?.title as string || 'Mark Foot'
})

export default router
