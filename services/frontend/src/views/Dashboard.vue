<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-view-dashboard</v-icon>
          Dashboard
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Visão geral dos dados de futebol
        </p>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col
        v-for="stat in stats"
        :key="stat.title"
        cols="12"
        sm="6"
        md="3"
      >
        <v-card
          :color="stat.color"
          dark
          elevation="2"
          class="text-center pa-4"
          :loading="loading"
        >
          <v-card-text class="pb-2">
            <v-icon
              :icon="stat.icon"
              size="48"
              class="mb-3"
            />
            <div class="text-h3 font-weight-bold mb-1">
              {{ stat.value || 0 }}
            </div>
            <div class="text-body-1">
              {{ stat.title }}
            </div>
            <v-chip
              v-if="stat.change"
              :color="stat.change > 0 ? 'success' : 'error'"
              size="small"
              class="mt-2"
            >
              <v-icon
                :icon="stat.change > 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
                size="16"
                class="mr-1"
              />
              {{ Math.abs(stat.change) }}%
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Main Content Row -->
    <v-row>
      <!-- Recent Matches -->
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-soccer</v-icon>
            Partidas Recentes
            <v-spacer />
            <v-btn
              color="primary"
              variant="text"
              size="small"
              @click="loadRecentMatches"
            >
              <v-icon class="mr-1">mdi-refresh</v-icon>
              Atualizar
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="recentMatches.length > 0">
              <v-list-item
                v-for="match in recentMatches"
                :key="match.id"
                class="mb-2"
              >
                <template #prepend>
                  <v-avatar
                    :image="match.home_team_crest"
                    size="32"
                    class="mr-2"
                  />
                </template>
                
                <v-list-item-title class="d-flex align-center">
                  <span class="text-body-1 font-weight-medium">
                    {{ match.home_team_name }}
                  </span>
                  
                  <v-chip
                    :color="getMatchStatusColor(match.status)"
                    size="small"
                    class="mx-3"
                  >
                    {{ formatMatchScore(match) }}
                  </v-chip>
                  
                  <span class="text-body-1 font-weight-medium">
                    {{ match.away_team_name }}
                  </span>
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  {{ match.competition_name }} • {{ formatDate(match.utc_date) }}
                </v-list-item-subtitle>
                
                <template #append>
                  <v-avatar
                    :image="match.away_team_crest"
                    size="32"
                    class="ml-2"
                  />
                </template>
              </v-list-item>
            </v-list>
            
            <v-alert
              v-else-if="!loading"
              type="info"
              variant="tonal"
              text="Nenhuma partida recente encontrada"
            />
            
            <div v-if="loading" class="text-center pa-6">
              <v-progress-circular
                indeterminate
                color="primary"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Top Scorers -->
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-trophy</v-icon>
            Top Artilheiros
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="topScorers.length > 0">
              <v-list-item
                v-for="(player, index) in topScorers"
                :key="player.player_name"
                class="mb-1"
              >
                <template #prepend>
                  <v-avatar
                    :color="index < 3 ? ['gold', 'silver', '#CD7F32'][index] : 'grey'"
                    size="32"
                    class="mr-2"
                  >
                    <span class="text-white font-weight-bold">
                      {{ index + 1 }}
                    </span>
                  </v-avatar>
                </template>
                
                <v-list-item-title class="text-body-2">
                  {{ player.player_name }}
                </v-list-item-title>
                
                <v-list-item-subtitle class="text-caption">
                  {{ player.team_name }}
                </v-list-item-subtitle>
                
                <template #append>
                  <v-chip
                    color="success"
                    size="small"
                  >
                    {{ player.total_goals }} gols
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            
            <v-alert
              v-else-if="!loading"
              type="info"
              variant="tonal"
              text="Nenhum artilheiro encontrado"
            />
          </v-card-text>
        </v-card>

        <!-- Quick Actions -->
        <v-card elevation="2" class="mt-4">
          <v-card-title>
            <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="action in quickActions"
                :key="action.title"
                :to="action.route"
                color="primary"
              >
                <template #prepend>
                  <v-icon :icon="action.icon" />
                </template>
                
                <v-list-item-title>{{ action.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ action.subtitle }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ApiService } from '@/services/api'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Reactive data
const loading = ref(false)
const stats = ref([
  {
    title: 'Times',
    value: 0,
    icon: 'mdi-shield-account',
    color: 'primary',
    change: 0
  },
  {
    title: 'Jogadores',
    value: 0,
    icon: 'mdi-account-group',
    color: 'success',
    change: 0
  },
  {
    title: 'Competições',
    value: 0,
    icon: 'mdi-trophy',
    color: 'warning',
    change: 0
  },
  {
    title: 'Partidas',
    value: 0,
    icon: 'mdi-soccer',
    color: 'info',
    change: 0
  }
])

const recentMatches = ref([])
const topScorers = ref([])

// Quick actions
const quickActions = [
  {
    title: 'Ver Times',
    subtitle: 'Explorar todos os times',
    icon: 'mdi-shield-account',
    route: '/teams'
  },
  {
    title: 'Buscar Jogadores',
    subtitle: 'Encontrar jogadores',
    icon: 'mdi-magnify',
    route: '/players'
  },
  {
    title: 'Últimas Partidas',
    subtitle: 'Resultados recentes',
    icon: 'mdi-soccer',
    route: '/matches'
  },
  {
    title: 'Classificação',
    subtitle: 'Tabelas de competições',
    icon: 'mdi-podium',
    route: '/standings'
  }
]

// Methods
const loadDashboardStats = async () => {
  try {
    loading.value = true
    const data = await ApiService.getDashboardStats()
    
    stats.value[0].value = data.total_teams
    stats.value[1].value = data.total_players
    stats.value[2].value = data.total_competitions
    stats.value[3].value = data.total_matches
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error)
  } finally {
    loading.value = false
  }
}

const loadRecentMatches = async () => {
  try {
    const data = await ApiService.getRecentMatches()
    recentMatches.value = data.slice(0, 5) // Mostrar apenas 5
  } catch (error) {
    console.error('Erro ao carregar partidas recentes:', error)
  }
}

const loadTopScorers = async () => {
  try {
    const data = await ApiService.getTopScorers()
    topScorers.value = data.slice(0, 5) // Mostrar apenas top 5
  } catch (error) {
    console.error('Erro ao carregar artilheiros:', error)
  }
}

const formatDate = (dateString: string) => {
  return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: ptBR })
}

const formatMatchScore = (match: any) => {
  if (match.status === 'FINISHED') {
    return `${match.home_team_score} x ${match.away_team_score}`
  }
  return match.status
}

const getMatchStatusColor = (status: string) => {
  switch (status) {
    case 'FINISHED':
      return 'success'
    case 'LIVE':
    case 'IN_PLAY':
      return 'error'
    case 'SCHEDULED':
      return 'primary'
    default:
      return 'grey'
  }
}

// Lifecycle
onMounted(() => {
  loadDashboardStats()
  loadRecentMatches()
  loadTopScorers()
})
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}
</style>
