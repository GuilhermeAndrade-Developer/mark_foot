<template>
  <div class="settings-page">
    <v-container fluid>
      <!-- Header -->
      <v-row>
        <v-col cols="12">
          <div class="d-flex align-center mb-6">
            <v-icon size="32" class="mr-3" color="primary">mdi-cog</v-icon>
            <h1 class="text-h4 font-weight-bold">Configurações</h1>
          </div>
        </v-col>
      </v-row>

      <!-- Sync Section -->
      <v-row>
        <v-col cols="12" lg="8">
          <v-card elevation="2" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-3" color="primary">mdi-sync</v-icon>
              Sincronização de Dados
            </v-card-title>
            <v-card-text>
              <p class="text-body-1 mb-4">
                Execute uma sincronização completa de todos os dados das APIs externas.
                O processo irá respeitar os limites de rate limiting automaticamente.
              </p>

              <!-- Sync Options -->
              <v-row class="mb-4">
                <v-col cols="12" md="6">
                  <v-select
                    v-model="syncOptions.competitions"
                    :items="availableCompetitions"
                    item-title="name"
                    item-value="code"
                    label="Competições para sincronizar"
                    multiple
                    chips
                    closable-chips
                    hint="Selecione as competições que deseja sincronizar"
                    persistent-hint
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="syncOptions.includeStandings"
                    label="Incluir Classificações"
                    color="primary"
                    hint="Sincronizar standings das competições"
                    persistent-hint
                  />
                  <v-switch
                    v-model="syncOptions.includePlayers"
                    label="Incluir Jogadores"
                    color="primary"
                    hint="Sincronizar jogadores dos times"
                    persistent-hint
                  />
                </v-col>
              </v-row>

              <!-- Sync Button -->
              <div class="text-center">
                <v-btn
                  :loading="syncInProgress"
                  :disabled="syncOptions.competitions.length === 0"
                  color="primary"
                  size="large"
                  @click="startFullSync"
                  class="mr-3"
                >
                  <v-icon left>mdi-play</v-icon>
                  Iniciar Sincronização Completa
                </v-btn>
                
                <v-btn
                  v-if="syncInProgress"
                  color="error"
                  size="large"
                  @click="cancelSync"
                >
                  <v-icon left>mdi-stop</v-icon>
                  Cancelar
                </v-btn>
              </div>
            </v-card-text>
          </v-card>

          <!-- Player Photos Sync Section -->
          <v-card elevation="2" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-3" color="info">mdi-camera</v-icon>
              Sincronização de Fotos dos Jogadores
            </v-card-title>
            <v-card-text>
              <p class="text-body-1 mb-4">
                Sincronize fotos dos jogadores usando TheSportsDB API. 
                Esta operação irá buscar e atualizar as fotos dos jogadores existentes no sistema.
              </p>

              <!-- Photo Sync Options -->
              <v-row class="mb-4">
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model.number="photoSyncOptions.limit"
                    type="number"
                    label="Limite de jogadores"
                    hint="Número máximo de jogadores para processar (30 requests/min)"
                    persistent-hint
                    min="1"
                    max="500"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="photoSyncOptions.dryRun"
                    label="Modo de Teste"
                    color="warning"
                    hint="Simular operação sem fazer alterações"
                    persistent-hint
                  />
                </v-col>
              </v-row>

              <!-- Stats Display -->
              <v-row class="mb-4">
                <v-col cols="12" md="4">
                  <v-card variant="outlined" class="text-center pa-3">
                    <div class="text-h5 font-weight-bold text-primary">{{ photoStats.totalPlayers }}</div>
                    <div class="text-caption text-medium-emphasis">Total de Jogadores</div>
                  </v-card>
                </v-col>
                <v-col cols="12" md="4">
                  <v-card variant="outlined" class="text-center pa-3">
                    <div class="text-h5 font-weight-bold text-success">{{ photoStats.playersWithPhotos }}</div>
                    <div class="text-caption text-medium-emphasis">Com Fotos</div>
                  </v-card>
                </v-col>
                <v-col cols="12" md="4">
                  <v-card variant="outlined" class="text-center pa-3">
                    <div class="text-h5 font-weight-bold text-warning">{{ photoStats.coveragePercentage }}%</div>
                    <div class="text-caption text-medium-emphasis">Cobertura</div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Photo Sync Button -->
              <div class="text-center">
                <v-btn
                  :loading="photoSyncInProgress"
                  color="info"
                  size="large"
                  @click="startPhotoSync"
                  class="mr-3"
                >
                  <v-icon left>mdi-camera-plus</v-icon>
                  {{ photoSyncOptions.dryRun ? 'Testar Sincronização' : 'Sincronizar Fotos' }}
                </v-btn>
                
                <v-btn
                  @click="refreshPhotoStats"
                  :loading="loadingPhotoStats"
                  variant="outlined"
                  color="info"
                  size="large"
                >
                  <v-icon left>mdi-refresh</v-icon>
                  Atualizar Estatísticas
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
          <v-card v-if="syncInProgress || syncLog.length > 0" elevation="2" class="mb-6">
            <v-card-title>
              <v-icon class="mr-3" :color="syncInProgress ? 'warning' : 'success'">
                {{ syncInProgress ? 'mdi-loading mdi-spin' : 'mdi-check-circle' }}
              </v-icon>
              Status da Sincronização
            </v-card-title>
            <v-card-text>
              <!-- Overall Progress -->
              <div v-if="syncInProgress" class="mb-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-subtitle-1">{{ currentSyncStep }}</span>
                  <span class="text-caption">{{ syncProgress.current }}/{{ syncProgress.total }}</span>
                </div>
                <v-progress-linear
                  :model-value="(syncProgress.current / syncProgress.total) * 100"
                  color="primary"
                  height="8"
                  rounded
                />
              </div>

              <!-- Sync Log -->
              <div class="sync-log">
                <v-list dense max-height="300" class="overflow-y-auto">
                  <v-list-item
                    v-for="(log, index) in syncLog"
                    :key="index"
                    class="px-0"
                  >
                    <template v-slot:prepend>
                      <v-icon
                        :color="getLogIconColor(log.type)"
                        size="small"
                        class="mr-2"
                      >
                        {{ getLogIcon(log.type) }}
                      </v-icon>
                    </template>
                    <v-list-item-title class="text-body-2">
                      <span class="text-caption text-medium-emphasis mr-2">
                        {{ formatTime(log.timestamp) }}
                      </span>
                      {{ log.message }}
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Quick Stats -->
        <v-col cols="12" lg="4">
          <v-card elevation="2" class="mb-6">
            <v-card-title>
              <v-icon class="mr-3" color="info">mdi-chart-line</v-icon>
              Estatísticas Atuais
            </v-card-title>
            <v-card-text>
              <div class="stats-grid">
                <div v-for="stat in currentStats" :key="stat.label" class="stat-item mb-3">
                  <div class="d-flex align-center">
                    <v-icon :color="stat.color" class="mr-2">{{ stat.icon }}</v-icon>
                    <div>
                      <div class="text-h6 font-weight-bold">{{ stat.value }}</div>
                      <div class="text-caption text-medium-emphasis">{{ stat.label }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <v-btn
                @click="refreshStats"
                :loading="loadingStats"
                variant="outlined"
                color="primary"
                size="small"
                block
                class="mt-3"
              >
                <v-icon left size="small">mdi-refresh</v-icon>
                Atualizar
              </v-btn>
            </v-card-text>
          </v-card>

          <!-- API Status -->
          <v-card elevation="2">
            <v-card-title>
              <v-icon class="mr-3" color="success">mdi-api</v-icon>
              Status das APIs
            </v-card-title>
            <v-card-text>
              <div v-for="api in apiStatus" :key="api.name" class="api-status-item mb-3">
                <div class="d-flex align-center justify-space-between">
                  <span class="text-body-2">{{ api.name }}</span>
                  <v-chip
                    :color="api.status === 'online' ? 'success' : 'error'"
                    size="small"
                    variant="flat"
                  >
                    {{ api.status === 'online' ? 'Online' : 'Offline' }}
                  </v-chip>
                </div>
                <div class="text-caption text-medium-emphasis">
                  Rate Limit: {{ api.rateLimit }} | Última checagem: {{ formatTime(api.lastCheck) }}
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { 
  syncService, 
  type SyncOptions, 
  type SyncProgress, 
  type SyncLog, 
  type ApiStatus, 
  type DatabaseStats 
} from '@/services/syncApi'

const appStore = useAppStore()

// Reactive data
const syncInProgress = ref(false)
const currentSyncStep = ref('')
const loadingStats = ref(false)
const syncProgress = reactive({
  current: 0,
  total: 0
})

const syncOptions = reactive({
  competitions: ['PL', 'BL1', 'PD', 'SA'],
  includeStandings: true,
  includePlayers: true
})

const photoSyncOptions = reactive({
  limit: 100,  // Increased default limit since we have 30 requests/minute
  dryRun: false
})

const photoStats = reactive({
  totalPlayers: 0,
  playersWithPhotos: 0,
  coveragePercentage: 0
})

const photoSyncInProgress = ref(false)
const loadingPhotoStats = ref(false)

const syncLog = ref([])
const currentStats = ref([])
const apiStatus = ref([])

const availableCompetitions = ref(syncService.getAvailableCompetitions())

// Sync control
let syncInterval: NodeJS.Timeout | null = null
let abortController: AbortController | null = null

// Methods
const addLog = (log: SyncLog) => {
  syncLog.value.unshift({
    ...log,
    timestamp: new Date()
  })
  
  // Keep only last 50 logs
  if (syncLog.value.length > 50) {
    syncLog.value = syncLog.value.slice(0, 50)
  }
}

const getLogIcon = (type: string) => {
  switch (type) {
    case 'success': return 'mdi-check-circle'
    case 'error': return 'mdi-alert-circle'
    case 'warning': return 'mdi-alert'
    case 'info': return 'mdi-information'
    default: return 'mdi-circle'
  }
}

const getLogIconColor = (type: string) => {
  switch (type) {
    case 'success': return 'success'
    case 'error': return 'error'
    case 'warning': return 'warning'
    case 'info': return 'info'
    default: return 'primary'
  }
}

const formatTime = (date: Date | string) => {
  if (!date) return 'N/A'
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date(date))
}

