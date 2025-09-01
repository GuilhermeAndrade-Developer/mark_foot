# Frontend Vue.js Integration for WhatsApp Management

## Objective
Integrate WhatsApp Business functionality with existing Vue.js admin dashboard, expanding current management interfaces and adding new components for comprehensive WhatsApp user management, analytics, and moderation.

## Current Project Context
- Existing Vue.js frontend with 40+ admin screens
- Complete Vue.js dashboard with navigation, routing, and components
- Django backend with WhatsApp integration (documents 01-06)
- Current admin screens: GestaoClientes.vue, FinanceiroDashboard.vue, Dashboard.vue, etc.
- Established component patterns and styling

## Technical Requirements

### 1. Update Main Navigation Menu

#### src/router/index.ts - Add WhatsApp Routes
```typescript
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import GestaoClientes from '@/views/GestaoClientes.vue'
import FinanceiroDashboard from '@/views/FinanceiroDashboard.vue'

// New WhatsApp components
import WhatsAppDashboard from '@/views/WhatsAppDashboard.vue'
import WhatsAppUsers from '@/views/WhatsAppUsers.vue'
import WhatsAppConversations from '@/views/WhatsAppConversations.vue'
import WhatsAppAnalytics from '@/views/WhatsAppAnalytics.vue'
import WhatsAppSettings from '@/views/WhatsAppSettings.vue'
import WhatsAppReports from '@/views/WhatsAppReports.vue'

const routes = [
  // ... existing routes ...
  
  // WhatsApp Management Routes
  {
    path: '/whatsapp',
    name: 'WhatsApp',
    redirect: '/whatsapp/dashboard',
    meta: { requiresAuth: true, roles: ['admin', 'moderator'] }
  },
  {
    path: '/whatsapp/dashboard',
    name: 'WhatsAppDashboard',
    component: WhatsAppDashboard,
    meta: { 
      requiresAuth: true, 
      roles: ['admin', 'moderator'],
      title: 'WhatsApp Dashboard',
      breadcrumb: 'WhatsApp > Dashboard'
    }
  },
  {
    path: '/whatsapp/users',
    name: 'WhatsAppUsers',
    component: WhatsAppUsers,
    meta: { 
      requiresAuth: true, 
      roles: ['admin', 'moderator'],
      title: 'Usuários WhatsApp',
      breadcrumb: 'WhatsApp > Usuários'
    }
  },
  {
    path: '/whatsapp/conversations',
    name: 'WhatsAppConversations',
    component: WhatsAppConversations,
    meta: { 
      requiresAuth: true, 
      roles: ['admin', 'moderator'],
      title: 'Conversas WhatsApp',
      breadcrumb: 'WhatsApp > Conversas'
    }
  },
  {
    path: '/whatsapp/analytics',
    name: 'WhatsAppAnalytics',
    component: WhatsAppAnalytics,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Analytics WhatsApp',
      breadcrumb: 'WhatsApp > Analytics'
    }
  },
  {
    path: '/whatsapp/reports',
    name: 'WhatsAppReports',
    component: WhatsAppReports,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Relatórios WhatsApp',
      breadcrumb: 'WhatsApp > Relatórios'
    }
  },
  {
    path: '/whatsapp/settings',
    name: 'WhatsAppSettings',
    component: WhatsAppSettings,
    meta: { 
      requiresAuth: true, 
      roles: ['admin'],
      title: 'Configurações WhatsApp',
      breadcrumb: 'WhatsApp > Configurações'
    }
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
```

