<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-shield-account</v-icon>
          Times
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Explore todos os times cadastrados no sistema
        </p>
      </v-col>
    </v-row>

    <!-- Filters and Search -->
    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Buscar times"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              @input="debouncedSearch"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedArea"
              :items="areas"
              item-title="name"
              item-value="id"
              label="País/Região"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="applyFilters"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              item-title="text"
              item-value="value"
              label="Ordenar por"
              variant="outlined"
              density="compact"
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
      <p class="mt-4 text-subtitle-1">Carregando times...</p>
    </v-card>

    <!-- Teams Grid View -->
    <v-row v-else-if="viewMode === 'grid'">
      <v-col
        v-for="team in teams"
        :key="team.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card
          elevation="2"
          class="team-card"
          @click="viewTeamDetails(team)"
        >
          <v-img
            :src="team.crest_url || '/placeholder-team.png'"
            height="120"
            contain
            class="team-logo pa-4"
          />
          
          <v-card-title class="text-center pb-2">
            {{ team.name }}
          </v-card-title>
          
          <v-card-subtitle class="text-center">
            {{ team.short_name || team.tla }}
          </v-card-subtitle>
          
          <v-card-text class="text-center pt-0">
            <v-chip
              v-if="team.area"
              size="small"
              variant="tonal"
              class="mb-2"
            >
              <v-icon start icon="mdi-flag" />
              {{ team.area.name }}
            </v-chip>
            
            <div v-if="team.founded" class="text-caption text-medium-emphasis">
              Fundado em {{ team.founded }}
            </div>
          </v-card-text>
          
          <v-card-actions class="justify-center">
            <v-btn
              color="primary"
              variant="text"
              size="small"
              @click.stop="viewTeamPlayers(team)"
            >
              <v-icon start>mdi-account-group</v-icon>
              Jogadores
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Teams List View -->
    <v-card v-else elevation="2">
      <v-data-table
        :headers="tableHeaders"
        :items="teams"
        :loading="loading"
        item-value="id"
        class="elevation-0"
      >
        <template #item.crest_url="{ item }">
          <v-avatar size="32">
            <v-img
              :src="item.crest_url || '/placeholder-team.png'"
              :alt="item.name"
            />
          </v-avatar>
        </template>
        
        <template #item.name="{ item }">
          <div>
            <div class="font-weight-medium">{{ item.name }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ item.short_name }}
            </div>
          </div>
        </template>
        
        <template #item.area="{ item }">
          <v-chip
            v-if="item.area"
            size="small"
            variant="tonal"
          >
            {{ item.area.name }}
          </v-chip>
        </template>
        
        <template #item.actions="{ item }">
          <v-btn
            icon
            size="small"
            variant="text"
            @click="viewTeamDetails(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          
          <v-btn
            icon
            size="small"
            variant="text"
            @click="viewTeamPlayers(item)"
          >
            <v-icon>mdi-account-group</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- No Results -->
    <v-card
      v-if="!loading && teams.length === 0"
      class="text-center pa-12"
    >
      <v-icon
        size="64"
        color="grey-lighten-1"
        class="mb-4"
      >
        mdi-shield-off
      </v-icon>
      <h3 class="text-h6 mb-2">Nenhum time encontrado</h3>
      <p class="text-body-2 text-medium-emphasis">
        Tente ajustar os filtros de busca
      </p>
    </v-card>

    <!-- Team Details Dialog -->
    <v-dialog
      v-model="detailsDialog"
      max-width="600"
    >
      <v-card v-if="selectedTeam">
        <v-card-title class="d-flex align-center">
          <v-avatar class="mr-3" size="32">
            <v-img
              :src="selectedTeam.crest_url || '/placeholder-team.png'"
              :alt="selectedTeam.name"
            />
          </v-avatar>
          {{ selectedTeam.name }}
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
              <strong>Sigla:</strong><br>
              {{ selectedTeam.tla || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Fundação:</strong><br>
              {{ selectedTeam.founded || 'N/A' }}
            </v-col>
            <v-col cols="12">
              <strong>Endereço:</strong><br>
              {{ selectedTeam.address || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Estádio:</strong><br>
              {{ selectedTeam.venue || 'N/A' }}
            </v-col>
            <v-col cols="6">
              <strong>Cores:</strong><br>
              {{ selectedTeam.club_colors || 'N/A' }}
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
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

// Reactive data
const loading = ref(false)
const teams = ref([])
const areas = ref([])
const search = ref('')
const selectedArea = ref(null)
const sortBy = ref('name')
const viewMode = ref('grid')
const detailsDialog = ref(false)
const selectedTeam = ref(null)

// Sort options
const sortOptions = [
  { text: 'Nome', value: 'name' },
  { text: 'Nome Curto', value: 'short_name' },
  { text: 'Fundação', value: 'founded' },
  { text: 'Data de Criação', value: 'created_at' }
]

// Table headers for list view
const tableHeaders = [
  { title: 'Logo', key: 'crest_url', sortable: false },
  { title: 'Nome', key: 'name' },
  { title: 'Sigla', key: 'tla' },
  { title: 'País', key: 'area', sortable: false },
  { title: 'Fundação', key: 'founded' },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Methods
const loadTeams = async (params = {}) => {
  try {
    loading.value = true
    const data = await ApiService.getTeams(params)
    teams.value = data.results || data
  } catch (error) {
    console.error('Erro ao carregar times:', error)
  } finally {
    loading.value = false
  }
}

const loadAreas = async () => {
  try {
    const data = await ApiService.getAreas()
    areas.value = data.results || data
  } catch (error) {
    console.error('Erro ao carregar áreas:', error)
  }
}

const applyFilters = () => {
  const params: any = {}
  
  if (search.value) {
    params.search = search.value
  }
  
  if (selectedArea.value) {
    params.area = selectedArea.value
  }
  
  if (sortBy.value) {
    params.ordering = sortBy.value
  }
  
  loadTeams(params)
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

const viewTeamDetails = (team: any) => {
  selectedTeam.value = team
  detailsDialog.value = true
}

const viewTeamPlayers = (team: any) => {
  // Navigate to players page with team filter
  // For now, just show an alert
  alert(`Visualizar jogadores do ${team.name}`)
}

// Lifecycle
onMounted(() => {
  loadTeams()
  loadAreas()
})
</script>

<style scoped>
.team-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  cursor: pointer;
}

.team-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.team-logo {
  background: linear-gradient(145deg, #f5f5f5, #ffffff);
}
</style>
