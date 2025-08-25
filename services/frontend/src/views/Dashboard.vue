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

    <!-- Charts Section -->
    <v-row class="mb-6">
      <!-- Goals Analysis -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Gols por Rodada
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <LineChart
              :data="goalsChartData"
              :height="250"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Team Performance -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-bar</v-icon>
            Performance dos Times
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <BarChart
              :data="teamPerformanceData"
              :height="250"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mb-6">
      <!-- Match Results Distribution -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-donut</v-icon>
            Distribuição de Resultados
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <DoughnutChart
              :data="matchResultsData"
              :height="250"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Top Scorers -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-trophy</v-icon>
            Artilheiros
          </v-card-title>
          
          <v-divider />
          
          <v-card-text v-if="topScorers.length === 0" class="text-center pa-8">
            <v-icon size="48" color="grey-lighten-1">mdi-account-star</v-icon>
            <p class="text-subtitle-1 mt-2">Nenhum artilheiro encontrado</p>
          </v-card-text>
          
          <v-list v-else density="compact">
            <v-list-item
              v-for="(player, index) in topScorers"
              :key="player.id"
              class="px-0"
            >
              <template #prepend>
                <v-chip
                  :color="index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'orange' : 'grey'"
                  size="small"
                  class="mr-3"
                >
                  {{ index + 1 }}
                </v-chip>
                <v-avatar size="32" class="mr-3">
                  <v-img
                    :src="player.photo_url || '/placeholder-player.png'"
                    :alt="player.name"
                  />
                </v-avatar>
              </template>
              
              <v-list-item-title class="font-weight-medium">
                {{ player.name }}
              </v-list-item-title>
              
              <v-list-item-subtitle>
                {{ player.team?.name }}
              </v-list-item-subtitle>
              
              <template #append>
                <v-chip
                  color="primary"
                  size="small"
                  variant="flat"
                >
                  {{ player.goals || 0 }} gols
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
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
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

// Reactive data
const loading = ref(false)
const topScorers = ref([])
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

// Chart data
const goalsChartData = ref({
  labels: ['Rodada 1', 'Rodada 2', 'Rodada 3', 'Rodada 4', 'Rodada 5'],
  datasets: [
    {
      label: 'Gols por Rodada',
      data: [12, 19, 15, 25, 22],
      borderColor: '#1976d2',
      backgroundColor: 'rgba(25, 118, 210, 0.1)',
      fill: true,
      tension: 0.4
    }
  ]
})

const teamPerformanceData = ref({
  labels: ['Vitórias', 'Empates', 'Derrotas'],
  datasets: [
    {
      label: 'Resultados',
      data: [0, 0, 0],
      backgroundColor: [
        '#4caf50',
        '#ff9800',
        '#f44336'
      ],
      borderColor: [
        '#388e3c',
        '#f57c00',
        '#d32f2f'
      ],
      borderWidth: 1
    }
  ]
})

const matchResultsData = ref({
  labels: ['Vitórias Casa', 'Empates', 'Vitórias Fora'],
  datasets: [
    {
      data: [0, 0, 0],
      backgroundColor: [
        '#1976d2',
        '#ffc107',
        '#e91e63'
      ],
      borderColor: [
        '#1565c0',
        '#ff8f00',
        '#c2185b'
      ],
      borderWidth: 2
    }
  ]
})

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

const updateChartData = async () => {
  try {
    // Atualizar dados dos gráficos com dados reais da API
    const matchesData = await ApiService.getMatches({ limit: 50 })
    const matches = matchesData.results || matchesData

    // Calcular distribuição de resultados
    const homeWins = matches.filter(m => m.status === 'FINISHED' && (m.home_score || 0) > (m.away_score || 0)).length
    const draws = matches.filter(m => m.status === 'FINISHED' && (m.home_score || 0) === (m.away_score || 0)).length
    const awayWins = matches.filter(m => m.status === 'FINISHED' && (m.home_score || 0) < (m.away_score || 0)).length

    matchResultsData.value.datasets[0].data = [homeWins, draws, awayWins]

    // Calcular performance geral dos times
    const totalFinished = homeWins + draws + awayWins
    if (totalFinished > 0) {
      teamPerformanceData.value.datasets[0].data = [
        homeWins + awayWins, // Total de vitórias
        draws, // Empates
        totalFinished - (homeWins + awayWins + draws) // Derrotas (se houver dados inconsistentes)
      ]
    }

    // Simular dados de gols por rodada (pode ser melhorado com dados reais)
    const goalsPerRound = [
      Math.floor(Math.random() * 20) + 10,
      Math.floor(Math.random() * 20) + 10,
      Math.floor(Math.random() * 20) + 10,
      Math.floor(Math.random() * 20) + 10,
      Math.floor(Math.random() * 20) + 10
    ]
    goalsChartData.value.datasets[0].data = goalsPerRound

  } catch (error) {
    console.error('Erro ao atualizar dados dos gráficos:', error)
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
  updateChartData()
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