#### Update Navigation Component - src/components/Navigation.vue
```vue
<template>
  <nav class="main-navigation">
    <!-- Existing navigation items -->
    <div class="nav-section">
      <h3>Gestão Principal</h3>
      <router-link to="/dashboard" class="nav-item">
        <i class="fas fa-tachometer-alt"></i>
        Dashboard
      </router-link>
      <router-link to="/gestao-clientes" class="nav-item">
        <i class="fas fa-users"></i>
        Gestão de Clientes
      </router-link>
      <router-link to="/financeiro" class="nav-item">
        <i class="fas fa-chart-line"></i>
        Financeiro
      </router-link>
    </div>

    <!-- NEW WHATSAPP SECTION -->
    <div class="nav-section whatsapp-section">
      <h3>
        <i class="fab fa-whatsapp"></i>
        WhatsApp Business
      </h3>
      <router-link to="/whatsapp/dashboard" class="nav-item">
        <i class="fas fa-chart-pie"></i>
        Dashboard WhatsApp
      </router-link>
      <router-link to="/whatsapp/users" class="nav-item">
        <i class="fas fa-mobile-alt"></i>
        Usuários
        <span v-if="whatsappStats.activeUsers" class="badge">
          {{ whatsappStats.activeUsers }}
        </span>
      </router-link>
      <router-link to="/whatsapp/conversations" class="nav-item">
        <i class="fas fa-comments"></i>
        Conversas
        <span v-if="whatsappStats.pendingMessages" class="badge badge-warning">
          {{ whatsappStats.pendingMessages }}
        </span>
      </router-link>
      <router-link to="/whatsapp/analytics" class="nav-item">
        <i class="fas fa-chart-bar"></i>
        Analytics
      </router-link>
      <router-link to="/whatsapp/reports" class="nav-item">
        <i class="fas fa-file-pdf"></i>
        Relatórios
      </router-link>
      <router-link to="/whatsapp/settings" class="nav-item">
        <i class="fas fa-cog"></i>
        Configurações
      </router-link>
    </div>

    <!-- Existing sections continue... -->
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useWhatsAppStore } from '@/stores/whatsapp'

const whatsappStore = useWhatsAppStore()
const whatsappStats = ref({
  activeUsers: 0,
  pendingMessages: 0
})

onMounted(async () => {
  await whatsappStore.fetchDashboardStats()
  whatsappStats.value = whatsappStore.stats
})
</script>

<style scoped>
.whatsapp-section {
  border-left: 4px solid #25d366;
  background: linear-gradient(90deg, rgba(37, 211, 102, 0.1) 0%, transparent 100%);
  padding-left: 12px;
}

.whatsapp-section h3 {
  color: #25d366;
  font-weight: bold;
}

.whatsapp-section .nav-item {
  position: relative;
}

.badge {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #25d366;
  color: white;
  border-radius: 12px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: bold;
}

.badge-warning {
  background: #ff9500;
}
</style>
```

### 2. Create WhatsApp Store - src/stores/whatsapp.ts

```typescript
import { defineStore } from 'pinia'
import axios from 'axios'

interface WhatsAppUser {
  id: number
  phone_number: string
  display_name: string
  subscription_status: string
  current_plan?: {
    id: number
    name: string
    price: number
  }
  daily_queries_count: number
  monthly_queries_count: number
  created_at: string
  last_activity: string
}

interface WhatsAppConversation {
  id: number
  user: WhatsAppUser
  messages: WhatsAppMessage[]
  status: 'active' | 'resolved' | 'pending'
  last_message_at: string
  tags: string[]
}

interface WhatsAppMessage {
  id: number
  message_type: 'incoming' | 'outgoing'
  content: string
  timestamp: string
  status: 'sent' | 'delivered' | 'read' | 'failed'
  is_bot_response: boolean
}

interface WhatsAppStats {
  total_users: number
  active_users: number
  premium_users: number
  daily_messages: number
  monthly_revenue: number
  conversion_rate: number
  pending_messages: number
  bot_accuracy: number
}

export const useWhatsAppStore = defineStore('whatsapp', {
  state: () => ({
    users: [] as WhatsAppUser[],
    conversations: [] as WhatsAppConversation[],
    stats: {} as WhatsAppStats,
    loading: false,
    error: null as string | null,
    pagination: {
      page: 1,
      total_pages: 1,
      total_items: 0,
      per_page: 20
    }
  }),

  getters: {
    premiumUsers: (state) => state.users.filter(u => u.subscription_status === 'premium' || u.subscription_status === 'pro'),
    freeUsers: (state) => state.users.filter(u => u.subscription_status === 'free'),
    activeConversations: (state) => state.conversations.filter(c => c.status === 'active'),
    pendingConversations: (state) => state.conversations.filter(c => c.status === 'pending'),
    todayRevenue: (state) => state.stats.monthly_revenue || 0,
    conversionRate: (state) => state.stats.conversion_rate || 0
  },

  actions: {
    async fetchUsers(page = 1, filters = {}) {
      this.loading = true
      this.error = null
      
      try {
        const params = {
          page,
          per_page: this.pagination.per_page,
          ...filters
        }
        
        const response = await axios.get('/api/whatsapp/users/', { params })
        
        this.users = response.data.results
        this.pagination = {
          page: response.data.page,
          total_pages: response.data.total_pages,
          total_items: response.data.total_items,
          per_page: response.data.per_page
        }
      } catch (error) {
        this.error = 'Erro ao carregar usuários WhatsApp'
        console.error('Erro ao buscar usuários:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchConversations(page = 1, filters = {}) {
      this.loading = true
      this.error = null
      
      try {
        const params = {
          page,
          per_page: this.pagination.per_page,
          ...filters
        }
        
        const response = await axios.get('/api/whatsapp/conversations/', { params })
        this.conversations = response.data.results
      } catch (error) {
        this.error = 'Erro ao carregar conversas'
        console.error('Erro ao buscar conversas:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchDashboardStats() {
      try {
        const response = await axios.get('/api/whatsapp/stats/')
        this.stats = response.data
      } catch (error) {
        console.error('Erro ao buscar estatísticas:', error)
      }
    },

    async updateUserSubscription(userId: number, planId: number) {
      try {
        const response = await axios.patch(`/api/whatsapp/users/${userId}/subscription/`, {
          plan_id: planId
        })
        
        // Update user in store
        const userIndex = this.users.findIndex(u => u.id === userId)
        if (userIndex !== -1) {
          this.users[userIndex] = response.data
        }
        
        return response.data
      } catch (error) {
        throw error
      }
    },

    async sendMessage(userId: number, message: string) {
      try {
        const response = await axios.post(`/api/whatsapp/users/${userId}/send-message/`, {
          message
        })
        return response.data
      } catch (error) {
        throw error
      }
    },

    async blockUser(userId: number, reason: string) {
      try {
        const response = await axios.patch(`/api/whatsapp/users/${userId}/block/`, {
          reason
        })
        
        // Update user in store
        const userIndex = this.users.findIndex(u => u.id === userId)
        if (userIndex !== -1) {
          this.users[userIndex].subscription_status = 'blocked'
        }
        
        return response.data
      } catch (error) {
        throw error
      }
    },

    async generateReport(reportType: string, parameters: any) {
      try {
        const response = await axios.post('/api/whatsapp/reports/generate/', {
          report_type: reportType,
          parameters
        })
        return response.data
      } catch (error) {
        throw error
      }
    }
  }
})
```

