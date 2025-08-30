<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-office-building</v-icon>
          Dashboard Empresarial
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Visão geral da gestão empresarial e performance de negócio
        </p>
      </v-col>
    </v-row>

    <!-- Business KPIs Cards -->
    <v-row class="mb-6">
      <v-col
        v-for="kpi in businessKPIs"
        :key="kpi.title"
        cols="12"
        sm="6"
        md="3"
      >
        <v-card
          :color="kpi.color"
          dark
          elevation="2"
          class="text-center pa-4"
          :loading="loading"
        >
          <v-card-text class="pb-2">
            <v-icon
              class="mb-3"
              :icon="kpi.icon"
              size="48"
            />
            <div class="text-h3 font-weight-bold mb-1">
              {{ kpi.value }}
            </div>
            <div class="text-body-1">
              {{ kpi.title }}
            </div>
            <v-chip
              class="mt-2"
              :color="kpi.trend > 0 ? 'success' : kpi.trend < 0 ? 'error' : 'warning'"
              size="small"
            >
              <v-icon 
                start 
                :icon="kpi.trend > 0 ? 'mdi-trending-up' : kpi.trend < 0 ? 'mdi-trending-down' : 'mdi-trending-neutral'"
              />
              {{ kpi.trend > 0 ? '+' : '' }}{{ kpi.trend }}%
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Performance Charts Section -->
    <v-row class="mb-6">
      <!-- User Growth -->
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-account-multiple-plus</v-icon>
            Crescimento de Usuários
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <LineChart
              :data="userGrowthData"
              :options="chartOptions"
              height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Revenue Distribution -->
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-cash-multiple</v-icon>
            Receita por Fonte
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <DoughnutChart
              :data="revenueData"
              :options="doughnutOptions"
              height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mb-6">
      <!-- System Performance -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-server-network</v-icon>
            Performance do Sistema
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <v-row>
              <v-col v-for="service in systemServices" :key="service.name" cols="12">
                <div class="d-flex align-center justify-space-between mb-3">
                  <div class="d-flex align-center">
                    <v-icon 
                      :icon="service.icon" 
                      :color="service.status === 'online' ? 'success' : 'error'"
                      class="mr-2"
                    />
                    <span class="font-weight-medium">{{ service.name }}</span>
                  </div>
                  <v-chip
                    :color="service.status === 'online' ? 'success' : 'error'"
                    size="small"
                  >
                    {{ service.status === 'online' ? 'Online' : 'Offline' }}
                  </v-chip>
                </div>
                <v-progress-linear
                  :model-value="service.performance"
                  :color="getPerformanceColor(service.performance)"
                  height="6"
                  rounded
                />
                <div class="text-caption mt-1">
                  Performance: {{ service.performance }}% | Uptime: {{ service.uptime }}%
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Social Media Engagement -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-thumb-up-outline</v-icon>
            Engajamento nas Redes
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <BarChart
              :data="socialEngagementData"
              :options="barChartOptions"
              height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Business Analytics Row -->
    <v-row>
      <!-- Active Users & Sessions -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-account-clock</v-icon>
            Usuários Ativos
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h4 font-weight-bold text-success">{{ activeUsers.online }}</div>
                  <div class="text-caption">Online Agora</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h4 font-weight-bold text-primary">{{ activeUsers.today }}</div>
                  <div class="text-caption">Hoje</div>
                </div>
              </v-col>
            </v-row>
            
            <v-divider class="my-4" />
            
            <div class="d-flex justify-space-between mb-2">
              <span>Usuários Premium</span>
              <span class="font-weight-bold">{{ premiumUsers.count }}</span>
            </div>
            <v-progress-linear
              :model-value="premiumUsers.percentage"
              color="warning"
              height="8"
              rounded
            />
            <div class="text-caption mt-1">
              {{ premiumUsers.percentage }}% dos usuários ativos
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Business Activities -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-timeline-clock</v-icon>
            Atividades Recentes
          </v-card-title>
          
          <v-card-text>
            <v-timeline density="compact" class="pa-0">
              <v-timeline-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :dot-color="activity.color"
                :icon="activity.icon"
                fill-dot
                size="small"
              >
                <div class="d-flex justify-space-between">
                  <div>
                    <div class="font-weight-medium">{{ activity.title }}</div>
                    <div class="text-caption text-medium-emphasis">{{ activity.description }}</div>
                  </div>
                  <div class="text-caption">{{ activity.time }}</div>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ApiService } from '@/services/api'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

