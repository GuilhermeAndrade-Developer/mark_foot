<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-chat</v-icon>
          Live Chat Dashboard
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerencie salas de chat, moderação e atividades em tempo real
        </p>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card elevation="2" color="primary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-forum</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.active_rooms || 0 }}</div>
                <div class="text-subtitle-2">Salas Ativas</div>
                <div class="text-caption">{{ stats.total_rooms || 0 }} total</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="success" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-account-group</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.total_active_users || 0 }}</div>
                <div class="text-subtitle-2">Usuários Online</div>
                <div class="text-caption">Agora</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="info" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-message</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.total_messages_today || 0 }}</div>
                <div class="text-subtitle-2">Mensagens Hoje</div>
                <div class="text-caption">{{ formatNumber(stats.total_messages_today || 0) }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="warning" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-flag</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.pending_reports || 0 }}</div>
                <div class="text-subtitle-2">Denúncias Pendentes</div>
                <div class="text-caption">{{ stats.flagged_messages || 0 }} flagadas</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Moderation Overview -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-shield-check</v-icon>
            Moderação Hoje
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title>Total de Ações</v-list-item-title>
                <template #append>
                  <v-chip color="primary" size="small">
                    {{ stats.moderation_stats?.actions_today || 0 }}
                  </v-chip>
                </template>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Avisos</v-list-item-title>
                <template #append>
                  <v-chip color="orange" size="small">
                    {{ stats.moderation_stats?.warnings_today || 0 }}
                  </v-chip>
                </template>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Banimentos</v-list-item-title>
                <template #append>
                  <v-chip color="red" size="small">
                    {{ stats.moderation_stats?.bans_today || 0 }}
                  </v-chip>
                </template>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Mensagens Deletadas</v-list-item-title>
                <template #append>
                  <v-chip color="grey" size="small">
                    {{ stats.moderation_stats?.message_deletions_today || 0 }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-chart-line</v-icon>
            Atividade das Últimas 24h
          </v-card-title>
          <v-card-text>
            <div class="chart-container" style="height: 250px;">
              <LineChart
                v-if="chartData.labels.length > 0"
                :data="chartData"
                :options="chartOptions"
              />
              <div v-else class="d-flex align-center justify-center" style="height: 250px;">
                <v-progress-circular indeterminate color="primary" />
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="primary"
                  block
                  size="large"
                  variant="outlined"
                  @click="router.push('/chat/rooms')"
                >
                  <v-icon start>mdi-forum</v-icon>
                  Gerenciar Salas
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="orange"
                  block
                  size="large"
                  variant="outlined"
                  @click="router.push('/chat/moderation')"
                >
                  <v-icon start>mdi-shield-check</v-icon>
                  Moderação
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="warning"
                  block
                  size="large"
                  variant="outlined"
                  @click="router.push('/chat/reports')"
                >
                  <v-icon start>mdi-flag</v-icon>
                  Denúncias ({{ stats.pending_reports || 0 }})
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="success"
                  block
                  size="large"
                  variant="outlined"
                  @click="createMatchRoom"
                >
                  <v-icon start>mdi-plus</v-icon>
                  Nova Sala
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Top Active Rooms & Recent Activity -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-trophy</v-icon>
            Salas Mais Ativas
          </v-card-title>
          <v-card-text>
            <v-list v-if="stats.top_rooms && stats.top_rooms.length">
              <v-list-item
                v-for="(room, index) in stats.top_rooms"
                :key="room.id"
              >
                <template #prepend>
                  <v-avatar
                    :color="getRoomTypeColor(room.room_type)"
                    size="32"
                    class="mr-3"
                  >
                    <v-icon color="white" size="16">
                      {{ getRoomTypeIcon(room.room_type) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ room.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ room.messages_today }} mensagens hoje • {{ room.active_users }} usuários ativos
                </v-list-item-subtitle>

                <template #append>
                  <v-chip size="small" :color="getRoomTypeColor(room.room_type)">
                    #{{ index + 1 }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              Nenhuma atividade encontrada
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-history</v-icon>
            Atividade Recente
          </v-card-title>
          <v-card-text>
            <v-list v-if="stats.recent_activity && stats.recent_activity.length">
              <v-list-item
                v-for="activity in stats.recent_activity"
                :key="activity.id"
              >
                <template #prepend>
                  <v-avatar
                    :color="getActivityColor(activity.action_type)"
                    size="32"
                    class="mr-3"
                  >
                    <v-icon color="white" size="16">
                      {{ getActivityIcon(activity.action_type) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ activity.moderator }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ getActivityDescription(activity) }}
                </v-list-item-subtitle>

                <template #append>
                  <v-chip size="small" variant="text">
                    {{ formatRelativeTime(activity.created_at) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              Nenhuma atividade recente
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create Room Dialog -->
    <v-dialog v-model="createRoomDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <v-icon class="mr-3">mdi-plus</v-icon>
          Criar Nova Sala de Chat
        </v-card-title>
        <v-card-text>
          <v-form ref="createRoomForm">
            <v-text-field
              v-model="newRoom.name"
              label="Nome da Sala"
              required
              :rules="[v => !!v || 'Nome é obrigatório']"
            />
            
            <v-textarea
              v-model="newRoom.description"
              label="Descrição"
              rows="3"
            />
            
            <v-select
              v-model="newRoom.room_type"
              label="Tipo de Sala"
              :items="roomTypes"
              required
              :rules="[v => !!v || 'Tipo é obrigatório']"
            />
            
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model.number="newRoom.max_users"
                  label="Máximo de Usuários"
                  type="number"
                  min="1"
                  max="10000"
                />
              </v-col>
              
              <v-col cols="6">
                <v-text-field
                  v-model.number="newRoom.rate_limit_messages"
                  label="Limite de Mensagens/min"
                  type="number"
                  min="1"
                  max="100"
                />
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="6">
                <v-switch
                  v-model="newRoom.auto_moderation"
                  label="Moderação Automática"
                  color="primary"
                />
              </v-col>
              
              <v-col cols="6">
                <v-switch
                  v-model="newRoom.profanity_filter"
                  label="Filtro de Palavrões"
                  color="primary"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="createRoomDialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="createRoom">Criar Sala</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="align-center justify-center"
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      />
    </v-overlay>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ChatApiService, { type ChatStats, type ChatRoom } from '@/services/chatApi'
import LineChart from '@/components/charts/LineChart.vue'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Router
const router = useRouter()

// Reactive data
const loading = ref(false)
const createRoomDialog = ref(false)
const stats = ref<ChatStats>({
  total_rooms: 0,
  active_rooms: 0,
  total_messages_today: 0,
  total_active_users: 0,
  pending_reports: 0,
  flagged_messages: 0,
  banned_users: 0,
  top_rooms: [],
  recent_activity: [],
  moderation_stats: {
    actions_today: 0,
    warnings_today: 0,
    bans_today: 0,
    message_deletions_today: 0
  },
  hourly_activity: []
})

const newRoom = ref({
  name: '',
  description: '',
  room_type: 'general',
  max_users: 1000,
  rate_limit_messages: 5,
  auto_moderation: true,
  profanity_filter: true
})

const roomTypes = [
  { title: 'Geral', value: 'general' },
  { title: 'Partida', value: 'match' },
  { title: 'Time', value: 'team' },
  { title: 'Admin', value: 'admin' }
]

// Chart data
const chartData = computed(() => {
  if (!stats.value.hourly_activity || stats.value.hourly_activity.length === 0) {
    return { labels: [], datasets: [] }
  }

  return {
    labels: stats.value.hourly_activity.map(item => item.hour),
    datasets: [
      {
        label: 'Mensagens por Hora',
        data: stats.value.hourly_activity.map(item => item.messages),
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        precision: 0
      }
    }
  }
}

// Methods
const loadStats = async () => {
  try {
    loading.value = true
    const data = await ChatApiService.getStats()
    stats.value = data
  } catch (error) {
    console.error('Erro ao carregar estatísticas do chat:', error)
  } finally {
    loading.value = false
  }
}

const createMatchRoom = () => {
  createRoomDialog.value = true
}

const createRoom = async () => {
  try {
    await ChatApiService.createRoom(newRoom.value)
    createRoomDialog.value = false
    
    // Reset form
    newRoom.value = {
      name: '',
      description: '',
      room_type: 'general',
      max_users: 1000,
      rate_limit_messages: 5,
      auto_moderation: true,
      profanity_filter: true
    }
    
    // Reload stats
    await loadStats()
  } catch (error) {
    console.error('Erro ao criar sala:', error)
  }
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('pt-BR').format(num)
}

const getRoomTypeColor = (type: string) => {
  switch (type) {
    case 'match': return 'green'
    case 'team': return 'blue'
    case 'admin': return 'purple'
    default: return 'grey'
  }
}

const getRoomTypeIcon = (type: string) => {
  switch (type) {
    case 'match': return 'mdi-soccer'
    case 'team': return 'mdi-shield'
    case 'admin': return 'mdi-shield-star'
    default: return 'mdi-forum'
  }
}

const getActivityColor = (type: string) => {
  switch (type) {
    case 'warn': return 'orange'
    case 'ban': return 'red'
    case 'kick': return 'deep-orange'
    case 'message_delete': return 'grey'
    case 'timeout': return 'amber'
    default: return 'primary'
  }
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'warn': return 'mdi-alert'
    case 'ban': return 'mdi-gavel'
    case 'kick': return 'mdi-exit-run'
    case 'message_delete': return 'mdi-delete'
    case 'timeout': return 'mdi-clock-alert'
    default: return 'mdi-shield-check'
  }
}

const getActivityDescription = (activity: any) => {
  const target = activity.target_user || 'mensagem'
  const action = getActionTranslation(activity.action_type)
  return `${action} ${target} em ${activity.room_name}`
}

const getActionTranslation = (action: string) => {
  switch (action) {
    case 'warn': return 'Alertou'
    case 'ban': return 'Baniu'
    case 'kick': return 'Expulsou'
    case 'message_delete': return 'Deletou mensagem de'
    case 'timeout': return 'Aplicou timeout em'
    default: return 'Moderou'
  }
}

const formatRelativeTime = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), { 
      addSuffix: true, 
      locale: ptBR 
    })
  } catch {
    return 'Agora'
  }
}

// Lifecycle
onMounted(() => {
  loadStats()
  
  // Auto-refresh every 30 seconds
  const interval = setInterval(loadStats, 30000)
  
  // Cleanup on unmount
  return () => clearInterval(interval)
})
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}

.text-h4 {
  font-size: 2rem !important;
}

.chart-container {
  position: relative;
}
</style>