### 3. WhatsApp Dashboard - src/views/WhatsAppDashboard.vue

```vue
<template>
  <div class="whatsapp-dashboard">
    <div class="page-header">
      <h1>
        <i class="fab fa-whatsapp"></i>
        Dashboard WhatsApp Business
      </h1>
      <p class="subtitle">Métricas e visão geral da plataforma WhatsApp</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card users">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatNumber(stats.total_users) }}</h3>
          <p>Total de Usuários</p>
          <span class="stat-change positive">
            +{{ formatNumber(stats.daily_new_users) }} hoje
          </span>
        </div>
      </div>

      <div class="stat-card premium">
        <div class="stat-icon">
          <i class="fas fa-crown"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatNumber(stats.premium_users) }}</h3>
          <p>Usuários Premium</p>
          <span class="stat-change">
            {{ stats.conversion_rate }}% conversão
          </span>
        </div>
      </div>

      <div class="stat-card messages">
        <div class="stat-icon">
          <i class="fas fa-comments"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatNumber(stats.daily_messages) }}</h3>
          <p>Mensagens Hoje</p>
          <span class="stat-change positive">
            +{{ stats.message_growth }}% vs ontem
          </span>
        </div>
      </div>

      <div class="stat-card revenue">
        <div class="stat-icon">
          <i class="fas fa-dollar-sign"></i>
        </div>
        <div class="stat-content">
          <h3>R$ {{ formatMoney(stats.monthly_revenue) }}</h3>
          <p>Receita Mensal</p>
          <span class="stat-change positive">
            +R$ {{ formatMoney(stats.daily_revenue) }} hoje
          </span>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-container">
        <h3>Usuários por Dia (Últimos 30 dias)</h3>
        <canvas ref="usersChart"></canvas>
      </div>
      
      <div class="chart-container">
        <h3>Conversão para Premium</h3>
        <canvas ref="conversionChart"></canvas>
      </div>
    </div>

    <!-- Activity Tables -->
    <div class="activity-section">
      <div class="recent-users">
        <h3>Novos Usuários Hoje</h3>
        <div class="user-list">
          <div 
            v-for="user in recentUsers" 
            :key="user.id" 
            class="user-item"
          >
            <div class="user-info">
              <strong>{{ user.display_name || user.phone_number }}</strong>
              <span class="phone">{{ user.phone_number }}</span>
            </div>
            <div class="user-status">
              <span :class="`status ${user.subscription_status}`">
                {{ getStatusLabel(user.subscription_status) }}
              </span>
              <span class="time">{{ formatTime(user.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="active-conversations">
        <h3>Conversas Ativas</h3>
        <div class="conversation-list">
          <div 
            v-for="conv in activeConversations" 
            :key="conv.id"
            class="conversation-item"
            @click="openConversation(conv.id)"
          >
            <div class="conv-info">
              <strong>{{ conv.user.display_name || conv.user.phone_number }}</strong>
              <p class="last-message">{{ conv.last_message_preview }}</p>
            </div>
            <div class="conv-meta">
              <span class="time">{{ formatTime(conv.last_message_at) }}</span>
              <span v-if="conv.unread_count" class="unread-badge">
                {{ conv.unread_count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h3>Ações Rápidas</h3>
      <div class="action-buttons">
        <button @click="sendBroadcast" class="action-btn broadcast">
          <i class="fas fa-bullhorn"></i>
          Enviar Broadcast
        </button>
        <button @click="generateReport" class="action-btn report">
          <i class="fas fa-chart-line"></i>
          Gerar Relatório
        </button>
        <button @click="exportUsers" class="action-btn export">
          <i class="fas fa-download"></i>
          Exportar Usuários
        </button>
        <button @click="viewSettings" class="action-btn settings">
          <i class="fas fa-cog"></i>
          Configurações Bot
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWhatsAppStore } from '@/stores/whatsapp'
import Chart from 'chart.js/auto'

const router = useRouter()
const whatsappStore = useWhatsAppStore()

const usersChart = ref<HTMLCanvasElement>()
const conversionChart = ref<HTMLCanvasElement>()

const stats = computed(() => whatsappStore.stats)
const recentUsers = computed(() => whatsappStore.users.slice(0, 5))
const activeConversations = computed(() => whatsappStore.activeConversations.slice(0, 5))

onMounted(async () => {
  await whatsappStore.fetchDashboardStats()
  await whatsappStore.fetchUsers(1, { recent: true })
  await whatsappStore.fetchConversations(1, { status: 'active' })
  
  initializeCharts()
})

const initializeCharts = () => {
  // Users Chart
  if (usersChart.value) {
    new Chart(usersChart.value, {
      type: 'line',
      data: {
        labels: stats.value.daily_users_labels || [],
        datasets: [{
          label: 'Usuários',
          data: stats.value.daily_users_data || [],
          borderColor: '#25d366',
          backgroundColor: 'rgba(37, 211, 102, 0.1)',
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        }
      }
    })
  }

  // Conversion Chart
  if (conversionChart.value) {
    new Chart(conversionChart.value, {
      type: 'doughnut',
      data: {
        labels: ['Free', 'Premium', 'Pro'],
        datasets: [{
          data: [
            stats.value.free_users || 0,
            stats.value.premium_users || 0,
            stats.value.pro_users || 0
          ],
          backgroundColor: ['#95a5a6', '#f39c12', '#e74c3c']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    })
  }
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('pt-BR').format(num || 0)
}

const formatMoney = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value || 0)
}

const formatTime = (timestamp: string) => {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(timestamp))
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    free: 'Gratuito',
    premium: 'Premium',
    pro: 'Pro',
    trial: 'Trial',
    blocked: 'Bloqueado'
  }
  return labels[status] || status
}

const openConversation = (conversationId: number) => {
  router.push(`/whatsapp/conversations/${conversationId}`)
}

const sendBroadcast = () => {
  // Open broadcast modal
  console.log('Send broadcast')
}

const generateReport = () => {
  router.push('/whatsapp/reports')
}

const exportUsers = () => {
  // Export users to CSV
  console.log('Export users')
}

const viewSettings = () => {
  router.push('/whatsapp/settings')
}
</script>

<style scoped>
.whatsapp-dashboard {
  padding: 24px;
  background: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  color: #25d366;
  font-size: 28px;
  margin-bottom: 8px;
}

.page-header h1 i {
  margin-right: 12px;
}

.subtitle {
  color: #6c757d;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-card.users .stat-icon { background: #3498db; }
.stat-card.premium .stat-icon { background: #f39c12; }
.stat-card.messages .stat-icon { background: #25d366; }
.stat-card.revenue .stat-icon { background: #e74c3c; }

.stat-content h3 {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 4px 0;
  color: #2c3e50;
}

.stat-content p {
  margin: 0 0 8px 0;
  color: #6c757d;
  font-size: 14px;
}

.stat-change {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 16px;
  background: #ecf0f1;
  color: #7f8c8d;
}

.stat-change.positive {
  background: #d5f4e6;
  color: #27ae60;
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-container h3 {
  margin-bottom: 16px;
  color: #2c3e50;
  font-size: 16px;
}

.chart-container canvas {
  height: 300px !important;
}

.activity-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.recent-users, .active-conversations {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-item, .conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ecf0f1;
}

.user-item:last-child, .conversation-item:last-child {
  border-bottom: none;
}

.conversation-item {
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f8f9fa;
  border-radius: 8px;
  margin: 0 -8px;
  padding: 12px 8px;
}

.user-info strong, .conv-info strong {
  display: block;
  color: #2c3e50;
  font-size: 14px;
}

.phone {
  color: #6c757d;
  font-size: 12px;
}

.last-message {
  color: #6c757d;
  font-size: 12px;
  margin: 4px 0 0 0;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
}

.status.free { background: #ecf0f1; color: #7f8c8d; }
.status.premium { background: #ffeaa7; color: #e17055; }
.status.pro { background: #fab1a0; color: #e17055; }
.status.trial { background: #81ecec; color: #00b894; }

.time {
  color: #6c757d;
  font-size: 11px;
}

.unread-badge {
  background: #e74c3c;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: bold;
  margin-left: 8px;
}

.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.action-btn {
  padding: 16px;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn.broadcast { background: #3498db; }
.action-btn.report { background: #e74c3c; }
.action-btn.export { background: #27ae60; }
.action-btn.settings { background: #6c757d; }
</style>
```

