<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-account-group</v-icon>
          Jogadores
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Explore informações detalhadas dos jogadores
        </p>
      </v-col>
    </v-row>

    <!-- Filters and Search -->
    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="search"
              label="Buscar jogadores"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              @input="debouncedSearch"
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
            <v-select
              v-model="selectedPosition"
              :items="positions"
              item-title="text"
              item-value="value"
              label="Posição"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="2">
            <v-select
              v-model="selectedNationality"
              :items="nationalities"
              label="Nacionalidade"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="2" class="d-flex align-end">
            <v-btn-toggle
              v-model="viewMode"
              mandatory
              variant="outlined"
              density="compact"
            >
              <v-btn value="grid" icon="mdi-view-grid" />
              <v-btn value="list" icon="mdi-view-list" />
            </v-btn-toggle>
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
      <p class="mt-4 text-subtitle-1">Carregando jogadores...</p>
    </v-card>

    <!-- Players Grid View -->
    <v-row v-else-if="viewMode === 'grid'">
      <v-col
        v-for="player in players"
        :key="player.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card
          elevation="2"
          class="player-card"
          @click="viewPlayerDetails(player)"
        >
          <v-img
            :src="player.photo_url || '/placeholder-player.png'"
            height="200"
            cover
            class="player-photo"
          >
            <v-overlay
              contained
              class="d-flex align-end justify-center"
              scrim="rgba(0,0,0,0.4)"
            >
              <div class="text-center text-white pa-2">
                <h3 class="text-h6 font-weight-bold mb-1">{{ player.name }}</h3>
                <v-chip
                  :color="getPositionColor(player.position_category)"
                  size="small"
                  dark
                >
                  {{ player.position || player.position_category }}
                </v-chip>
              </div>
            </v-overlay>
          </v-img>
          
          <v-card-text class="pb-2">
            <div class="text-center">
              <v-chip
                v-if="player.team"
                size="small"
                variant="outlined"
                class="mb-2"
              >
                <v-icon start>mdi-shield-account</v-icon>
                {{ player.team.name }}
              </v-chip>
              
              <div class="d-flex justify-center gap-2 mb-2">
                <v-chip
                  v-if="player.nationality"
                  size="small"
                  variant="tonal"
                >
                  <v-icon start>mdi-flag</v-icon>
                  {{ player.nationality }}
                </v-chip>
                
                <v-chip
                  v-if="player.age"
                  size="small"
                  variant="tonal"
                >
                  {{ player.age }} anos
                </v-chip>
              </div>
              
              <v-chip
                :color="getStatusColor(player.status)"
                size="small"
                variant="flat"
              >
                {{ player.status }}
              </v-chip>
            </div>
          </v-card-text>
          
          <v-card-actions class="justify-center pt-0">
            <v-btn
              color="primary"
              variant="text"
              size="small"
              @click.stop="viewPlayerStats(player)"
            >
              <v-icon start>mdi-chart-line</v-icon>
              Estatísticas
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Players List View -->
    <v-card v-else elevation="2">
      <v-data-table
        :headers="tableHeaders"
        :items="players"
        :loading="loading"
        item-value="id"
        class="elevation-0"
      >
        <template #item.photo_url="{ item }">
          <v-avatar size="40">
            <v-img
              :src="item.photo_url || '/placeholder-player.png'"
              :alt="item.name"
            />
          </v-avatar>
        </template>
        
        <template #item.name="{ item }">
          <div>
            <div class="font-weight-medium">{{ item.name }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ item.short_name || 'N/A' }}
            </div>
          </div>
        </template>
        
        <template #item.position_category="{ item }">
          <v-chip
            :color="getPositionColor(item.position_category)"
            size="small"
            variant="flat"
          >
            {{ item.position_category }}
          </v-chip>
        </template>
        
        <template #item.team="{ item }">
          <v-chip
            v-if="item.team"
            size="small"
            variant="outlined"
          >
            {{ item.team.name }}
          </v-chip>
          <span v-else class="text-medium-emphasis">Sem time</span>
        </template>
        
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="flat"
          >
            {{ item.status }}
          </v-chip>
        </template>
        
        <template #item.actions="{ item }">
          <v-btn
            icon
            size="small"
            variant="text"
            @click="viewPlayerDetails(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          
          <v-btn
            icon
            size="small"
            variant="text"
            @click="viewPlayerStats(item)"
          >
            <v-icon>mdi-chart-line</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- No Results -->
    <v-card
      v-if="!loading && players.length === 0"
      class="text-center pa-12"
    >
      <v-icon
        size="64"
        color="grey-lighten-1"
        class="mb-4"
      >
        mdi-account-off
      </v-icon>
      <h3 class="text-h6 mb-2">Nenhum jogador encontrado</h3>
      <p class="text-body-2 text-medium-emphasis">
        Tente ajustar os filtros de busca
      </p>
    </v-card>

    <!-- Player Details Dialog -->
    <v-dialog
      v-model="detailsDialog"
      max-width="700"
    >
      <v-card v-if="selectedPlayer">
        <v-card-title class="d-flex align-center">
          <v-avatar class="mr-3" size="48">
            <v-img
              :src="selectedPlayer.photo_url || '/placeholder-player.png'"
              :alt="selectedPlayer.name"
            />
          </v-avatar>
          <div>
            <div class="text-h6">{{ selectedPlayer.name }}</div>
            <div class="text-subtitle-2 text-medium-emphasis">
              {{ selectedPlayer.position }} • {{ selectedPlayer.nationality }}
            </div>
          </div>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="6">
              <strong>Nome Completo:</strong><br>
              {{ selectedPlayer.name }}
            </v-col>
            <v-col cols="6">
              <strong>Nome Curto:</strong><br>
              {{ selectedPlayer.short_name || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Idade:</strong><br>
              {{ selectedPlayer.age || 'N/A' }} anos
            </v-col>
            <v-col cols="6">
              <strong>Data de Nascimento:</strong><br>
              {{ formatDate(selectedPlayer.date_of_birth) || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Posição:</strong><br>
              {{ selectedPlayer.position || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Categoria:</strong><br>
              <v-chip
                :color="getPositionColor(selectedPlayer.position_category)"
                size="small"
              >
                {{ selectedPlayer.position_category }}
              </v-chip>
            </v-col>
            <v-col cols="6">
              <strong>Time Atual:</strong><br>
              {{ selectedPlayer.team?.name || 'Sem time' }}
            </v-col>
            <v-col cols="6">
              <strong>Status:</strong><br>
              <v-chip
                :color="getStatusColor(selectedPlayer.status)"
                size="small"
              >
                {{ selectedPlayer.status }}
              </v-chip>
            </v-col>
            <v-col cols="6">
              <strong>Altura:</strong><br>
              {{ selectedPlayer.height || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Peso:</strong><br>
              {{ selectedPlayer.weight || 'N/A' }}
            </v-col>
            <v-col v-if="selectedPlayer.description" cols="12">
              <strong>Descrição:</strong><br>
              {{ selectedPlayer.description }}
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-btn
            color="primary"
            variant="text"
            @click="viewPlayerStats(selectedPlayer)"
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
import { ref, onMounted } from 'vue'
import { ApiService } from '@/services/api'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Reactive data
const loading = ref(false)
const players = ref([])
const teams = ref([])
const search = ref('')
const selectedTeam = ref(null)
const selectedPosition = ref(null)
const selectedNationality = ref(null)
const viewMode = ref('grid')
const detailsDialog = ref(false)
const selectedPlayer = ref(null)

// Position options
const positions = [
  { text: 'Goleiro', value: 'GK' },
  { text: 'Defensor', value: 'DF' },
  { text: 'Meio-campo', value: 'MF' },
  { text: 'Atacante', value: 'FW' },
  { text: 'Técnico', value: 'COACH' }
]

// Get unique nationalities (will be populated from API)
const nationalities = ref([])

// Table headers for list view
const tableHeaders = [
  { title: 'Foto', key: 'photo_url', sortable: false },
  { title: 'Nome', key: 'name' },
  { title: 'Posição', key: 'position_category' },
  { title: 'Time', key: 'team', sortable: false },
  { title: 'Nacionalidade', key: 'nationality' },
  { title: 'Idade', key: 'age' },
  { title: 'Status', key: 'status' },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Methods
const loadPlayers = async (params = {}) => {
  try {
    loading.value = true
    const data = await ApiService.getPlayers(params)
    players.value = data.results || data
    
    // Extract unique nationalities
    const uniqueNationalities = [...new Set(players.value.map(p => p.nationality).filter(Boolean))]
    nationalities.value = uniqueNationalities.map(n => ({ text: n, value: n }))
  } catch (error) {
    console.error('Erro ao carregar jogadores:', error)
  } finally {
    loading.value = false
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
  
  if (search.value) {
    params.search = search.value
  }
  
  if (selectedTeam.value) {
    params.team = selectedTeam.value
  }
  
  if (selectedPosition.value) {
    params.position_category = selectedPosition.value
  }
  
  if (selectedNationality.value) {
    params.nationality = selectedNationality.value
  }
  
  loadPlayers(params)
}

const debouncedSearch = (() => {
  let timeout: any
  return () => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      applyFilters()
    }, 500)
  }
})()

const viewPlayerDetails = (player: any) => {
  selectedPlayer.value = player
  detailsDialog.value = true
}

const viewPlayerStats = (player: any) => {
  // For now, just show an alert
  alert(`Estatísticas de ${player.name} - Funcionalidade em desenvolvimento`)
}

const getPositionColor = (position: string) => {
  switch (position) {
    case 'GK':
      return 'orange'
    case 'DF':
      return 'blue'
    case 'MF':
      return 'green'
    case 'FW':
      return 'red'
    case 'COACH':
      return 'purple'
    default:
      return 'grey'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Active':
      return 'success'
    case 'Retired':
      return 'grey'
    case 'Injured':
      return 'error'
    case 'Loan':
      return 'warning'
    default:
      return 'grey'
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return null
  return format(new Date(dateString), 'dd/MM/yyyy', { locale: ptBR })
}

// Lifecycle
onMounted(() => {
  loadPlayers()
  loadTeams()
})
</script>

<style scoped>
.player-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  cursor: pointer;
}

.player-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.player-photo {
  position: relative;
}
</style>