// Reactive data
const loading = ref(false)

// Business KPIs
const businessKPIs = ref([
  {
    title: 'Usuários Ativos',
    value: '12.5K',
    icon: 'mdi-account-multiple',
    color: 'primary',
    trend: 15.2
  },
  {
    title: 'Usuários Premium',
    value: '1.8K',
    icon: 'mdi-crown',
    color: 'warning',
    trend: 8.5
  },
  {
    title: 'Receita Mensal',
    value: 'R$ 45K',
    icon: 'mdi-cash-multiple',
    color: 'success',
    trend: 22.1
  },
  {
    title: 'Uptime Sistema',
    value: '99.8%',
    icon: 'mdi-server-network',
    color: 'info',
    trend: 0.2
  }
])

// Active users data
const activeUsers = ref({
  online: 234,
  today: 2847
})

// Premium users data
const premiumUsers = ref({
  count: 1847,
  percentage: 14.5
})

// System services status
const systemServices = ref([
  {
    name: 'API Backend',
    icon: 'mdi-api',
    status: 'online',
    performance: 98,
    uptime: 99.8
  },
  {
    name: 'Database MySQL',
    icon: 'mdi-database',
    status: 'online',
    performance: 95,
    uptime: 99.9
  },
  {
    name: 'Redis Cache',
    icon: 'mdi-memory',
    status: 'online',
    performance: 97,
    uptime: 99.7
  },
  {
    name: 'Celery Workers',
    icon: 'mdi-worker',
    status: 'online',
    performance: 92,
    uptime: 99.5
  },
  {
    name: 'IA Services',
    icon: 'mdi-brain',
    status: 'online',
    performance: 89,
    uptime: 98.2
  }
])

// Recent business activities
const recentActivities = ref([
  {
    id: 1,
    title: 'Novo usuário premium',
    description: 'Usuário #12847 assinou plano Premium',
    time: '5 min',
    icon: 'mdi-crown',
    color: 'warning'
  },
  {
    id: 2,
    title: 'Pico de acessos',
    description: 'Maior número de usuários simultâneos hoje',
    time: '12 min',
    icon: 'mdi-trending-up',
    color: 'success'
  },
  {
    id: 3,
    title: 'Backup realizado',
    description: 'Backup automático do banco de dados',
    time: '1 hora',
    icon: 'mdi-backup-restore',
    color: 'info'
  },
  {
    id: 4,
    title: 'Nova partnership',
    description: 'Integração com clube local finalizada',
    time: '2 horas',
    icon: 'mdi-handshake',
    color: 'primary'
  },
  {
    id: 5,
    title: 'Meta de receita',
    description: 'Meta mensal de R$ 40K atingida',
    time: '1 dia',
    icon: 'mdi-target',
    color: 'success'
  }
])

// Chart data
const userGrowthData = ref({
  labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul'],
  datasets: [
    {
      label: 'Usuários Totais',
      data: [2400, 3200, 4100, 5800, 7200, 9500, 12500],
      borderColor: '#1976d2',
      backgroundColor: 'rgba(25, 118, 210, 0.1)',
      fill: true,
      tension: 0.4
    },
    {
      label: 'Usuários Premium',
      data: [120, 280, 450, 680, 920, 1350, 1800],
      borderColor: '#ff9800',
      backgroundColor: 'rgba(255, 152, 0, 0.1)',
      fill: true,
      tension: 0.4
    }
  ]
})