### 4. WhatsApp Users Management - src/views/WhatsAppUsers.vue

```vue
<template>
  <div class="whatsapp-users">
    <div class="page-header">
      <h1>
        <i class="fas fa-mobile-alt"></i>
        Usuários WhatsApp
      </h1>
      <div class="header-actions">
        <button @click="exportUsers" class="btn btn-secondary">
          <i class="fas fa-download"></i>
          Exportar
        </button>
        <button @click="sendBroadcast" class="btn btn-primary">
          <i class="fas fa-bullhorn"></i>
          Broadcast
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="filter-group">
          <label>Status da Assinatura</label>
          <select v-model="filters.subscription_status" @change="applyFilters">
            <option value="">Todos</option>
            <option value="free">Gratuito</option>
            <option value="premium">Premium</option>
            <option value="pro">Pro</option>
            <option value="trial">Trial</option>
            <option value="blocked">Bloqueado</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Período de Cadastro</label>
          <select v-model="filters.registration_period" @change="applyFilters">
            <option value="">Todos</option>
            <option value="today">Hoje</option>
            <option value="week">Última Semana</option>
            <option value="month">Último Mês</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Buscar</label>
          <input 
            v-model="filters.search" 
            @input="debounceSearch"
            type="text" 
            placeholder="Nome ou telefone..."
            class="search-input"
          >
        </div>

        <button @click="clearFilters" class="btn btn-outline">
          <i class="fas fa-times"></i>
          Limpar
        </button>
      </div>
    </div>

    <!-- Stats Summary -->
    <div class="stats-summary">
      <div class="stat-item">
        <span class="stat-number">{{ totalUsers }}</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ premiumUsers.length }}</span>
        <span class="stat-label">Premium</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ freeUsers.length }}</span>
        <span class="stat-label">Gratuito</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">R$ {{ monthlyRevenue }}</span>
        <span class="stat-label">Receita Mensal</span>
      </div>
    </div>

    <!-- Users Table -->
    <div class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>
              <input 
                type="checkbox" 
                v-model="selectAll" 
                @change="toggleSelectAll"
              >
            </th>
            <th>Usuário</th>
            <th>Telefone</th>
            <th>Status</th>
            <th>Plano</th>
            <th>Mensagens/Dia</th>
            <th>Última Atividade</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="user in whatsappStore.users" 
            :key="user.id"
            :class="{ selected: selectedUsers.includes(user.id) }"
          >
            <td>
              <input 
                type="checkbox" 
                :value="user.id"
                v-model="selectedUsers"
              >
            </td>
            <td>
              <div class="user-info">
                <div class="user-avatar">
                  {{ getInitials(user.display_name || user.phone_number) }}
                </div>
                <div>
                  <div class="user-name">
                    {{ user.display_name || 'Sem nome' }}
                  </div>
                  <div class="user-id">ID: {{ user.id }}</div>
                </div>
              </div>
            </td>
            <td>
              <span class="phone-number">{{ formatPhone(user.phone_number) }}</span>
            </td>
            <td>
              <span :class="`status-badge ${user.subscription_status}`">
                {{ getStatusLabel(user.subscription_status) }}
              </span>
            </td>
            <td>
              <span class="plan-info">
                {{ user.current_plan?.name || 'Nenhum' }}
                <span v-if="user.current_plan" class="plan-price">
                  R$ {{ user.current_plan.price }}
                </span>
              </span>
            </td>
            <td>
              <div class="usage-info">
                <span class="usage-count">{{ user.daily_queries_count }}</span>
                <div class="usage-bar">
                  <div 
                    class="usage-fill"
                    :style="{ width: getUsagePercentage(user) + '%' }"
                  ></div>
                </div>
              </div>
            </td>
            <td>
              <span class="last-activity">
                {{ formatDate(user.last_activity) }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button 
                  @click="openUserDetail(user)"
                  class="btn-icon btn-primary"
                  title="Ver detalhes"
                >
                  <i class="fas fa-eye"></i>
                </button>
                <button 
                  @click="sendMessage(user)"
                  class="btn-icon btn-success"
                  title="Enviar mensagem"
                >
                  <i class="fas fa-comment"></i>
                </button>
                <button 
                  @click="editSubscription(user)"
                  class="btn-icon btn-warning"
                  title="Editar assinatura"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button 
                  @click="blockUser(user)"
                  class="btn-icon btn-danger"
                  title="Bloquear usuário"
                >
                  <i class="fas fa-ban"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
      <div class="pagination-info">
        Mostrando {{ startItem }} a {{ endItem }} de {{ totalUsers }} usuários
      </div>
      <div class="pagination-controls">
        <button 
          @click="changePage(pagination.page - 1)"
          :disabled="pagination.page === 1"
          class="btn btn-outline"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <button 
          v-for="page in visiblePages"
          :key="page"
          @click="changePage(page)"
          :class="{ active: page === pagination.page }"
          class="btn btn-outline page-btn"
        >
          {{ page }}
        </button>
        
        <button 
          @click="changePage(pagination.page + 1)"
          :disabled="pagination.page === pagination.total_pages"
          class="btn btn-outline"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedUsers.length > 0" class="bulk-actions">
      <div class="bulk-info">
        {{ selectedUsers.length }} usuário(s) selecionado(s)
      </div>
      <div class="bulk-buttons">
        <button @click="bulkSendMessage" class="btn btn-primary">
          <i class="fas fa-comment"></i>
          Enviar Mensagem
        </button>
        <button @click="bulkUpdatePlan" class="btn btn-warning">
          <i class="fas fa-crown"></i>
          Alterar Plano
        </button>
        <button @click="bulkBlock" class="btn btn-danger">
          <i class="fas fa-ban"></i>
          Bloquear
        </button>
      </div>
    </div>

    <!-- Modals -->
    <UserDetailModal 
      v-if="showUserDetail"
      :user="selectedUser"
      @close="showUserDetail = false"
      @updated="refreshUsers"
    />

    <SendMessageModal
      v-if="showSendMessage"
      :users="messageTargetUsers"
      @close="showSendMessage = false"
      @sent="onMessageSent"
    />

    <EditSubscriptionModal
      v-if="showEditSubscription"
      :user="selectedUser"
      @close="showEditSubscription = false"
      @updated="refreshUsers"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useWhatsAppStore } from '@/stores/whatsapp'
import { debounce } from 'lodash'
import UserDetailModal from '@/components/WhatsApp/UserDetailModal.vue'
import SendMessageModal from '@/components/WhatsApp/SendMessageModal.vue'
import EditSubscriptionModal from '@/components/WhatsApp/EditSubscriptionModal.vue'

const whatsappStore = useWhatsAppStore()

// Reactive data
const filters = ref({
  subscription_status: '',
  registration_period: '',
  search: ''
})

const selectedUsers = ref<number[]>([])
const selectAll = ref(false)
const showUserDetail = ref(false)
const showSendMessage = ref(false)
const showEditSubscription = ref(false)
const selectedUser = ref(null)
const messageTargetUsers = ref([])

// Computed properties
const totalUsers = computed(() => whatsappStore.pagination.total_items)
const premiumUsers = computed(() => whatsappStore.premiumUsers)
const freeUsers = computed(() => whatsappStore.freeUsers)
const monthlyRevenue = computed(() => {
  return whatsappStore.premiumUsers.reduce((total, user) => {
    return total + (user.current_plan?.price || 0)
  }, 0).toFixed(2)
})

const pagination = computed(() => whatsappStore.pagination)
const startItem = computed(() => ((pagination.value.page - 1) * pagination.value.per_page) + 1)
const endItem = computed(() => Math.min(pagination.value.page * pagination.value.per_page, totalUsers.value))

const visiblePages = computed(() => {
  const current = pagination.value.page
  const total = pagination.value.total_pages
  const pages = []
  
  for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
onMounted(() => {
  refreshUsers()
})

const refreshUsers = async () => {
  await whatsappStore.fetchUsers(pagination.value.page, filters.value)
}

const applyFilters = () => {
  refreshUsers()
}

const debounceSearch = debounce(() => {
  applyFilters()
}, 500)

const clearFilters = () => {
  filters.value = {
    subscription_status: '',
    registration_period: '',
    search: ''
  }
  applyFilters()
}

const changePage = (page: number) => {
  whatsappStore.fetchUsers(page, filters.value)
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedUsers.value = whatsappStore.users.map(u => u.id)
  } else {
    selectedUsers.value = []
  }
}

const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const formatPhone = (phone: string) => {
  // Format Brazilian phone numbers
  return phone.replace(/(\+55)(\d{2})(\d{5})(\d{4})/, '$1 ($2) $3-$4')
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    free: 'Gratuito',
    premium: 'Premium',
    pro: 'Pro',
    trial: 'Trial',
    blocked: 'Bloqueado'
  }
  return labels[status] || status
}

const getUsagePercentage = (user: any) => {
  const limit = user.subscription_status === 'free' ? 5 : 100
  return Math.min((user.daily_queries_count / limit) * 100, 100)
}

const formatDate = (date: string) => {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

const openUserDetail = (user: any) => {
  selectedUser.value = user
  showUserDetail.value = true
}

const sendMessage = (user: any) => {
  messageTargetUsers.value = [user]
  showSendMessage.value = true
}

const editSubscription = (user: any) => {
  selectedUser.value = user
  showEditSubscription.value = true
}

const blockUser = async (user: any) => {
  if (confirm(`Tem certeza que deseja bloquear ${user.display_name || user.phone_number}?`)) {
    try {
      await whatsappStore.blockUser(user.id, 'Bloqueado pelo administrador')
      refreshUsers()
    } catch (error) {
      alert('Erro ao bloquear usuário')
    }
  }
}

const bulkSendMessage = () => {
  const users = whatsappStore.users.filter(u => selectedUsers.value.includes(u.id))
  messageTargetUsers.value = users
  showSendMessage.value = true
}

const bulkUpdatePlan = () => {
  // Implement bulk plan update
  console.log('Bulk update plan for:', selectedUsers.value)
}

const bulkBlock = () => {
  if (confirm(`Tem certeza que deseja bloquear ${selectedUsers.value.length} usuários?`)) {
    // Implement bulk block
    console.log('Bulk block:', selectedUsers.value)
  }
}

const exportUsers = () => {
  // Implement user export
  console.log('Export users')
}

const sendBroadcast = () => {
  // Open broadcast modal
  console.log('Send broadcast')
}

const onMessageSent = () => {
  showSendMessage.value = false
  selectedUsers.value = []
}

// Watch for selected users changes
watch(selectedUsers, (newVal) => {
  selectAll.value = newVal.length === whatsappStore.users.length && newVal.length > 0
})
</script>

<style scoped>
.whatsapp-users {
  padding: 24px;
  background: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  color: #25d366;
  font-size: 28px;
  margin: 0;
}

.page-header h1 i {
  margin-right: 12px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filters-row {
  display: flex;
  gap: 24px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 150px;
}

.filter-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
}

.filter-group select,
.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-input {
  min-width: 200px;
}

.stats-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.stat-item {
  background: white;
  border-radius: 8px;
  padding: 16px 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
  min-width: 120px;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
  text-transform: uppercase;
}

.users-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 24px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #ecf0f1;
}

.users-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.users-table tr:hover {
  background: #f8f9fa;
}

.users-table tr.selected {
  background: #e3f2fd;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #25d366;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
}

.user-name {
  font-weight: 500;
  color: #2c3e50;
}

.user-id {
  font-size: 11px;
  color: #6c757d;
}

.phone-number {
  font-family: monospace;
  color: #2c3e50;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
}

.status-badge.free { background: #ecf0f1; color: #7f8c8d; }
.status-badge.premium { background: #ffeaa7; color: #e17055; }
.status-badge.pro { background: #fab1a0; color: #e17055; }
.status-badge.trial { background: #81ecec; color: #00b894; }
.status-badge.blocked { background: #ff7675; color: white; }

.plan-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.plan-price {
  font-size: 11px;
  color: #6c757d;
}

.usage-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 60px;
}

.usage-count {
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
}

.usage-bar {
  width: 100%;
  height: 4px;
  background: #ecf0f1;
  border-radius: 2px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  background: #25d366;
  transition: width 0.3s ease;
}

.last-activity {
  color: #6c757d;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: opacity 0.2s;
}

.btn-icon:hover {
  opacity: 0.8;
}

.btn-icon.btn-primary { background: #3498db; }
.btn-icon.btn-success { background: #27ae60; }
.btn-icon.btn-warning { background: #f39c12; }
.btn-icon.btn-danger { background: #e74c3c; }

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pagination-info {
  color: #6c757d;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  gap: 4px;
}

.page-btn.active {
  background: #25d366;
  color: white;
}

.bulk-actions {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  gap: 24px;
  z-index: 1000;
}

.bulk-info {
  color: #2c3e50;
  font-weight: 500;
}

.bulk-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn.btn-primary { background: #3498db; color: white; }
.btn.btn-secondary { background: #6c757d; color: white; }
.btn.btn-success { background: #27ae60; color: white; }
.btn.btn-warning { background: #f39c12; color: white; }
.btn.btn-danger { background: #e74c3c; color: white; }
.btn.btn-outline { background: white; border: 1px solid #ddd; color: #6c757d; }

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn:disabled:hover {
  transform: none;
}
</style>
```

