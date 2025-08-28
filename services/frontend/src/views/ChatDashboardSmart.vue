<template>
  <div class="chat-dashboard">
    <!-- System Status Card -->
    <SystemStatus />

    <!-- Dashboard Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Chat Dashboard</h1>
        <p class="text-body-1 text-medium-emphasis">
          Sistema de gerenciamento de chat ao vivo
        </p>
      </div>
      
      <v-btn
        color="primary"
        prepend-icon="mdi-refresh"
        @click="refreshData"
        :loading="loading"
      >
        Atualizar Dados
      </v-btn>
    </div>

    <!-- Quick Stats -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="stats-card">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h5 font-weight-bold">{{ stats?.total_rooms || 0 }}</div>
                <div class="text-body-2 text-medium-emphasis">Total de Salas</div>
              </div>
              <v-icon color="primary" size="40">mdi-chat</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="stats-card">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h5 font-weight-bold">{{ stats?.active_rooms || 0 }}</div>
                <div class="text-body-2 text-medium-emphasis">Salas Ativas</div>
              </div>
              <v-icon color="success" size="40">mdi-chat-processing</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="stats-card">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h5 font-weight-bold">{{ stats?.total_messages_today || 0 }}</div>
                <div class="text-body-2 text-medium-emphasis">Mensagens Hoje</div>
              </div>
              <v-icon color="info" size="40">mdi-message-text</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="stats-card">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h5 font-weight-bold">{{ stats?.total_active_users || 0 }}</div>
                <div class="text-body-2 text-medium-emphasis">Usuários Ativos</div>
              </div>
              <v-icon color="warning" size="40">mdi-account-group</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Action Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-card
          class="action-card h-100"
          @click="$router.push('/chat/rooms')"
          hover
        >
          <v-card-text class="text-center">
            <v-icon color="primary" size="48" class="mb-3">mdi-chat-plus</v-icon>
            <div class="text-h6 font-weight-medium mb-2">Gerenciar Salas</div>
            <div class="text-body-2 text-medium-emphasis">
              Criar, editar e configurar salas de chat
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card
          class="action-card h-100"
          @click="$router.push('/chat/moderation')"
          hover
        >
          <v-card-text class="text-center">
            <v-icon color="warning" size="48" class="mb-3">mdi-shield-account</v-icon>
            <div class="text-h6 font-weight-medium mb-2">Moderação</div>
            <div class="text-body-2 text-medium-emphasis">
              Revisar reportes e gerenciar usuários
            </div>
            <v-chip
              v-if="(stats?.pending_reports || 0) > 0"
              color="error"
              size="small"
              class="mt-2"
            >
              {{ stats?.pending_reports }} pendentes
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="action-card h-100" hover>
          <v-card-text class="text-center">
            <v-icon color="info" size="48" class="mb-3">mdi-chart-line</v-icon>
            <div class="text-h6 font-weight-medium mb-2">Estatísticas</div>
            <div class="text-body-2 text-medium-emphasis">
              Relatórios de uso e atividade
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts and Recent Activity -->
    <v-row>
      <!-- Hourly Activity Chart -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-bar</v-icon>
            Atividade por Hora (Últimas 24h)
          </v-card-title>
          <v-card-text>
            <canvas ref="activityChart" style="max-height: 300px;"></canvas>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Activity -->
      <v-col cols="12" lg="4">
        <v-card class="h-100">
          <v-card-title>
            <v-icon class="mr-2">mdi-history</v-icon>
            Atividade Recente
          </v-card-title>
          <v-card-text>
            <div v-if="!stats?.recent_activity?.length" class="text-center text-medium-emphasis">
              <v-icon size="48" class="mb-2">mdi-history</v-icon>
              <div>Nenhuma atividade recente</div>
            </div>
            
            <v-timeline v-else density="compact" size="small">
              <v-timeline-item
                v-for="activity in stats.recent_activity"
                :key="activity.id"
                size="small"
                :dot-color="getActivityColor(activity.action_type)"
              >
                <div class="text-body-2">
                  <strong>{{ activity.moderator }}</strong>
                  {{ getActivityDescription(activity) }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  {{ formatTimeAgo(activity.created_at) }}
                </div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Top Rooms -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-trophy</v-icon>
            Salas Mais Ativas Hoje
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col
                v-for="room in stats?.top_rooms || []"
                :key="room.id"
                cols="12"
                md="4"
              >
                <v-card variant="outlined" class="pa-3">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <div class="text-subtitle-1 font-weight-medium">{{ room.name }}</div>
                    <v-chip
                      :color="getRoomTypeColor(room.room_type)"
                      size="small"
                      variant="flat"
                    >
                      {{ getRoomTypeLabel(room.room_type) }}
                    </v-chip>
                  </div>
                  
                  <div class="d-flex justify-space-between text-body-2">
                    <div>
                      <v-icon size="small" class="mr-1">mdi-message</v-icon>
                      {{ room.messages_today }} msgs
                    </div>
                    <div>
                      <v-icon size="small" class="mr-1">mdi-account-group</v-icon>
                      {{ room.active_users }} usuários
                    </div>
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import chatApiService, { type ChatStats } from '@/services/chatApiSmart'
import SystemStatus from '@/components/chat/SystemStatus.vue'

Chart.register(...registerables)

// Reactive state
const stats = ref<ChatStats | null>(null)
const loading = ref(false)
const activityChart = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

// Methods
const loadStats = async () => {
  try {
    loading.value = true
    stats.value = await chatApiService.getStats()
    
    // Update chart after stats are loaded
    nextTick(() => {
      updateChart()
    })
  } catch (error) {
    console.error('Error loading chat stats:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadStats()
}

const updateChart = () => {
  if (!activityChart.value || !stats.value?.hourly_activity) return

  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }

  const ctx = activityChart.value.getContext('2d')
  if (!ctx) return

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: stats.value.hourly_activity.map(item => item.hour),
      datasets: [{
        label: 'Mensagens',
        data: stats.value.hourly_activity.map(item => item.messages),
        borderColor: 'rgb(33, 150, 243)',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
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
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      }
    }
  })
}

const getActivityColor = (actionType: string): string => {
  switch (actionType) {
    case 'message': return 'info'
    case 'moderation': return 'warning'
    case 'ban': return 'error'
    case 'warning': return 'orange'
    default: return 'grey'
  }
}

const getActivityDescription = (activity: any): string => {
  switch (activity.action_type) {
    case 'message':
      return `flagou mensagem em ${activity.room_name}`
    case 'moderation':
      return `moderou ${activity.target_user} em ${activity.room_name}`
    case 'ban':
      return `baniu ${activity.target_user}`
    case 'warning':
      return `advertiu ${activity.target_user}`
    default:
      return activity.reason || 'realizou ação'
  }
}

const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (minutes < 1) return 'agora'
  if (minutes < 60) return `${minutes}m atrás`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h atrás`
  
  const days = Math.floor(hours / 24)
  return `${days}d atrás`
}

const getRoomTypeColor = (type: string): string => {
  switch (type) {
    case 'match': return 'success'
    case 'team': return 'primary'
    case 'general': return 'info'
    case 'admin': return 'warning'
    default: return 'grey'
  }
}

const getRoomTypeLabel = (type: string): string => {
  switch (type) {
    case 'match': return 'Partida'
    case 'team': return 'Time'
    case 'general': return 'Geral'
    case 'admin': return 'Admin'
    default: return type
  }
}

// Lifecycle
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stats-card {
  height: 100%;
}

.action-card {
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
}

.action-card:hover {
  transform: translateY(-2px);
}

.h-100 {
  height: 100%;
}
</style>
