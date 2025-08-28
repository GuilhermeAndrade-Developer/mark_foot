<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-forum</v-icon>
          Live Chat Dashboard
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Sistema de monitoramento e administração do Live Chat
        </p>
      </v-col>
    </v-row>

    <!-- Status Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card color="primary" variant="tonal" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-icon size="48" class="mb-3">mdi-forum</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.totalRooms }}</div>
            <div class="text-subtitle-1">Salas Totais</div>
            <div class="text-caption text-medium-emphasis">
              {{ stats.activeRooms }} ativas
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card color="success" variant="tonal" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-icon size="48" class="mb-3">mdi-message-text</v-icon>
            <div class="text-h4 font-weight-bold">{{ formatNumber(stats.totalMessages) }}</div>
            <div class="text-subtitle-1">Mensagens Hoje</div>
            <div class="text-caption text-medium-emphasis">
              +{{ stats.messageGrowth }}% vs ontem
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card color="info" variant="tonal" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-icon size="48" class="mb-3">mdi-account-group</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.activeUsers }}</div>
            <div class="text-subtitle-1">Usuários Ativos</div>
            <div class="text-caption text-medium-emphasis">
              Online agora
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card color="warning" variant="tonal" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-icon size="48" class="mb-3">mdi-shield-alert</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.pendingReports }}</div>
            <div class="text-subtitle-1">Denúncias Pendentes</div>
            <div class="text-caption text-medium-emphasis">
              Requer atenção
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Action Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-card elevation="2" class="h-100">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-door-open</v-icon>
            Gerenciar Salas
          </v-card-title>
          <v-card-text>
            <p>Crie, edite e configure salas de chat para partidas, times e discussões gerais.</p>
            <v-list class="mt-3">
              <v-list-item density="compact">
                <v-list-item-title>✓ Configurações de moderação</v-list-item-title>
              </v-list-item>
              <v-list-item density="compact">
                <v-list-item-title>✓ Limites de usuários</v-list-item-title>
              </v-list-item>
              <v-list-item density="compact">
                <v-list-item-title>✓ Criação automática para partidas</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
          <v-card-actions>
            <v-btn 
              color="primary" 
              variant="elevated"
              to="/chat/rooms"
              block
            >
              <v-icon class="mr-2">mdi-door-open</v-icon>
              Gerenciar Salas
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2" class="h-100">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-shield-check</v-icon>
            Moderação
          </v-card-title>
          <v-card-text>
            <p>Monitore mensagens, analise denúncias e gerencie usuários banidos.</p>
            <v-list class="mt-3">
              <v-list-item density="compact">
                <v-list-item-title>✓ Mensagens flagadas</v-list-item-title>
              </v-list-item>
              <v-list-item density="compact">
                <v-list-item-title>✓ Sistema de denúncias</v-list-item-title>
              </v-list-item>
              <v-list-item density="compact">
                <v-list-item-title>✓ Moderação automática</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
          <v-card-actions>
            <v-btn 
              color="orange" 
              variant="elevated"
              to="/chat/moderation"
              block
            >
              <v-icon class="mr-2">mdi-shield-check</v-icon>
              Ir para Moderação
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2" class="h-100">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-chart-line</v-icon>
            Analytics
          </v-card-title>
          <v-card-text>
            <p>Visualize métricas detalhadas e relatórios de desempenho do chat.</p>
            <v-list class="mt-3">
              <v-list-item density="compact">
                <v-list-item-title>✓ Atividade em tempo real</v-list-item-title>
              </v-list-item>
              <v-list-item density="compact">
                <v-list-item-title>✓ Relatórios de moderação</v-list-item-title>
              </v-list-item>
              <v-list-item density="compact">
                <v-list-item-title>✓ Estatísticas de engajamento</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
          <v-card-actions>
            <v-btn 
              color="success" 
              variant="elevated"
              block
              @click="loadAnalytics"
            >
              <v-icon class="mr-2">mdi-chart-line</v-icon>
              Ver Analytics
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Activity -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-clock-outline</v-icon>
            Atividade Recente
          </v-card-title>
          <v-card-text>
            <v-timeline density="compact">
              <v-timeline-item
                v-for="activity in recentActivity"
                :key="activity.id"
                :dot-color="getActivityColor(activity.type)"
                size="small"
              >
                <v-card variant="outlined">
                  <v-card-text class="py-2">
                    <div class="d-flex justify-space-between align-center">
                      <div>
                        <div class="font-weight-medium">{{ activity.description }}</div>
                        <div class="text-caption text-medium-emphasis">
                          {{ activity.user }} - {{ activity.room }}
                        </div>
                      </div>
                      <div class="text-caption">{{ activity.time }}</div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2" class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-fire</v-icon>
            Salas Mais Ativas
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="room in topRooms"
                :key="room.id"
                class="px-0"
              >
                <template #prepend>
                  <v-avatar :color="getRoomTypeColor(room.type)" size="32">
                    <v-icon color="white" size="16">
                      {{ getRoomTypeIcon(room.type) }}
                    </v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title>{{ room.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ room.messages }} mensagens
                </v-list-item-subtitle>
                
                <template #append>
                  <v-chip size="x-small" :color="getRoomTypeColor(room.type)">
                    {{ room.activeUsers }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Quick Actions -->
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          <v-card-text>
            <v-btn
              block
              color="primary"
              variant="outlined"
              class="mb-2"
              @click="createNewRoom"
            >
              <v-icon class="mr-2">mdi-plus</v-icon>
              Nova Sala
            </v-btn>
            
            <v-btn
              block
              color="orange"
              variant="outlined"
              class="mb-2"
              @click="viewReports"
            >
              <v-icon class="mr-2">mdi-flag</v-icon>
              Ver Denúncias
            </v-btn>
            
            <v-btn
              block
              color="red"
              variant="outlined"
              @click="viewBannedUsers"
            >
              <v-icon class="mr-2">mdi-account-cancel</v-icon>
              Usuários Banidos
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Status Info -->
    <v-row class="mt-4">
      <v-col>
        <v-alert
          type="info"
          variant="tonal"
          density="compact"
        >
          <div class="d-flex align-center">
            <v-icon class="mr-3">mdi-information</v-icon>
            <div>
              <strong>Sistema Live Chat:</strong> Implementação administrativa completa. 
              Ready para monitoramento e moderação de chats em tempo real.
              <v-chip class="ml-2" size="small" color="success">v1.0 Operacional</v-chip>
            </div>
          </div>
        </v-alert>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Demo data
const stats = ref({
  totalRooms: 5,
  activeRooms: 4,
  totalMessages: 1247,
  messageGrowth: 23,
  activeUsers: 89,
  pendingReports: 3
})

const recentActivity = ref([
  {
    id: 1,
    type: 'message',
    description: 'Nova mensagem flagada automaticamente',
    user: 'Sistema',
    room: 'Chat Geral',
    time: 'há 2 min'
  },
  {
    id: 2,
    type: 'moderation',
    description: 'Usuário advertido por spam',
    user: 'Admin',
    room: 'Real Madrid Fan Club',
    time: 'há 5 min'
  },
  {
    id: 3,
    type: 'room',
    description: 'Nova sala criada para partida',
    user: 'Sistema',
    room: 'Liverpool vs Arsenal',
    time: 'há 15 min'
  },
  {
    id: 4,
    type: 'report',
    description: 'Nova denúncia recebida',
    user: 'torcedor123',
    room: 'Premier League Chat',
    time: 'há 20 min'
  }
])

const topRooms = ref([
  {
    id: 1,
    name: 'Chat Geral',
    type: 'general',
    messages: 456,
    activeUsers: 23
  },
  {
    id: 2,
    name: 'Real Madrid Fan Club',
    type: 'team',
    messages: 289,
    activeUsers: 18
  },
  {
    id: 3,
    name: 'Premier League Chat',
    type: 'general',
    messages: 156,
    activeUsers: 12
  },
  {
    id: 4,
    name: 'Liverpool vs Arsenal',
    type: 'match',
    messages: 89,
    activeUsers: 8
  }
])

// Methods
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('pt-BR').format(num)
}

const getActivityColor = (type: string) => {
  switch (type) {
    case 'message': return 'blue'
    case 'moderation': return 'orange'
    case 'room': return 'green'
    case 'report': return 'red'
    default: return 'grey'
  }
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

const loadAnalytics = () => {
  // TODO: Navigate to analytics page
  console.log('Load analytics')
}

const createNewRoom = () => {
  // TODO: Open create room dialog
  console.log('Create new room')
}

const viewReports = () => {
  // TODO: Navigate to reports
  console.log('View reports')
}

const viewBannedUsers = () => {
  // TODO: Navigate to banned users
  console.log('View banned users')
}

// Lifecycle
onMounted(() => {
  console.log('Chat Dashboard loaded')
})
</script>

<style scoped>
.h-100 {
  height: 100%;
}

.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}
</style>