### 5. API Integration Service - src/services/whatsappApi.ts

```typescript
import axios from 'axios'

const API_BASE = '/api/whatsapp'

export interface WhatsAppApiResponse<T> {
  results: T[]
  page: number
  total_pages: number
  total_items: number
  per_page: number
}

export const whatsappApi = {
  // Users
  async getUsers(params: any): Promise<WhatsAppApiResponse<any>> {
    const response = await axios.get(`${API_BASE}/users/`, { params })
    return response.data
  },

  async getUserDetail(userId: number) {
    const response = await axios.get(`${API_BASE}/users/${userId}/`)
    return response.data
  },

  async updateUser(userId: number, data: any) {
    const response = await axios.patch(`${API_BASE}/users/${userId}/`, data)
    return response.data
  },

  async blockUser(userId: number, reason: string) {
    const response = await axios.patch(`${API_BASE}/users/${userId}/block/`, { reason })
    return response.data
  },

  async sendMessage(userId: number, message: string) {
    const response = await axios.post(`${API_BASE}/users/${userId}/send-message/`, { message })
    return response.data
  },

  // Conversations
  async getConversations(params: any) {
    const response = await axios.get(`${API_BASE}/conversations/`, { params })
    return response.data
  },

  async getConversation(conversationId: number) {
    const response = await axios.get(`${API_BASE}/conversations/${conversationId}/`)
    return response.data
  },

  async sendMessageToConversation(conversationId: number, message: string) {
    const response = await axios.post(`${API_BASE}/conversations/${conversationId}/messages/`, { message })
    return response.data
  },

  async updateConversationStatus(conversationId: number, status: string) {
    const response = await axios.patch(`${API_BASE}/conversations/${conversationId}/`, { status })
    return response.data
  },

  // Analytics
  async getDashboardStats() {
    const response = await axios.get(`${API_BASE}/stats/`)
    return response.data
  },

  async getAnalyticsData(params: any) {
    const response = await axios.get(`${API_BASE}/analytics/`, { params })
    return response.data
  },

  // Reports
  async generateReport(reportType: string, parameters: any) {
    const response = await axios.post(`${API_BASE}/reports/generate/`, {
      report_type: reportType,
      parameters
    })
    return response.data
  },

  async getReports(params: any) {
    const response = await axios.get(`${API_BASE}/reports/`, { params })
    return response.data
  },

  async downloadReport(reportId: number, format: 'pdf' | 'excel') {
    const response = await axios.get(`${API_BASE}/reports/${reportId}/${format}/`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Subscriptions
  async updateSubscription(userId: number, planId: number) {
    const response = await axios.patch(`${API_BASE}/users/${userId}/subscription/`, {
      plan_id: planId
    })
    return response.data
  },

  async getSubscriptionPlans() {
    const response = await axios.get(`${API_BASE}/plans/`)
    return response.data
  },

  // Settings
  async getSettings() {
    const response = await axios.get(`${API_BASE}/settings/`)
    return response.data
  },

  async updateSettings(settings: any) {
    const response = await axios.patch(`${API_BASE}/settings/`, settings)
    return response.data
  },

  // Broadcasts
  async sendBroadcast(message: string, userIds: number[], scheduleAt?: string) {
    const response = await axios.post(`${API_BASE}/broadcast/`, {
      message,
      user_ids: userIds,
      schedule_at: scheduleAt
    })
    return response.data
  },

  async getBroadcastHistory(params: any) {
    const response = await axios.get(`${API_BASE}/broadcasts/`, { params })
    return response.data
  }
}
```

