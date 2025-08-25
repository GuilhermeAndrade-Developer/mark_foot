<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-soccer</v-icon>
          Partidas
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Acompanhe resultados e próximos jogos
        </p>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedCompetition"
              :items="competitions"
              item-title="name"
              item-value="id"
              label="Competição"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedTeam"
              :items="teams"
              item-title="name"
              item-value="id"
              label="Time"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="2">
            <v-text-field
              v-model="dateFrom"
              type="date"
              label="Data inicial"
              variant="outlined"
              density="compact"
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="2">
            <v-text-field
              v-model="dateTo"
              type="date"
              label="Data final"
              variant="outlined"
              density="compact"
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="2">
            <v-select
              v-model="selectedStatus"
              :items="statusOptions"
              item-title="text"
              item-value="value"
              label="Status"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Status Tabs -->
    <v-tabs
      v-model="activeTab"
      class="mb-6"
      color="primary"
      @update:model-value="onTabChange"
    >
      <v-tab value="upcoming">
        <v-icon start>mdi-calendar-clock</v-icon>
        Próximas ({{ upcomingCount }})
      </v-tab>
      <v-tab value="live">
        <v-icon start>mdi-circle" class="live-indicator</v-icon>
        Ao Vivo ({{ liveCount }})
      </v-tab>
      <v-tab value="finished">
        <v-icon start>mdi-check-circle</v-icon>
        Finalizadas ({{ finishedCount }})
      </v-tab>
    </v-tabs>

    <!-- Loading -->
    <v-card v-if="loading" class="text-center pa-12">
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      />
      <p class="mt-4 text-subtitle-1">Carregando partidas...</p>
    </v-card>

    <!-- Matches List -->
    <div v-else>
      <v-row>
        <v-col
          v-for="match in filteredMatches"
          :key="match.id"
          cols="12"
        >
          <v-card
            elevation="2"
            class="match-card"
            :class="getMatchCardClass(match)"
          >
            <v-card-text class="pa-4">
              <v-row align="center">
                <!-- Competition and Date -->
                <v-col cols="12" sm="3">
                  <div class="text-center">
                    <v-chip
                      :color="getCompetitionColor(match.competition)"
                      size="small"
                      class="mb-2"
                    >
                      {{ match.competition?.name || 'Liga' }}
                    </v-chip>
                    <div class="text-body-2 text-medium-emphasis">
                      {{ formatMatchDate(match.match_date) }}
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      {{ formatMatchTime(match.match_date) }}
                    </div>
                    <v-chip
                      v-if="match.matchday"
                      variant="tonal"
                      size="x-small"
                      class="mt-1"
                    >
                      Rodada {{ match.matchday }}
                    </v-chip>
                  </div>
                </v-col>

                <!-- Teams and Score -->
                <v-col cols="12" sm="6">
                  <div class="d-flex align-center justify-center">
                    <!-- Home Team -->
                    <div class="text-center flex-grow-1">
                      <v-avatar
                        :image="match.home_team?.logo_url"
                        size="48"
                        class="mb-2"
                      >
                        <v-icon>mdi-shield</v-icon>
                      </v-avatar>
                      <div class="text-subtitle-2 font-weight-medium">
                        {{ match.home_team?.name || 'Casa' }}
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        {{ match.home_team?.short_name }}
                      </div>
                    </div>

                    <!-- Score or VS -->
                    <div class="text-center mx-4">
                      <div v-if="match.status === 'FINISHED'" class="score-display">
                        <span class="text-h4 font-weight-bold">
                          {{ match.home_score ?? 0 }}
                        </span>
                        <span class="mx-2 text-h6">-</span>
                        <span class="text-h4 font-weight-bold">
                          {{ match.away_score ?? 0 }}
                        </span>
                      </div>
                      <div v-else-if="match.status === 'LIVE'" class="score-display">
                        <v-chip color="error" size="small" class="mb-2">
                          <v-icon start class="live-indicator">mdi-circle</v-icon>
                          AO VIVO
                        </v-chip>
                        <div>
                          <span class="text-h4 font-weight-bold">
                            {{ match.home_score ?? 0 }}
                          </span>
                          <span class="mx-2 text-h6">-</span>
                          <span class="text-h4 font-weight-bold">
                            {{ match.away_score ?? 0 }}
                          </span>
                        </div>
                        <div v-if="match.minute" class="text-caption">
                          {{ match.minute }}'
                        </div>
                      </div>
                      <div v-else class="vs-display">
                        <span class="text-h5 text-medium-emphasis">VS</span>
                      </div>
                    </div>

                    <!-- Away Team -->
                    <div class="text-center flex-grow-1">
                      <v-avatar
                        :image="match.away_team?.logo_url"
                        size="48"
                        class="mb-2"
                      >
                        <v-icon>mdi-shield</v-icon>
                      </v-avatar>
                      <div class="text-subtitle-2 font-weight-medium">
                        {{ match.away_team?.name || 'Fora' }}
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        {{ match.away_team?.short_name }}
                      </div>
                    </div>
                  </div>
                </v-col>

                <!-- Status and Actions -->
                <v-col cols="12" sm="3">
                  <div class="text-center">
                    <v-chip
                      :color="getStatusColor(match.status)"
                      size="small"
                      class="mb-3"
                    >
                      {{ getStatusText(match.status) }}
                    </v-chip>
                    
                    <div v-if="match.venue" class="text-caption text-medium-emphasis mb-2">
                      <v-icon size="12" class="mr-1">mdi-map-marker</v-icon>
                      {{ match.venue }}
                    </div>
                    
                    <div class="d-flex justify-center gap-1">
                      <v-btn
                        size="small"
                        variant="text"
                        icon
                        @click="viewMatchDetails(match)"
                      >
                        <v-icon>mdi-eye</v-icon>
                        <v-tooltip activator="parent">Ver Detalhes</v-tooltip>
                      </v-btn>
                      
                      <v-btn
                        v-if="match.status === 'FINISHED'"
                        size="small"
                        variant="text"
                        icon
                        @click="viewMatchStats(match)"
                      >
                        <v-icon>mdi-chart-line</v-icon>
                        <v-tooltip activator="parent">Estatísticas</v-tooltip>
                      </v-btn>
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- No Results -->
      <v-card
        v-if="filteredMatches.length === 0"
        class="text-center pa-12"
      >
        <v-icon
          size="64"
          color="grey-lighten-1"
          class="mb-4"
        >
          mdi-soccer-field
        </v-icon>
        <h3 class="text-h6 mb-2">Nenhuma partida encontrada</h3>
        <p class="text-body-2 text-medium-emphasis">
          Tente ajustar os filtros de busca
        </p>
      </v-card>
    </div>

    <!-- Match Details Dialog -->
    <v-dialog
      v-model="detailsDialog"
      max-width="800"
    >
      <v-card v-if="selectedMatch">
        <v-card-title class="d-flex align-center bg-primary">
          <div class="text-white">
            <div class="text-h6">{{ selectedMatch.competition?.name }}</div>
            <div class="text-subtitle-2">
              {{ formatMatchDate(selectedMatch.match_date) }} - 
              {{ formatMatchTime(selectedMatch.match_date) }}
            </div>
          </div>
        </v-card-title>
        
        <!-- Match Header -->
        <v-card-text class="pa-6">
          <div class="d-flex align-center justify-center mb-6">
            <div class="text-center flex-grow-1">
              <v-avatar size="80" class="mb-3">
                <v-img
                  :src="selectedMatch.home_team?.logo_url"
                  :alt="selectedMatch.home_team?.name"
                />
              </v-avatar>
              <div class="text-h6 font-weight-bold">
                {{ selectedMatch.home_team?.name }}
              </div>
            </div>

            <div class="text-center mx-6">
              <div v-if="selectedMatch.status === 'FINISHED'" class="score-display">
                <div class="text-h2 font-weight-bold mb-2">
                  {{ selectedMatch.home_score ?? 0 }} - {{ selectedMatch.away_score ?? 0 }}
                </div>
                <v-chip color="success" size="small">
                  FINALIZADA
                </v-chip>
              </div>
              <div v-else-if="selectedMatch.status === 'LIVE'" class="score-display">
                <v-chip color="error" class="mb-2">
                  <v-icon start class="live-indicator">mdi-circle</v-icon>
                  AO VIVO
                </v-chip>
                <div class="text-h2 font-weight-bold">
                  {{ selectedMatch.home_score ?? 0 }} - {{ selectedMatch.away_score ?? 0 }}
                </div>
              </div>
              <div v-else>
                <div class="text-h4 text-medium-emphasis mb-2">VS</div>
                <v-chip :color="getStatusColor(selectedMatch.status)" size="small">
                  {{ getStatusText(selectedMatch.status) }}
                </v-chip>
              </div>
            </div>

            <div class="text-center flex-grow-1">
              <v-avatar size="80" class="mb-3">
                <v-img
                  :src="selectedMatch.away_team?.logo_url"
                  :alt="selectedMatch.away_team?.name"
                />
              </v-avatar>
              <div class="text-h6 font-weight-bold">
                {{ selectedMatch.away_team?.name }}
              </div>
            </div>
          </div>

          <!-- Match Details -->
          <v-row>
            <v-col cols="6">
              <strong>Competição:</strong><br>
              {{ selectedMatch.competition?.name || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Rodada:</strong><br>
              {{ selectedMatch.matchday || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Local:</strong><br>
              {{ selectedMatch.venue || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Árbitro:</strong><br>
              {{ selectedMatch.referee || 'N/A' }}
            </v-col>
            <v-col v-if="selectedMatch.attendance" cols="6">
              <strong>Público:</strong><br>
              {{ formatNumber(selectedMatch.attendance) }}
            </v-col>
            <v-col v-if="selectedMatch.duration" cols="6">
              <strong>Duração:</strong><br>
              {{ selectedMatch.duration }} min
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-btn
            v-if="selectedMatch.status === 'FINISHED'"
            color="primary"
            variant="text"
            @click="viewMatchStats(selectedMatch)"
          >
            <v-icon start>mdi-chart-line</v-icon>
            Ver Estatísticas
          </v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            @click="detailsDialog = false"
          >
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ApiService } from '@/services/api'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Reactive data
const loading = ref(false)
const matches = ref([])
const competitions = ref([])
const teams = ref([])
const selectedCompetition = ref(null)
const selectedTeam = ref(null)
const dateFrom = ref('')
const dateTo = ref('')
const selectedStatus = ref(null)
const activeTab = ref('upcoming')
const detailsDialog = ref(false)
const selectedMatch = ref(null)

// Status options
const statusOptions = [
  { text: 'Agendada', value: 'SCHEDULED' },
  { text: 'Ao Vivo', value: 'LIVE' },
  { text: 'Pausada', value: 'PAUSED' },
  { text: 'Finalizada', value: 'FINISHED' },
  { text: 'Adiada', value: 'POSTPONED' },
  { text: 'Cancelada', value: 'CANCELLED' }
]

// Computed properties
const filteredMatches = computed(() => {
  let filtered = matches.value

  switch (activeTab.value) {
    case 'upcoming':
      filtered = filtered.filter(m => ['SCHEDULED', 'POSTPONED'].includes(m.status))
      break
    case 'live':
      filtered = filtered.filter(m => ['LIVE', 'PAUSED'].includes(m.status))
      break
    case 'finished':
      filtered = filtered.filter(m => m.status === 'FINISHED')
      break
  }

  return filtered.sort((a, b) => {
    const dateA = new Date(a.match_date)
    const dateB = new Date(b.match_date)
    
    if (activeTab.value === 'finished') {
      return dateB.getTime() - dateA.getTime() // Mais recentes primeiro
    } else {
      return dateA.getTime() - dateB.getTime() // Mais próximas primeiro
    }
  })
})

const upcomingCount = computed(() => 
  matches.value.filter(m => ['SCHEDULED', 'POSTPONED'].includes(m.status)).length
)

const liveCount = computed(() => 
  matches.value.filter(m => ['LIVE', 'PAUSED'].includes(m.status)).length
)

const finishedCount = computed(() => 
  matches.value.filter(m => m.status === 'FINISHED').length
)

// Methods
const loadMatches = async (params = {}) => {
  try {
    loading.value = true
    const data = await ApiService.getMatches(params)
    matches.value = data.results || data
  } catch (error) {
    console.error('Erro ao carregar partidas:', error)
  } finally {
    loading.value = false
  }
}

const loadCompetitions = async () => {
  try {
    const data = await ApiService.getCompetitions()
    competitions.value = data.results || data
  } catch (error) {
    console.error('Erro ao carregar competições:', error)
  }
}

const loadTeams = async () => {
  try {
    const data = await ApiService.getTeams()
    teams.value = data.results || data
  } catch (error) {
    console.error('Erro ao carregar times:', error)
  }
}

const applyFilters = () => {
  const params: any = {}
  
  if (selectedCompetition.value) {
    params.competition = selectedCompetition.value
  }
  
  if (selectedTeam.value) {
    params.team = selectedTeam.value
  }
  
  if (dateFrom.value) {
    params.date_from = dateFrom.value
  }
  
  if (dateTo.value) {
    params.date_to = dateTo.value
  }
  
  if (selectedStatus.value) {
    params.status = selectedStatus.value
  }
  
  loadMatches(params)
}

const onTabChange = () => {
  // Tab change handled by computed property
}

const viewMatchDetails = (match: any) => {
  selectedMatch.value = match
  detailsDialog.value = true
}

const viewMatchStats = (match: any) => {
  alert(`Estatísticas da partida ${match.home_team?.name} vs ${match.away_team?.name} - Funcionalidade em desenvolvimento`)
}

const getMatchCardClass = (match: any) => {
  if (match.status === 'LIVE') return 'live-match'
  if (match.status === 'FINISHED') return 'finished-match'
  return 'upcoming-match'
}

const getCompetitionColor = (competition: any) => {
  const colors = ['primary', 'secondary', 'accent', 'info', 'warning', 'error', 'success']
  return colors[competition?.id % colors.length] || 'primary'
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'SCHEDULED':
      return 'info'
    case 'LIVE':
      return 'error'
    case 'PAUSED':
      return 'warning'
    case 'FINISHED':
      return 'success'
    case 'POSTPONED':
      return 'orange'
    case 'CANCELLED':
      return 'grey'
    default:
      return 'grey'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'SCHEDULED':
      return 'Agendada'
    case 'LIVE':
      return 'Ao Vivo'
    case 'PAUSED':
      return 'Pausada'
    case 'FINISHED':
      return 'Finalizada'
    case 'POSTPONED':
      return 'Adiada'
    case 'CANCELLED':
      return 'Cancelada'
    default:
      return status
  }
}

const formatMatchDate = (dateString: string) => {
  if (!dateString) return 'Data não definida'
  return format(new Date(dateString), 'dd/MM/yyyy', { locale: ptBR })
}

const formatMatchTime = (dateString: string) => {
  if (!dateString) return 'Horário não definido'
  return format(new Date(dateString), 'HH:mm', { locale: ptBR })
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('pt-BR').format(num)
}

// Lifecycle
onMounted(() => {
  loadMatches()
  loadCompetitions()
  loadTeams()
})
</script>

<style scoped>
.match-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.match-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.live-match {
  border-left: 4px solid #f44336;
}

.finished-match {
  border-left: 4px solid #4caf50;
}

.upcoming-match {
  border-left: 4px solid #2196f3;
}

.live-indicator {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.score-display {
  font-family: 'Roboto Mono', monospace;
}

.vs-display {
  font-weight: bold;
  color: rgba(0, 0, 0, 0.6);
}
</style>
