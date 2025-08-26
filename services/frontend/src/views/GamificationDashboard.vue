<template>
  <div class="gamification-admin-dashboard">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card class="gradient-primary pa-6">
          <div class="text-white">
            <h1 class="text-h4 font-weight-bold mb-2">
              🎮 Painel de Gamificação
            </h1>
            <p class="text-h6 mb-4 opacity-90">
              Gerencie jogos, desafios e monitore o engajamento dos usuários
            </p>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Analytics Overview -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="primary" class="mb-2">mdi-account-group</v-icon>
          <div class="text-h4 font-weight-bold">{{ totalUsers }}</div>
          <div class="text-body-2 text-medium-emphasis">Usuários Ativos</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="success" class="mb-2">mdi-gamepad-variant</v-icon>
          <div class="text-h4 font-weight-bold">{{ totalPredictions }}</div>
          <div class="text-body-2 text-medium-emphasis">Predições Feitas</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="warning" class="mb-2">mdi-trophy</v-icon>
          <div class="text-h4 font-weight-bold">{{ activeChallenges }}</div>
          <div class="text-body-2 text-medium-emphasis">Desafios Ativos</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="info" class="mb-2">mdi-medal</v-icon>
          <div class="text-h4 font-weight-bold">{{ totalBadges }}</div>
          <div class="text-body-2 text-medium-emphasis">Badges Criados</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions -->
    <v-row class="mb-6">
      <v-col cols="12">
        <h2 class="text-h5 font-weight-bold mb-4">Ações Administrativas</h2>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-4 text-center hover-card" @click="openCreateGameDialog">
              <v-icon size="48" color="primary" class="mb-2">mdi-plus-circle</v-icon>
              <div class="text-h6 font-weight-bold">Criar Jogo</div>
              <div class="text-body-2 text-medium-emphasis">
                Novo jogo de predição
              </div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-4 text-center hover-card" @click="openCreateChallengeDialog">
              <v-icon size="48" color="success" class="mb-2">mdi-trophy-variant</v-icon>
              <div class="text-h6 font-weight-bold">Criar Desafio</div>
              <div class="text-body-2 text-medium-emphasis">
                Novo challenge temporário
              </div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-4 text-center hover-card" @click="openCreateBadgeDialog">
              <v-icon size="48" color="warning" class="mb-2">mdi-medal</v-icon>
              <div class="text-h6 font-weight-bold">Criar Badge</div>
              <div class="text-body-2 text-medium-emphasis">
                Nova conquista
              </div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-4 text-center hover-card" @click="goToAnalytics">
              <v-icon size="48" color="info" class="mb-2">mdi-chart-line</v-icon>
              <div class="text-h6 font-weight-bold">Analytics</div>
              <div class="text-body-2 text-medium-emphasis">
                Relatórios detalhados
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <v-row>
      <!-- Top Users -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-crown</v-icon>
            Top Usuários por Pontos
            <v-spacer />
            <v-btn variant="text" size="small" @click="goToUserManagement">
              Gerenciar Usuários
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-4">
              <v-progress-circular indeterminate size="32" />
            </div>
            <div v-else>
              <v-list dense>
                <v-list-item 
                  v-for="(user, index) in topUsers" 
                  :key="user.id"
                  class="px-0"
                >
                  <template v-slot:prepend>
                    <v-avatar size="32" color="primary">
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
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Activity -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-clock-outline</v-icon>
            Atividade Recente
            <v-spacer />
            <v-btn variant="text" size="small" @click="refreshActivityFeed">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-4">
              <v-progress-circular indeterminate size="32" />
            </div>
            <div v-else>
              <v-timeline density="compact" align="start">
                <v-timeline-item
                  v-for="activity in recentActivity"
                  :key="activity.id"
                  size="small"
                  dot-color="primary"
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
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Engagement Analytics -->
    <v-row class="mt-6">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-trending-up</v-icon>
            Métricas de Engajamento
            <v-spacer />
            <v-btn variant="text" size="small" @click="goToAnalytics">
              Relatório Completo
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="loading" class="text-center py-4">
              <v-progress-circular indeterminate size="32" />
            </div>
            <div v-else>
              <v-row dense>
                <v-col cols="6">
                  <div class="text-center pa-2">
                    <div class="text-h6 font-weight-bold text-success">{{ engagementStats?.daily_active || 0 }}</div>
                    <div class="text-caption">Usuários Ativos (Hoje)</div>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="text-center pa-2">
                    <div class="text-h6 font-weight-bold text-info">{{ engagementStats?.weekly_active || 0 }}</div>
                    <div class="text-caption">Ativos (7 dias)</div>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="text-center pa-2">
                    <div class="text-h6 font-weight-bold text-warning">{{ engagementStats?.avg_session_time || '0min' }}</div>
                    <div class="text-caption">Tempo Médio</div>
                  </div>
                </v-col>
                <v-col cols="6">
                  <div class="text-center pa-2">
                    <div class="text-h6 font-weight-bold text-error">{{ engagementStats?.challenge_completion_rate || '0%' }}</div>
                    <div class="text-caption">Taxa Conclusão</div>
                  </div>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- System Status -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-server</v-icon>
            Status do Sistema
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item class="px-0">
                <template v-slot:prepend>
                  <v-icon color="success">mdi-check-circle</v-icon>
                </template>
                <v-list-item-title>API de Gamificação</v-list-item-title>
                <v-list-item-subtitle>Online</v-list-item-subtitle>
              </v-list-item>
              <v-list-item class="px-0">
                <template v-slot:prepend>
                  <v-icon color="success">mdi-check-circle</v-icon>
                </template>
                <v-list-item-title>Banco de Dados</v-list-item-title>
                <v-list-item-subtitle>Conectado</v-list-item-subtitle>
              </v-list-item>
              <v-list-item class="px-0">
                <template v-slot:prepend>
                  <v-icon color="warning">mdi-alert-circle</v-icon>
                </template>
                <v-list-item-title>Cache</v-list-item-title>
                <v-list-item-subtitle>Limpeza necessária</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create Game Dialog -->
    <v-dialog v-model="showCreateGameDialog" max-width="600">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2">mdi-plus-circle</v-icon>
          Criar Novo Jogo de Predição
        </v-card-title>
        <v-card-text>
          <v-form ref="gameForm" v-model="gameFormValid">
            <v-text-field
              v-model="newGame.name"
              label="Nome do Jogo"
              :rules="[v => !!v || 'Nome é obrigatório']"
              required
            />
            <v-textarea
              v-model="newGame.description"
              label="Descrição"
              :rules="[v => !!v || 'Descrição é obrigatória']"
              required
            />
            <v-select
              v-model="newGame.game_type"
              :items="gameTypes"
              item-title="text"
              item-value="value"
              label="Tipo do Jogo"
              required
            />
            <v-text-field
              v-model.number="newGame.entry_fee_points"
              label="Taxa de Entrada (Pontos)"
              type="number"
              min="0"
            />
            <v-text-field
              v-model.number="newGame.reward_multiplier"
              label="Multiplicador de Recompensa"
              type="number"
              step="0.1"
              min="1"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showCreateGameDialog = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            :disabled="!gameFormValid"
            :loading="creating"
            @click="createGame"
          >
            Criar Jogo
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Create Challenge Dialog -->
    <v-dialog v-model="showCreateChallengeDialog" max-width="600">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2">mdi-trophy-variant</v-icon>
          Criar Novo Desafio
        </v-card-title>
        <v-card-text>
          <v-form ref="challengeForm" v-model="challengeFormValid">
            <v-text-field
              v-model="newChallenge.title"
              label="Título do Desafio"
              :rules="[v => !!v || 'Título é obrigatório']"
              required
            />
            <v-textarea
              v-model="newChallenge.description"
              label="Descrição"
              :rules="[v => !!v || 'Descrição é obrigatória']"
              required
            />
            <v-select
              v-model="newChallenge.challenge_type"
              :items="challengeTypes"
              item-title="text"
              item-value="value"
              label="Tipo do Desafio"
              required
            />
            <v-text-field
              v-model.number="newChallenge.points_reward"
              label="Recompensa em Pontos"
              type="number"
              min="0"
            />
            <v-text-field
              v-model.number="newChallenge.max_participants"
              label="Máximo de Participantes"
              type="number"
              min="1"
            />
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="newChallenge.start_date"
                  label="Data de Início"
                  type="datetime-local"
                  required
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="newChallenge.end_date"
                  label="Data de Fim"
                  type="datetime-local"
                  required
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showCreateChallengeDialog = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            :disabled="!challengeFormValid"
            :loading="creating"
            @click="createChallenge"
          >
            Criar Desafio
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Create Badge Dialog -->
    <v-dialog v-model="showCreateBadgeDialog" max-width="600">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2">mdi-medal</v-icon>
          Criar Novo Badge
        </v-card-title>
        <v-card-text>
          <v-form ref="badgeForm" v-model="badgeFormValid">
            <v-text-field
              v-model="newBadge.name"
              label="Nome do Badge"
              :rules="[v => !!v || 'Nome é obrigatório']"
              required
            />
            <v-textarea
              v-model="newBadge.description"
              label="Descrição"
              :rules="[v => !!v || 'Descrição é obrigatória']"
              required
            />
            <v-select
              v-model="newBadge.badge_type"
              :items="badgeTypes"
              item-title="text"
              item-value="value"
              label="Tipo do Badge"
              required
            />
            <v-select
              v-model="newBadge.rarity"
              :items="rarityLevels"
              item-title="text"
              item-value="value"
              label="Raridade"
              required
            />
            <v-text-field
              v-model="newBadge.icon_url"
              label="URL do Ícone"
              placeholder="https://..."
            />
            <v-text-field
              v-model.number="newBadge.points_reward"
              label="Recompensa em Pontos"
              type="number"
              min="0"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showCreateBadgeDialog = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            :disabled="!badgeFormValid"
            :loading="creating"
            @click="createBadge"
          >
            Criar Badge
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGamificationStore } from '@/stores/gamification'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const router = useRouter()
const gamificationStore = useGamificationStore()
const authStore = useAuthStore()

