<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-trophy</v-icon>
          Classificação
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Acompanhe a tabela de classificação das competições
        </p>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedCompetition"
              :items="competitions"
              item-title="name"
              item-value="id"
              label="Competição"
              variant="outlined"
              density="compact"
              @update:model-value="loadStandings"
            />
          </v-col>
          
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedSeason"
              :items="seasons"
              item-title="text"
              item-value="value"
              label="Temporada"
              variant="outlined"
              density="compact"
              @update:model-value="loadStandings"
            />
          </v-col>
          
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedGroup"
              :items="groups"
              item-title="text"
              item-value="value"
              label="Grupo"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="loadStandings"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Loading -->
    <v-card v-if="loading" class="text-center pa-12">
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      />
      <p class="mt-4 text-subtitle-1">Carregando classificação...</p>
    </v-card>

    <!-- Standings Table -->
    <v-card v-else-if="standings.length > 0" elevation="2">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-trophy</v-icon>
        <span>{{ selectedCompetitionName }} - {{ selectedSeason || 'Temporada Atual' }}</span>
        <v-spacer />
        <v-chip
          v-if="lastUpdated"
          size="small"
          variant="tonal"
        >
          <v-icon start size="small">mdi-clock</v-icon>
          Atualizado: {{ formatDate(lastUpdated) }}
        </v-chip>
      </v-card-title>

      <v-divider />

      <div class="standings-table">
        <v-table density="comfortable">
          <thead>
            <tr class="header-row">
              <th class="text-center" style="width: 60px;">#</th>
              <th style="min-width: 200px;">Time</th>
              <th class="text-center" style="width: 60px;">
                <v-tooltip text="Jogos">
                  <template #activator="{ props }">
                    <span v-bind="props">J</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center" style="width: 60px;">
                <v-tooltip text="Vitórias">
                  <template #activator="{ props }">
                    <span v-bind="props">V</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center" style="width: 60px;">
                <v-tooltip text="Empates">
                  <template #activator="{ props }">
                    <span v-bind="props">E</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center" style="width: 60px;">
                <v-tooltip text="Derrotas">
                  <template #activator="{ props }">
                    <span v-bind="props">D</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center" style="width: 80px;">
                <v-tooltip text="Gols Pró">
                  <template #activator="{ props }">
                    <span v-bind="props">GP</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center" style="width: 80px;">
                <v-tooltip text="Gols Contra">
                  <template #activator="{ props }">
                    <span v-bind="props">GC</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center" style="width: 80px;">
                <v-tooltip text="Saldo de Gols">
                  <template #activator="{ props }">
                    <span v-bind="props">SG</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center font-weight-bold" style="width: 80px;">
                <v-tooltip text="Pontos">
                  <template #activator="{ props }">
                    <span v-bind="props">PTS</span>
                  </template>
                </v-tooltip>
              </th>
              <th class="text-center" style="width: 120px;">Forma</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(standing, index) in standings"
              :key="standing.id"
              class="standing-row"
              :class="getPositionClass(standing.position, standings.length)"
              @click="viewTeamDetails(standing.team)"
            >
              <!-- Position -->
              <td class="text-center position-cell">
                <div class="d-flex align-center justify-center">
                  <span class="position-number font-weight-bold">
                    {{ standing.position }}
                  </span>
                  <div
                    v-if="getPositionIndicator(standing.position, standings.length)"
                    class="position-indicator ml-1"
                    :class="getPositionIndicator(standing.position, standings.length)"
                  />
                </div>
              </td>

              <!-- Team -->
              <td class="team-cell">
                <div class="d-flex align-center">
                  <v-avatar
                    :image="standing.team?.logo_url"
                    size="32"
                    class="mr-3"
                  >
                    <v-icon>mdi-shield</v-icon>
                  </v-avatar>
                  <div>
                    <div class="font-weight-medium">
                      {{ standing.team?.name }}
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      {{ standing.team?.short_name }}
                    </div>
                  </div>
                </div>
              </td>

              <!-- Games Played -->
              <td class="text-center">
                {{ standing.games_played || 0 }}
              </td>

              <!-- Wins -->
              <td class="text-center text-success">
                {{ standing.wins || 0 }}
              </td>

              <!-- Draws -->
              <td class="text-center text-warning">
                {{ standing.draws || 0 }}
              </td>

              <!-- Losses -->
              <td class="text-center text-error">
                {{ standing.losses || 0 }}
              </td>

              <!-- Goals For -->
              <td class="text-center">
                {{ standing.goals_for || 0 }}
              </td>

              <!-- Goals Against -->
              <td class="text-center">
                {{ standing.goals_against || 0 }}
              </td>

              <!-- Goal Difference -->
              <td class="text-center">
                <span
                  :class="{
                    'text-success': (standing.goals_for || 0) - (standing.goals_against || 0) > 0,
                    'text-error': (standing.goals_for || 0) - (standing.goals_against || 0) < 0,
                    'text-medium-emphasis': (standing.goals_for || 0) - (standing.goals_against || 0) === 0
                  }"
                >
                  {{ (standing.goals_for || 0) - (standing.goals_against || 0) > 0 ? '+' : '' }}{{ (standing.goals_for || 0) - (standing.goals_against || 0) }}
                </span>
              </td>

              <!-- Points -->
              <td class="text-center">
                <span class="points-value font-weight-bold text-h6">
                  {{ standing.points || 0 }}
                </span>
              </td>

              <!-- Form -->
              <td class="text-center">
                <div class="form-indicators">
                  <v-chip
                    v-for="(form, formIndex) in getFormArray(standing.form)"
                    :key="formIndex"
                    :color="getFormColor(form)"
                    size="x-small"
                    variant="flat"
                    class="ma-1"
                  >
                    {{ form }}
                  </v-chip>
                </div>
              </td>
            </tr>
          </tbody>
        </v-table>
      </div>

      <!-- Legend -->
      <v-card-text class="pt-4">
        <v-row>
          <v-col cols="12">
            <div class="text-subtitle-2 font-weight-bold mb-2">Legenda:</div>
            <div class="d-flex flex-wrap gap-4">
              <div class="d-flex align-center">
                <div class="legend-indicator champions mr-2" />
                <span class="text-caption">Classificação para Champions League</span>
              </div>
              <div class="d-flex align-center">
                <div class="legend-indicator europa mr-2" />
                <span class="text-caption">Classificação para Europa League</span>
              </div>
              <div class="d-flex align-center">
                <div class="legend-indicator conference mr-2" />
                <span class="text-caption">Classificação para Conference League</span>
              </div>
              <div class="d-flex align-center">
                <div class="legend-indicator relegation mr-2" />
                <span class="text-caption">Zona de Rebaixamento</span>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- No Results -->
    <v-card
      v-else
      class="text-center pa-12"
    >
      <v-icon
        size="64"
        color="grey-lighten-1"
        class="mb-4"
      >
        mdi-trophy-outline
      </v-icon>
      <h3 class="text-h6 mb-2">Nenhuma classificação encontrada</h3>
      <p class="text-body-2 text-medium-emphasis">
        Selecione uma competição para visualizar a classificação
      </p>
    </v-card>

    <!-- Team Details Dialog -->
    <v-dialog
      v-model="teamDialog"
      max-width="600"
    >
      <v-card v-if="selectedTeam">
        <v-card-title class="d-flex align-center">
          <v-avatar
            :image="selectedTeam.logo_url"
            size="48"
            class="mr-3"
          >
            <v-icon>mdi-shield</v-icon>
          </v-avatar>
          <div>
            <div class="text-h6">{{ selectedTeam.name }}</div>
            <div class="text-subtitle-2 text-medium-emphasis">
              {{ selectedTeam.founded ? `Fundado em ${selectedTeam.founded}` : '' }}
            </div>
          </div>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="6">
              <strong>Nome Completo:</strong><br>
              {{ selectedTeam.name }}
            </v-col>
            <v-col cols="6">
              <strong>Nome Curto:</strong><br>
              {{ selectedTeam.short_name || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>País:</strong><br>
              {{ selectedTeam.area || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Estádio:</strong><br>
              {{ selectedTeam.venue || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Técnico:</strong><br>
              {{ selectedTeam.coach || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Website:</strong><br>
              <a
                v-if="selectedTeam.website"
                :href="selectedTeam.website"
                target="_blank"
                class="text-primary"
              >
                {{ selectedTeam.website }}
              </a>
              <span v-else>N/A</span>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-btn
            color="primary"
            variant="text"
            @click="viewTeamPlayers(selectedTeam)"
          >
            <v-icon start>mdi-account-group</v-icon>
            Ver Jogadores
          </v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            @click="teamDialog = false"
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
const standings = ref([])
const competitions = ref([])
const selectedCompetition = ref(null)
const selectedSeason = ref('2024')
const selectedGroup = ref(null)
const teamDialog = ref(false)
const selectedTeam = ref(null)
const lastUpdated = ref(null)

// Season options
const seasons = [
  { text: '2024', value: '2024' },
  { text: '2023', value: '2023' },
  { text: '2022', value: '2022' }
]

// Groups (will be populated based on competition)
const groups = ref([])

// Computed properties
const selectedCompetitionName = computed(() => {
  const comp = competitions.value.find(c => c.id === selectedCompetition.value)
  return comp?.name || 'Competição'
})

// Methods
const loadStandings = async () => {
  if (!selectedCompetition.value) return

  try {
    loading.value = true
    const params: any = {
      competition: selectedCompetition.value
    }
    
    if (selectedSeason.value) {
      params.season = selectedSeason.value
    }
    
    if (selectedGroup.value) {
      params.group = selectedGroup.value
    }

    const data = await ApiService.getStandings(params)
    standings.value = data.results || data
    lastUpdated.value = new Date()
  } catch (error) {
    console.error('Erro ao carregar classificação:', error)
    standings.value = []
  } finally {
    loading.value = false
  }
}

const loadCompetitions = async () => {
  try {
    const data = await ApiService.getCompetitions()
    competitions.value = data.results || data
    
    // Auto-select first competition
    if (competitions.value.length > 0 && !selectedCompetition.value) {
      selectedCompetition.value = competitions.value[0].id
      loadStandings()
    }
  } catch (error) {
    console.error('Erro ao carregar competições:', error)
  }
}

const viewTeamDetails = (team: any) => {
  selectedTeam.value = team
  teamDialog.value = true
}

const viewTeamPlayers = (team: any) => {
  alert(`Jogadores do ${team.name} - Funcionalidade em desenvolvimento`)
}

const getPositionClass = (position: number, totalTeams: number) => {
  if (position <= 4) return 'champions-position'
  if (position <= 6) return 'europa-position'
  if (position <= 7) return 'conference-position'
  if (position > totalTeams - 3) return 'relegation-position'
  return ''
}

const getPositionIndicator = (position: number, totalTeams: number) => {
  if (position <= 4) return 'champions'
  if (position <= 6) return 'europa'
  if (position <= 7) return 'conference'
  if (position > totalTeams - 3) return 'relegation'
  return null
}

const getFormArray = (form: string) => {
  if (!form) return []
  return form.split('').slice(-5) // Last 5 matches
}

const getFormColor = (result: string) => {
  switch (result.toUpperCase()) {
    case 'W':
      return 'success'
    case 'D':
      return 'warning'
    case 'L':
      return 'error'
    default:
      return 'grey'
  }
}

const formatDate = (date: Date) => {
  return format(date, 'dd/MM/yyyy HH:mm', { locale: ptBR })
}

// Lifecycle
onMounted(() => {
  loadCompetitions()
})
</script>

<style scoped>
.standings-table {
  overflow-x: auto;
}

.header-row {
  background-color: rgb(var(--v-theme-surface-variant));
}

.standing-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.standing-row:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.position-cell {
  min-width: 60px;
}

.team-cell {
  min-width: 200px;
}

.position-number {
  min-width: 24px;
  display: inline-block;
}

.position-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.position-indicator.champions {
  background-color: #1976d2;
}

.position-indicator.europa {
  background-color: #ff9800;
}

.position-indicator.conference {
  background-color: #9c27b0;
}

.position-indicator.relegation {
  background-color: #f44336;
}

.champions-position {
  border-left: 4px solid #1976d2;
}

.europa-position {
  border-left: 4px solid #ff9800;
}

.conference-position {
  border-left: 4px solid #9c27b0;
}

.relegation-position {
  border-left: 4px solid #f44336;
}

.points-value {
  color: rgb(var(--v-theme-primary));
}

.form-indicators {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2px;
}

.legend-indicator {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}

.legend-indicator.champions {
  background-color: #1976d2;
}

.legend-indicator.europa {
  background-color: #ff9800;
}

.legend-indicator.conference {
  background-color: #9c27b0;
}

.legend-indicator.relegation {
  background-color: #f44336;
}
</style>
