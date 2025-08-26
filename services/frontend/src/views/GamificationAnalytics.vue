<template>
  <div class="gamification-analytics">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card class="gradient-primary pa-6">
          <div class="text-white">
            <h1 class="text-h4 font-weight-bold mb-2">
              📊 Analytics de Gamificação
            </h1>
            <p class="text-h6 mb-4 opacity-90">
              Relatórios detalhados de engajamento e performance
            </p>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Date Range Filter -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedPeriod"
          :items="periodOptions"
          label="Período"
          variant="outlined"
          @update:model-value="loadAnalytics"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="startDate"
          label="Data Início"
          type="date"
          variant="outlined"
          @change="loadAnalytics"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="endDate"
          label="Data Fim"
          type="date"
          variant="outlined"
          @change="loadAnalytics"
        />
      </v-col>
    </v-row>

    <!-- Key Metrics -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="primary" class="mb-2">mdi-account-multiple</v-icon>
          <div class="text-h4 font-weight-bold">{{ metrics.totalUsers }}</div>
          <div class="text-body-2 text-medium-emphasis">Usuários Ativos</div>
          <div class="text-caption text-success">
            +{{ metrics.userGrowth }}% vs período anterior
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="success" class="mb-2">mdi-gamepad-variant</v-icon>
          <div class="text-h4 font-weight-bold">{{ metrics.totalPredictions }}</div>
          <div class="text-body-2 text-medium-emphasis">Predições Feitas</div>
          <div class="text-caption text-success">
            +{{ metrics.predictionGrowth }}% vs período anterior
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="warning" class="mb-2">mdi-trophy</v-icon>
          <div class="text-h4 font-weight-bold">{{ metrics.completedChallenges }}</div>
          <div class="text-body-2 text-medium-emphasis">Challenges Concluídos</div>
          <div class="text-caption text-success">
            {{ metrics.challengeCompletionRate }}% taxa de conclusão
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="info" class="mb-2">mdi-clock-outline</v-icon>
          <div class="text-h4 font-weight-bold">{{ metrics.avgSessionTime }}</div>
          <div class="text-body-2 text-medium-emphasis">Tempo Médio de Sessão</div>
          <div class="text-caption text-success">
            +{{ metrics.sessionGrowth }}min vs período anterior
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Row 1 -->
    <v-row class="mb-6">
      <!-- User Engagement Chart -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Engajamento de Usuários
            <v-spacer />
            <v-btn-toggle v-model="engagementChartType" variant="outlined" density="compact">
              <v-btn value="daily" size="small">Diário</v-btn>
              <v-btn value="weekly" size="small">Semanal</v-btn>
              <v-btn value="monthly" size="small">Mensal</v-btn>
            </v-btn-toggle>
          </v-card-title>
          <v-card-text>
            <div class="chart-container">
              <canvas ref="engagementChart"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Top Challenges -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-trophy-variant</v-icon>
            Top Challenges
          </v-card-title>
          <v-card-text>
            <div v-for="challenge in topChallenges" :key="challenge.id" class="mb-3">
              <div class="d-flex justify-space-between align-center mb-1">
                <span class="text-subtitle-2">{{ challenge.title }}</span>
                <v-chip size="small" color="primary">{{ challenge.participants }}</v-chip>
              </div>
              <v-progress-linear 
                :model-value="challenge.completionRate" 
                height="6"
                color="success"
                class="mb-1"
              />
              <div class="text-caption text-medium-emphasis">
                {{ challenge.completionRate }}% taxa de conclusão
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Row 2 -->
    <v-row class="mb-6">
      <!-- Prediction Accuracy -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-target</v-icon>
            Precisão das Predições
          </v-card-title>
          <v-card-text>
            <div class="chart-container">
              <canvas ref="accuracyChart"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Badge Distribution -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-medal</v-icon>
            Distribuição de Badges
          </v-card-title>
          <v-card-text>
            <div class="chart-container">
              <canvas ref="badgeChart"></canvas>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Detailed Tables -->
    <v-row class="mb-6">
      <!-- User Leaderboard -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-podium</v-icon>
            Top Usuários por Pontos
            <v-spacer />
            <v-btn variant="text" size="small" @click="exportLeaderboard">
              <v-icon>mdi-download</v-icon>
              Exportar
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item 
                v-for="(user, index) in topUsers" 
                :key="user.id"
                class="px-0"
              >
                <template v-slot:prepend>
                  <v-avatar size="32" :color="getRankColor(index + 1)">
                    <span class="text-white font-weight-bold">#{{ index + 1 }}</span>
                  </v-avatar>
                </template>
                <v-list-item-title>{{ user.user.username }}</v-list-item-title>
                <v-list-item-subtitle>Level {{ user.level }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-chip size="small" color="success">{{ user.total_points }} pts</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Activity -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-history</v-icon>
            Atividade Recente
            <v-spacer />
            <v-btn variant="text" size="small" @click="refreshActivity">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-timeline density="compact" align="start">
              <v-timeline-item
                v-for="activity in recentActivity"
                :key="activity.id"
                size="small"
                :dot-color="getActivityColor(activity.type)"
              >
                <div class="d-flex justify-space-between">
                  <div>
                    <div class="text-body-2 font-weight-medium">{{ activity.description }}</div>
                    <div class="text-caption text-medium-emphasis">{{ activity.user }}</div>
                  </div>
                  <div class="text-caption text-medium-emphasis">{{ formatTime(activity.created_at) }}</div>
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Export Section -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-file-export</v-icon>
            Exportar Relatórios
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-btn 
                  color="primary" 
                  variant="outlined" 
                  @click="exportReport('users')"
                  block
                >
                  <v-icon left>mdi-account-group</v-icon>
                  Relatório de Usuários
                </v-btn>
              </v-col>
              <v-col cols="12" md="3">
                <v-btn 
                  color="success" 
                  variant="outlined" 
                  @click="exportReport('predictions')"
                  block
                >
                  <v-icon left>mdi-crystal-ball</v-icon>
                  Relatório de Predições
                </v-btn>
              </v-col>
              <v-col cols="12" md="3">
                <v-btn 
                  color="warning" 
                  variant="outlined" 
                  @click="exportReport('challenges')"
                  block
                >
                  <v-icon left>mdi-trophy</v-icon>
                  Relatório de Challenges
                </v-btn>
              </v-col>
              <v-col cols="12" md="3">
                <v-btn 
                  color="info" 
                  variant="outlined" 
                  @click="exportReport('engagement')"
                  block
                >
                  <v-icon left>mdi-chart-pie</v-icon>
                  Relatório de Engajamento
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useGamificationStore } from '@/stores/gamification'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import Chart from 'chart.js/auto'

