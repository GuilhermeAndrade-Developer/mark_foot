<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-soccer</v-icon>
          Dashboard de Futebol
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Análise completa dos dados e estatísticas de futebol
        </p>
      </v-col>
    </v-row>

    <!-- Football Statistics Cards -->
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
              class="mb-3"
              :icon="stat.icon"
              size="48"
            />
            <div class="text-h3 font-weight-bold mb-1">
              {{ stat.value }}
            </div>
            <div class="text-body-1">
              {{ stat.title }}
            </div>
            <v-chip
              class="mt-2"
              :color="stat.change > 0 ? 'success' : stat.change < 0 ? 'error' : 'warning'"
              size="small"
            >
              <v-icon 
                start 
                :icon="stat.change > 0 ? 'mdi-trending-up' : stat.change < 0 ? 'mdi-trending-down' : 'mdi-trending-neutral'"
              />
              {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}%
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
            Análise de Gols por Rodada
          </v-card-title>
          
          <v-divider />
          
          <v-card-text>
            <LineChart
              :data="goalsChartData"
              :options="chartOptions"
              height="300"
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
              :options="chartOptions"
              height="300"
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
              :options="doughnutOptions"
              height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Top Scorers -->
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-trophy-award</v-icon>
            Top Artilheiros
          </v-card-title>
          
          <v-divider />
          
          <v-card-text v-if="topScorers.length === 0" class="text-center pa-8">
            <v-icon size="64" color="grey-lighten-1">mdi-soccer</v-icon>
            <div class="text-h6 mt-4 text-medium-emphasis">
              Dados de artilheiros não disponíveis
            </div>
            <div class="text-body-2 text-medium-emphasis">
              Os dados serão atualizados em breve
            </div>
          </v-card-text>
          
          <v-list v-else density="compact">
            <v-list-item
              v-for="(scorer, index) in topScorers.slice(0, 5)"
              :key="scorer.id"
              class="px-0"
            >
              <template #prepend>
                <v-avatar
                  :color="index === 0 ? 'warning' : index === 1 ? 'grey' : index === 2 ? 'brown' : 'primary'"
                  size="32"
                >
                  <span class="text-white font-weight-bold">{{ index + 1 }}</span>
                </v-avatar>
              </template>
              
              <v-list-item-title>{{ scorer.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ scorer.team }}</v-list-item-subtitle>
              
              <template #append>
                <v-chip color="success" size="small">
                  {{ scorer.goals }} gols
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
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="recentMatches.length > 0">
              <v-list-item
                v-for="match in recentMatches"
                :key="match.id"
                class="px-0 mb-2"
              >
                <v-card
                  class="w-100"
                  variant="outlined"
                >
                  <v-card-text class="pa-3">
                    <div class="d-flex align-center justify-space-between">
                      <div class="d-flex align-center">
                        <div class="text-center mr-4">
                          <div class="text-body-2 font-weight-medium">{{ match.home_team_name }}</div>
                          <div class="text-caption text-medium-emphasis">Casa</div>
                        </div>
                        
                        <div class="text-center mx-4">
                          <div class="text-h6 font-weight-bold">
                            {{ formatMatchScore(match) }}
                          </div>
                          <v-chip
                            :color="getMatchStatusColor(match.status)"
                            size="x-small"
                          >
                            {{ match.status }}
                          </v-chip>
                        </div>
                        
                        <div class="text-center ml-4">
                          <div class="text-body-2 font-weight-medium">{{ match.away_team_name }}</div>
                          <div class="text-caption text-medium-emphasis">Visitante</div>
                        </div>
                      </div>
                      
                      <div class="text-right">
                        <div class="text-caption">{{ formatDate(match.utc_date) }}</div>
                        <div class="text-caption text-medium-emphasis">{{ match.competition_name }}</div>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-list-item>
            </v-list>
            
            <div v-else class="text-center pa-8">
              <v-icon size="64" color="grey-lighten-1">mdi-soccer</v-icon>
              <div class="text-h6 mt-4 text-medium-emphasis">
                Nenhuma partida recente encontrada
              </div>
              <div class="text-body-2 text-medium-emphasis">
                Os dados de partidas serão atualizados automaticamente
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Side Panel -->
      <v-col cols="12" md="4">
        <!-- AI Predictions -->
        <v-card elevation="2" class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-brain</v-icon>
            Predições IA
          </v-card-title>
          
          <v-card-text>
            <div class="text-center pa-4">
              <v-icon size="48" color="primary">mdi-robot</v-icon>
              <div class="text-body-1 mt-2">Sistema de IA ativo</div>
              <div class="text-caption text-medium-emphasis">
                8 modelos de machine learning funcionando
              </div>
              <v-btn
                color="primary"
                variant="outlined"
                size="small"
                class="mt-3"
                @click="$router.push('/ai-dashboard')"
              >
                Ver Análises IA
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- Quick Actions -->
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="action in quickActions"
                :key="action.title"
                :prepend-icon="action.icon"
                :title="action.title"
                :subtitle="action.subtitle"
                @click="$router.push(action.route)"
                class="mb-2"
              >
                <template #append>
                  <v-icon>mdi-chevron-right</v-icon>
                </template>
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
      beginAtZero: true
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