const updateProgress = (progress: SyncProgress) => {
  syncProgress.current = progress.current
  syncProgress.total = progress.total
}

const refreshStats = async () => {
  loadingStats.value = true
  try {
    const stats = await syncService.getStats()
    currentStats.value = [
      {
        label: 'Competições',
        value: stats.competitions || 0,
        icon: 'mdi-trophy',
        color: 'primary'
      },
      {
        label: 'Times',
        value: stats.teams || 0,
        icon: 'mdi-shield',
        color: 'success'
      },
      {
        label: 'Jogadores',
        value: stats.players || 0,
        icon: 'mdi-account-group',
        color: 'info'
      },
      {
        label: 'Partidas',
        value: stats.matches || 0,
        icon: 'mdi-soccer',
        color: 'warning'
      }
    ]
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error)
  } finally {
    loadingStats.value = false
  }
}

const checkApiStatus = async () => {
  try {
    const apis = await syncService.checkApiStatus()
    apiStatus.value = apis
  } catch (error) {
    console.error('Error checking API status:', error)
    // Fallback to simulated data
    apiStatus.value = [
      {
        name: 'Football-Data.org',
        status: 'error',
        rateLimit: '10/min',
        lastCheck: new Date().toISOString(),
        error: 'Could not connect to sync service'
      },
      {
        name: 'TheSportsDB',
        status: 'error',
        rateLimit: 'Unlimited',
        lastCheck: new Date().toISOString(),
        error: 'Could not connect to sync service'
      }
    ]
  }
}