const gamificationStore = useGamificationStore()

// Reactive data
const loading = ref(false)
const selectedPeriod = ref('30days')
const startDate = ref('')
const endDate = ref('')
const engagementChartType = ref('daily')

// Chart refs
const engagementChart = ref(null)
const accuracyChart = ref(null)
const badgeChart = ref(null)

// Chart instances
let engagementChartInstance = null
let accuracyChartInstance = null
let badgeChartInstance = null

// Analytics data
const metrics = ref({
  totalUsers: 0,
  userGrowth: 0,
  totalPredictions: 0,
  predictionGrowth: 0,
  completedChallenges: 0,
  challengeCompletionRate: 0,
  avgSessionTime: '0min',
  sessionGrowth: 0
})

const topChallenges = ref([])
const topUsers = ref([])
const recentActivity = ref([])

// Options
const periodOptions = [
  { title: 'Últimos 7 dias', value: '7days' },
  { title: 'Últimos 30 dias', value: '30days' },
  { title: 'Últimos 90 dias', value: '90days' },
  { title: 'Personalizado', value: 'custom' }
]

// Methods
const loadAnalytics = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadMetrics(),
      loadTopChallenges(),
      loadTopUsers(),
      loadRecentActivity()
    ])
    
    await nextTick()
    createCharts()
  } catch (error) {
    console.error('Error loading analytics:', error)
  } finally {
    loading.value = false
  }
}

const loadMetrics = async () => {
  // Mock data - replace with real API calls
  metrics.value = {
    totalUsers: 157,
    userGrowth: 12.5,
    totalPredictions: 1249,
    predictionGrowth: 23.1,
    completedChallenges: 89,
    challengeCompletionRate: 67,
    avgSessionTime: '12min',
    sessionGrowth: 3
  }
}