// Reactive data
const loading = ref(false)
const creating = ref(false)

// Dialog states
const showCreateGameDialog = ref(false)
const showCreateChallengeDialog = ref(false)
const showCreateBadgeDialog = ref(false)

// Form validation
const gameFormValid = ref(false)
const challengeFormValid = ref(false)
const badgeFormValid = ref(false)

// Admin statistics (these would come from API in real implementation)
const totalUsers = ref(0)
const totalPredictions = ref(0)
const activeChallenges = ref(0)
const totalBadges = ref(0)
const topUsers = ref([])
const recentActivity = ref([])
const engagementStats = ref({
  daily_active: 0,
  weekly_active: 0,
  avg_session_time: '0min',
  challenge_completion_rate: '0%'
})

// Form data
const newGame = ref({
  name: '',
  description: '',
  game_type: 'match_result',
  entry_fee_points: 0,
  reward_multiplier: 2.0
})

const newChallenge = ref({
  title: '',
  description: '',
  challenge_type: 'prediction',
  points_reward: 100,
  max_participants: 1000,
  start_date: '',
  end_date: ''
})

const newBadge = ref({
  name: '',
  description: '',
  badge_type: 'prediction',
  rarity: 'common',
  icon_url: '',
  points_reward: 50
})

// Select options
const gameTypes = [
  { text: 'Resultado da Partida', value: 'match_result' },
  { text: 'Placar Exato', value: 'exact_score' },
  { text: 'Rodada Semanal', value: 'weekly_round' },
  { text: 'Torneio', value: 'tournament' }
]