## Expected Deliverables

1. **Complete Vue.js Integration:**
   - Navigation menu with WhatsApp section
   - 6 new WhatsApp management screens
   - Responsive components with consistent styling
   - Real-time data updates and notifications

2. **Enhanced Existing Screens:**
   - Dashboard.vue with WhatsApp widgets
   - GestaoClientes.vue with WhatsApp users tab
   - FinanceiroDashboard.vue with WhatsApp revenue tracking

3. **Advanced Features:**
   - User management with bulk actions
   - Real-time conversation monitoring
   - Analytics dashboards and reporting
   - Subscription management interface
   - Bot configuration and settings

4. **Integration Points:**
   - Pinia store for state management
   - TypeScript API service layer
   - Responsive design for all screen sizes
   - Real-time updates via WebSocket/polling

## Success Criteria

- Seamless integration with existing Vue.js architecture
- All WhatsApp management features accessible via web interface
- Real-time data synchronization between WhatsApp and admin panel
- Consistent UI/UX matching existing admin screens
- Complete user lifecycle management (registration to premium conversion)
- Comprehensive analytics and reporting capabilities
- Mobile-responsive design for management on-the-go

## Implementation Notes

This document provides complete Vue.js components that integrate with the WhatsApp backend APIs defined in documents 01-06. The frontend maintains the existing design patterns while adding comprehensive WhatsApp management capabilities.

All components use TypeScript, Composition API, and follow Vue 3 best practices. The styling matches the existing admin panel aesthetic while adding WhatsApp-specific design elements (green color scheme, appropriate icons).

The integration allows full management of the WhatsApp Business platform through the existing admin interface, maintaining the value of your current frontend investment while extending it for the new WhatsApp strategy.
