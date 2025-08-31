<template>
  <v-card class="mb-4" variant="outlined">
    <v-card-text>
      <div class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon 
            :color="statusColor" 
            class="mr-3"
            size="large"
          >
            {{ statusIcon }}
          </v-icon>
          
          <div>
            <div class="text-h6 font-weight-medium">
              {{ statusTitle }}
            </div>
            <div class="text-body-2 text-medium-emphasis">
              {{ statusDescription }}
            </div>
          </div>
        </div>

        <div class="d-flex align-center gap-2">
          <v-chip
            :color="systemStatus?.mode === 'real' ? 'success' : 'warning'"
            size="small"
            variant="flat"
          >
            <v-icon start size="small">
              {{ systemStatus?.mode === 'real' ? 'mdi-database-check' : 'mdi-presentation' }}
            </v-icon>
            {{ systemStatus?.mode === 'real' ? 'Dados Reais' : 'Demonstração' }}
          </v-chip>

          <v-btn
            :loading="refreshing"
            size="small"
            variant="outlined"
            @click="refreshStatus"
          >
            <v-icon size="small">mdi-refresh</v-icon>
            Verificar
          </v-btn>
        </div>
      </div>

      <!-- Additional info when in demo mode -->
      <v-expand-transition>
        <v-alert
          v-if="systemStatus?.mode === 'demo'"
          class="mt-4"
          color="warning"
          variant="tonal"
          border="start"
        >
          <div class="text-body-2">
            <strong>Modo Demonstração Ativo:</strong><br>
            • Dados são simulados para demonstração<br>
            • Operações de criação/edição são temporárias<br>
            • Sistema alternará automaticamente quando dados reais estiverem disponíveis
          </div>
        </v-alert>
      </v-expand-transition>

      <!-- Connection details -->
      <v-expand-transition>
        <div v-if="showDetails" class="mt-4">
          <v-divider class="mb-3"></v-divider>
          <div class="text-body-2">
            <div><strong>API Disponível:</strong> {{ systemStatus?.api_available ? 'Sim' : 'Não' }}</div>
            <div><strong>Dados Disponíveis:</strong> {{ systemStatus?.has_data ? 'Sim' : 'Não' }}</div>
            <div><strong>Última Verificação:</strong> {{ formatLastCheck }}</div>
          </div>
        </div>
      </v-expand-transition>

      <v-btn
        v-if="systemStatus"
        class="mt-2"
        size="small"
        variant="text"
        @click="showDetails = !showDetails"
      >
        {{ showDetails ? 'Ocultar' : 'Mostrar' }} Detalhes
        <v-icon size="small" class="ml-1">
          {{ showDetails ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
        </v-icon>
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import chatApiService from '@/services/chatApiSmart'

// Reactive state
const systemStatus = ref<{
  mode: 'demo' | 'real'
  api_available: boolean
  has_data: boolean
  last_check: Date
} | null>(null)

const refreshing = ref(false)
const showDetails = ref(false)

// Auto-refresh interval
let refreshInterval: NodeJS.Timeout | null = null

// Computed properties
const statusColor = computed(() => {
  if (!systemStatus.value) return 'grey'
  return systemStatus.value.mode === 'real' ? 'success' : 'warning'
})

const statusIcon = computed(() => {
  if (!systemStatus.value) return 'mdi-help-circle'
  return systemStatus.value.mode === 'real' ? 'mdi-cloud-check' : 'mdi-presentation'
})

const statusTitle = computed(() => {
  if (!systemStatus.value) return 'Verificando Sistema...'
  return systemStatus.value.mode === 'real' ? 'Sistema Conectado' : 'Modo Demonstração'
})

const statusDescription = computed(() => {
  if (!systemStatus.value) return 'Detectando disponibilidade de dados'
  
  if (systemStatus.value.mode === 'real') {
    return 'Conectado ao backend com dados reais'
  } else {
    return 'Usando dados de demonstração - o sistema alternará automaticamente quando dados reais estiverem disponíveis'
  }
})

const formatLastCheck = computed(() => {
  if (!systemStatus.value) return '-'
  
  const now = new Date()
  const diff = now.getTime() - systemStatus.value.last_check.getTime()
  const seconds = Math.floor(diff / 1000)
  
  if (seconds < 60) return `${seconds} segundos atrás`
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutos atrás`
  return systemStatus.value.last_check.toLocaleTimeString()
})

// Methods
const loadStatus = async () => {
  try {
    systemStatus.value = await chatApiService.getSystemStatus()
  } catch (error) {
    console.error('Error loading system status:', error)
  }
}

const refreshStatus = async () => {
  refreshing.value = true
  try {
    const newMode = await chatApiService.refreshSystemStatus()
    systemStatus.value = await chatApiService.getSystemStatus()
    
    // Emit event for parent components
    if (newMode !== systemStatus.value.mode) {
      // Could emit an event here if needed
      console.info(`🔄 System mode changed to: ${newMode}`)
    }
  } catch (error) {
    console.error('Error refreshing system status:', error)
  } finally {
    refreshing.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await loadStatus()
  
  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(loadStatus, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>