const challengeTypes = [
  { text: 'Predição', value: 'prediction' },
  { text: 'Fantasy', value: 'fantasy' },
  { text: 'Sequência', value: 'streak' },
  { text: 'Social', value: 'social' }
]

const badgeTypes = [
  { text: 'Predição', value: 'prediction' },
  { text: 'Fantasy', value: 'fantasy' },
  { text: 'Social', value: 'social' },
  { text: 'Sequência', value: 'streak' },
  { text: 'Especial', value: 'special' }
]

const rarityLevels = [
  { text: 'Comum', value: 'common' },
  { text: 'Incomum', value: 'uncommon' },
  { text: 'Raro', value: 'rare' },
  { text: 'Épico', value: 'epic' },
  { text: 'Lendário', value: 'legendary' }
]

// Methods
const loadDashboardData = async () => {
  loading.value = true
  try {
    // In a real implementation, these would be separate API calls
    await Promise.all([
      loadUserStats(),
      loadTopUsers(),
      loadRecentActivity(),
      loadEngagementStats()
    ])
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const loadUserStats = async () => {
  try {
    // Mock data - replace with real API calls
    totalUsers.value = 157
    totalPredictions.value = 1249
    activeChallenges.value = 6
    totalBadges.value = 15
  } catch (error) {
    console.error('Error loading user stats:', error)
  }
}

const loadTopUsers = async () => {
  try {
    // This would come from gamification API
    const profiles = await gamificationStore.getUserProfiles()
    topUsers.value = profiles.slice(0, 5)
  } catch (error) {
    console.error('Error loading top users:', error)
  }
}

const loadRecentActivity = async () => {
  try {
    // Mock recent activity data
    recentActivity.value = [
      {
        id: 1,
        description: 'Novo badge conquistado: Primeira Predição',
        user: 'test_user_1',
        created_at: new Date().toISOString()
      },
      {
        id: 2,
        description: 'Desafio "Novato das Predições" iniciado',
        user: 'admin',
        created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
      },
      {
        id: 3,
        description: 'Usuário subiu para Level 2',
        user: 'test_user_2',
        created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString()
      }
    ]
  } catch (error) {
    console.error('Error loading recent activity:', error)
  }
}

const loadEngagementStats = async () => {
  try {
    // Mock engagement data
    engagementStats.value = {
      daily_active: 45,
      weekly_active: 127,
      avg_session_time: '12min',
      challenge_completion_rate: '67%'
    }
  } catch (error) {
    console.error('Error loading engagement stats:', error)
  }
}

// Dialog methods
const openCreateGameDialog = () => {
  // Reset form
  newGame.value = {
    name: '',
    description: '',
    game_type: 'match_result',
    entry_fee_points: 0,
    reward_multiplier: 2.0
  }
  showCreateGameDialog.value = true
}

const openCreateChallengeDialog = () => {
  // Reset form and set default dates
  const now = new Date()
  const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000)
  const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  
  newChallenge.value = {
    title: '',
    description: '',
    challenge_type: 'prediction',
    points_reward: 100,
    max_participants: 1000,
    start_date: tomorrow.toISOString().slice(0, 16),
    end_date: nextWeek.toISOString().slice(0, 16)
  }
  showCreateChallengeDialog.value = true
}

const openCreateBadgeDialog = () => {
  // Reset form
  newBadge.value = {
    name: '',
    description: '',
    badge_type: 'prediction',
    rarity: 'common',
    icon_url: '',
    points_reward: 50
  }
  showCreateBadgeDialog.value = true
}

// Creation methods
const createGame = async () => {
  creating.value = true
  try {
    await gamificationStore.createPredictionGame({
      ...newGame.value,
      starts_at: new Date().toISOString(),
      ends_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
    })
    showCreateGameDialog.value = false
    await loadDashboardData()
  } catch (error) {
    console.error('Error creating game:', error)
  } finally {
    creating.value = false
  }
}

const createChallenge = async () => {
  creating.value = true
  try {
    await gamificationStore.createChallenge({
      ...newChallenge.value,
      status: 'active',
      requirements: {},
      is_active: true
    })
    showCreateChallengeDialog.value = false
    await loadDashboardData()
  } catch (error) {
    console.error('Error creating challenge:', error)
  } finally {
    creating.value = false
  }
}

const createBadge = async () => {
  creating.value = true
  try {
    await gamificationStore.createBadge(newBadge.value)
    showCreateBadgeDialog.value = false
    await loadDashboardData()
  } catch (error) {
    console.error('Error creating badge:', error)
  } finally {
    creating.value = false
  }
}

// Navigation methods
const goToAnalytics = () => router.push('/gamification/analytics')
const goToUserManagement = () => router.push('/gamification/users')

// Utility methods
const formatTime = (dateString: string) => {
  return format(new Date(dateString), "HH:mm", { locale: ptBR })
}

const refreshActivityFeed = async () => {
  await loadRecentActivity()
}

// Lifecycle
onMounted(async () => {
  await loadDashboardData()
})
</script>

<style scoped>
.gradient-primary {
  background: linear-gradient(135deg, #1976d2, #42a5f5);
}

.hover-card {
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.gamification-admin-dashboard {
  padding: 0;
}

.v-card {
  transition: box-shadow 0.3s ease;
}

.v-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.text-h4 {
  color: white;
}

.text-h6 {
  color: white;
}
</style>