const loadTopChallenges = async () => {
  // Mock data
  topChallenges.value = [
    {
      id: 1,
      title: 'Novato das Predições',
      participants: 45,
      completionRate: 78
    },
    {
      id: 2,
      title: 'Mestre do Fantasy',
      participants: 32,
      completionRate: 65
    },
    {
      id: 3,
      title: 'Sequência Dourada',
      participants: 28,
      completionRate: 52
    }
  ]
}

const loadTopUsers = async () => {
  try {
    const profiles = await gamificationStore.getUserProfiles()
    topUsers.value = profiles.sort((a, b) => b.total_points - a.total_points).slice(0, 10)
  } catch (error) {
    console.error('Error loading top users:', error)
  }
}

const loadRecentActivity = async () => {
  // Mock recent activity
  recentActivity.value = [
    {
      id: 1,
      type: 'badge',
      description: 'Badge "Primeira Predição" conquistado',
      user: 'test_user_1',
      created_at: new Date().toISOString()
    },
    {
      id: 2,
      type: 'challenge',
      description: 'Challenge "Novato" completado',
      user: 'test_user_2',
      created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
    },
    {
      id: 3,
      type: 'level',
      description: 'Subiu para Level 3',
      user: 'test_user_3',
      created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString()
    }
  ]
}

const createCharts = () => {
  createEngagementChart()
  createAccuracyChart()
  createBadgeChart()
}

const createEngagementChart = () => {
  if (engagementChartInstance) {
    engagementChartInstance.destroy()
  }

  const ctx = engagementChart.value?.getContext('2d')
  if (!ctx) return

  const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
  const data = [65, 72, 80, 78, 85, 92]

  engagementChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Usuários Ativos',
        data,
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
}

const createAccuracyChart = () => {
  if (accuracyChartInstance) {
    accuracyChartInstance.destroy()
  }

  const ctx = accuracyChart.value?.getContext('2d')
  if (!ctx) return

  accuracyChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Acertos', 'Erros', 'Pendentes'],
      datasets: [{
        data: [68, 25, 7],
        backgroundColor: ['#4caf50', '#f44336', '#ff9800']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
}

const createBadgeChart = () => {
  if (badgeChartInstance) {
    badgeChartInstance.destroy()
  }

  const ctx = badgeChart.value?.getContext('2d')
  if (!ctx) return

  badgeChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Comum', 'Incomum', 'Raro', 'Épico', 'Lendário'],
      datasets: [{
        label: 'Badges Conquistados',
        data: [45, 23, 12, 6, 2],
        backgroundColor: ['#9e9e9e', '#4caf50', '#2196f3', '#9c27b0', '#ff9800']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  })
}

// Utility methods
const getRankColor = (rank: number) => {
  if (rank === 1) return 'yellow-darken-2'
  if (rank === 2) return 'grey'
  if (rank === 3) return 'orange-darken-2'
  return 'primary'
}

const getActivityColor = (type: string) => {
  const colors = {
    badge: 'warning',
    challenge: 'success',
    level: 'info',
    prediction: 'primary'
  }
  return colors[type] || 'grey'
}

const formatTime = (dateString: string) => {
  return format(new Date(dateString), "HH:mm", { locale: ptBR })
}

// Export methods
const exportReport = (type: string) => {
  console.log(`Exporting ${type} report...`)
  // Implementation would depend on the specific report type
}

const exportLeaderboard = () => {
  const csv = topUsers.value.map(user => 
    `${user.user.username},${user.level},${user.total_points}`
  ).join('\n')
  
  const blob = new Blob(['Username,Level,Points\n' + csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'leaderboard.csv'
  a.click()
  URL.revokeObjectURL(url)
}

const refreshActivity = async () => {
  await loadRecentActivity()
}

// Lifecycle
onMounted(async () => {
  // Set default dates
  const now = new Date()
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  
  startDate.value = thirtyDaysAgo.toISOString().split('T')[0]
  endDate.value = now.toISOString().split('T')[0]
  
  await loadAnalytics()
})
</script>

<style scoped>
.gradient-primary {
  background: linear-gradient(135deg, #1976d2, #42a5f5);
}

.gamification-analytics {
  padding: 0;
}

.chart-container {
  height: 300px;
  position: relative;
}
</style>