const startFullSync = async () => {
  if (syncInProgress.value) return
  
  syncInProgress.value = true
  syncLog.value = []
  syncProgress.current = 0
  syncProgress.total = 0
  
  abortController = new AbortController()
  
  try {
    const options: SyncOptions = {
      competitions: syncOptions.competitions,
      includeStandings: syncOptions.includeStandings,
      includePlayers: syncOptions.includePlayers
    }

    const success = await syncService.executeFullSync(
      options,
      updateProgress,
      addLog,
      abortController.signal
    )

    if (success) {
      await refreshStats()
    }
    
  } catch (error) {
    addLog({
      type: 'error',
      message: `❌ Erro na sincronização: ${error.message}`,
      timestamp: new Date()
    })
  } finally {
    syncInProgress.value = false
    currentSyncStep.value = ''
    abortController = null
  }
}

const cancelSync = () => {
  if (abortController) {
    abortController.abort()
    addLog({
      type: 'warning',
      message: '⚠️ Sincronização cancelada',
      timestamp: new Date()
    })
  }
}

const refreshPhotoStats = async () => {
  loadingPhotoStats.value = true
  try {
    const stats = await syncService.getStats()
    photoStats.totalPlayers = stats.players || 0
    photoStats.playersWithPhotos = stats.players_with_photos || 0
    photoStats.coveragePercentage = stats.photo_coverage_percentage || 0
  } catch (error) {
    console.error('Erro ao carregar estatísticas de fotos:', error)
  } finally {
    loadingPhotoStats.value = false
  }
}

const startPhotoSync = async () => {
  if (photoSyncInProgress.value) return
  
  photoSyncInProgress.value = true
  
  try {
    addLog({
      type: 'info',
      message: `📸 Iniciando sincronização de fotos (${photoSyncOptions.limit} jogadores)...`,
      timestamp: new Date()
    })
    
    const result = await syncService.syncPlayerPhotos(
      photoSyncOptions.limit, 
      photoSyncOptions.dryRun
    )
    
    if (result.success) {
      addLog({
        type: 'success',
        message: `✅ Fotos sincronizadas: ${result.summary}`,
        timestamp: new Date()
      })
      
      // Update photo stats
      photoStats.totalPlayers = result.details.total_players
      photoStats.playersWithPhotos = result.details.players_with_photos
      photoStats.coveragePercentage = result.details.coverage_percentage
      
      // Refresh general stats
      await refreshStats()
    } else {
      addLog({
        type: 'error',
        message: `❌ Erro na sincronização de fotos: ${result.error}`,
        timestamp: new Date()
      })
    }
    
  } catch (error) {
    addLog({
      type: 'error',
      message: `❌ Erro na sincronização de fotos: ${error.message}`,
      timestamp: new Date()
    })
  } finally {
    photoSyncInProgress.value = false
  }
}

// Lifecycle
onMounted(() => {
  refreshStats()
  refreshPhotoStats()
  checkApiStatus()
})

onUnmounted(() => {
  if (syncInterval) {
    clearInterval(syncInterval)
  }
  if (abortController) {
    abortController.abort()
  }
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.sync-log {
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.stat-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.api-status-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.api-status-item:last-child {
  border-bottom: none;
}

.mdi-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