const revenueData = ref({
  labels: ['Assinaturas Premium', 'Partnerships', 'API Marketplace', 'Publicidade'],
  datasets: [
    {
      data: [65, 20, 10, 5],
      backgroundColor: [
        '#4caf50',
        '#2196f3',
        '#ff9800',
        '#9c27b0'
      ],
      borderColor: [
        '#388e3c',
        '#1976d2',
        '#f57c00',
        '#7b1fa2'
      ],
      borderWidth: 2
    }
  ]
})

const socialEngagementData = ref({
  labels: ['Instagram', 'TikTok', 'Twitter', 'Facebook', 'YouTube'],
  datasets: [
    {
      label: 'Engajamento (%)',
      data: [85, 92, 78, 65, 73],
      backgroundColor: [
        '#e91e63',
        '#000000',
        '#1da1f2',
        '#1877f2',
        '#ff0000'
      ],
      borderColor: [
        '#c2185b',
        '#333333',
        '#1976d2',
        '#1565c0',
        '#d32f2f'
      ],
      borderWidth: 1
    }
  ]
})

// Chart options
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  }
})

const doughnutOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
    },
  }
})

const barChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  }
})

// Methods
const getPerformanceColor = (performance: number) => {
  if (performance >= 95) return 'success'
  if (performance >= 80) return 'warning'
  return 'error'
}

const loadBusinessMetrics = async () => {
  try {
    loading.value = true
    
    // Carregar métricas reais da API (com fallback automático para demo)
    const metrics = await ApiService.getBusinessMetrics()
    
    // Atualizar KPIs
    businessKPIs.value[0].value = `${(metrics.activeUsers.today / 1000).toFixed(1)}K`
    businessKPIs.value[1].value = `${(metrics.premiumUsers.count / 1000).toFixed(1)}K`
    businessKPIs.value[2].value = `R$ ${(metrics.revenue.monthly / 1000).toFixed(0)}K`
    businessKPIs.value[3].value = `${metrics.systemUptime}%`
    
    // Atualizar dados de usuários ativos
    activeUsers.value = metrics.activeUsers
    
    // Atualizar dados de usuários premium
    premiumUsers.value = metrics.premiumUsers
    
    // Atualizar dados de serviços do sistema
    systemServices.value = metrics.services
    
    // Carregar dados dos gráficos
    const userGrowth = await ApiService.getUserGrowthData()
    userGrowthData.value = {
      labels: userGrowth.labels,
      datasets: [
        {
          label: 'Usuários Totais',
          data: userGrowth.totalUsers,
          borderColor: '#1976d2',
          backgroundColor: 'rgba(25, 118, 210, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Usuários Premium',
          data: userGrowth.premiumUsers,
          borderColor: '#ff9800',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    }
    
    // Carregar dados de receita
    const revenue = await ApiService.getRevenueData()
    revenueData.value = {
      labels: revenue.sources,
      datasets: [
        {
          data: revenue.values,
          backgroundColor: [
            '#4caf50',
            '#2196f3',
            '#ff9800',
            '#9c27b0'
          ],
          borderColor: [
            '#388e3c',
            '#1976d2',
            '#f57c00',
            '#7b1fa2'
          ],
          borderWidth: 2
        }
      ]
    }
    
    // Carregar dados de engajamento social
    const socialData = await ApiService.getSocialEngagementData()
    socialEngagementData.value = {
      labels: socialData.platforms,
      datasets: [
        {
          label: 'Engajamento (%)',
          data: socialData.engagement,
          backgroundColor: [
            '#e91e63',
            '#000000',
            '#1da1f2',
            '#1877f2',
            '#ff0000'
          ],
          borderColor: [
            '#c2185b',
            '#333333',
            '#1976d2',
            '#1565c0',
            '#d32f2f'
          ],
          borderWidth: 1
        }
      ]
    }
    
    // Carregar atividades recentes
    const activities = await ApiService.getBusinessActivities()
    recentActivities.value = activities
    
    console.log('Métricas de negócio carregadas com sucesso')
    
  } catch (error) {
    console.error('Erro ao carregar métricas de negócio:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadBusinessMetrics()
})
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}

.v-timeline {
  max-height: 300px;
  overflow-y: auto;
}
</style>
