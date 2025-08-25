<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold mb-2">
              <v-icon class="mr-3" color="warning">mdi-test-tube</v-icon>
              Centro de Testes IA
            </h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              Execução e monitoramento de testes do sistema de inteligência artificial
            </p>
          </div>
          <v-btn
            color="warning"
            @click="clearLogs"
          >
            <v-icon left>mdi-broom</v-icon>
            Limpar Logs
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Test Commands Grid -->
    <v-row class="mb-6">
      <v-col cols="12" md="6" lg="4">
        <v-card elevation="2" class="test-card">
          <v-card-title class="pb-2">
            <v-icon class="mr-2" color="primary">mdi-play</v-icon>
            Teste Básico
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-4">Executa um teste básico do sistema IA para verificar conectividade e funcionamento.</p>
            <v-btn
              block
              color="primary"
              @click="runTest('basic_test')"
              :loading="loadingTests.basic_test"
            >
              <v-icon left>mdi-play</v-icon>
              Executar
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="4">
        <v-card elevation="2" class="test-card">
          <v-card-title class="pb-2">
            <v-icon class="mr-2" color="success">mdi-heart</v-icon>
            Análise de Sentimento
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-4">Testa o módulo de análise de sentimento com dados de exemplo.</p>
            <v-text-field
              v-model="testParams.sentimentText"
              label="Texto para análise"
              placeholder="Digite um texto para testar..."
              variant="outlined"
              density="compact"
              class="mb-2"
            />
            <v-btn
              block
              color="success"
              @click="runTest('sentiment_analysis')"
              :loading="loadingTests.sentiment_analysis"
            >
              <v-icon left>mdi-heart</v-icon>
              Analisar
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="4">
        <v-card elevation="2" class="test-card">
          <v-card-title class="pb-2">
            <v-icon class="mr-2" color="info">mdi-database</v-icon>
            Estatísticas Database
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-4">Gera estatísticas e análises dos dados no banco de dados.</p>
            <v-select
              v-model="testParams.dbTable"
              :items="dbTableOptions"
              label="Tabela"
              variant="outlined"
              density="compact"
              class="mb-2"
            />
            <v-btn
              block
              color="info"
              @click="runTest('database_stats')"
              :loading="loadingTests.database_stats"
            >
              <v-icon left>mdi-database</v-icon>
              Gerar Stats
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="4">
        <v-card elevation="2" class="test-card">
          <v-card-title class="pb-2">
            <v-icon class="mr-2" color="warning">mdi-test-tube</v-icon>
            Teste Completo
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-4">Executa uma bateria completa de testes em todos os módulos IA.</p>
            <v-btn
              block
              color="warning"
              @click="runTest('complete_test')"
              :loading="loadingTests.complete_test"
            >
              <v-icon left>mdi-test-tube</v-icon>
              Executar Completo
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="4">
        <v-card elevation="2" class="test-card">
          <v-card-title class="pb-2">
            <v-icon class="mr-2" color="purple">mdi-speedometer</v-icon>
            Teste de Performance
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-4">Avalia a performance e tempo de resposta dos serviços IA.</p>
            <v-slider
              v-model="testParams.iterations"
              label="Iterações"
              min="1"
              max="100"
              step="1"
              thumb-label
              class="mb-2"
            />
            <v-btn
              block
              color="purple"
              @click="runTest('performance_test')"
              :loading="loadingTests.performance_test"
            >
              <v-icon left>mdi-speedometer</v-icon>
              Testar Performance
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="4">
        <v-card elevation="2" class="test-card">
          <v-card-title class="pb-2">
            <v-icon class="mr-2" color="deep-orange">mdi-console</v-icon>
            Comando Personalizado
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-4">Executa um comando personalizado no sistema IA.</p>
            <v-text-field
              v-model="testParams.customCommand"
              label="Comando"
              placeholder="Ex: data_stats --verbose"
              variant="outlined"
              density="compact"
              class="mb-2"
            />
            <v-btn
              block
              color="deep-orange"
              @click="runTest('custom')"
              :loading="loadingTests.custom"
            >
              <v-icon left>mdi-console</v-icon>
              Executar
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Execution Log -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-file-document-outline</v-icon>
            Log de Execução
            <v-spacer />
            <v-chip
              :color="isExecuting ? 'success' : 'grey'"
              :class="{ 'pulse': isExecuting }"
              small
            >
              <v-icon left size="16">
                {{ isExecuting ? 'mdi-play' : 'mdi-stop' }}
              </v-icon>
              {{ isExecuting ? 'Executando' : 'Parado' }}
            </v-chip>
          </v-card-title>
          
          <v-card-text>
            <div class="log-container">
              <div
                v-for="(log, index) in executionLogs"
                :key="index"
                :class="['log-entry', `log-${log.type}`]"
              >
                <span class="log-timestamp">[{{ log.timestamp }}]</span>
                <span class="log-command">[{{ log.command }}]</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
              
              <div v-if="executionLogs.length === 0" class="text-center text-medium-emphasis py-8">
                <v-icon size="48" class="mb-4">mdi-file-document-outline</v-icon>
                <p>Nenhum log de execução disponível</p>
                <p class="text-caption">Execute um teste para ver os logs aqui</p>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- System Information -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-information</v-icon>
            Informações do Sistema
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <template #prepend>
                  <v-icon>mdi-server</v-icon>
                </template>
                <v-list-item-title>Status do Servidor</v-list-item-title>
                <template #append>
                  <v-chip color="success" size="small">Online</v-chip>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon>mdi-brain</v-icon>
                </template>
                <v-list-item-title>Módulos IA</v-list-item-title>
                <template #append>
                  <v-chip color="success" size="small">3 Ativos</v-chip>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon>mdi-database</v-icon>
                </template>
                <v-list-item-title>Conexão Database</v-list-item-title>
                <template #append>
                  <v-chip color="success" size="small">Conectado</v-chip>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon>mdi-clock</v-icon>
                </template>
                <v-list-item-title>Último Teste</v-list-item-title>
                <template #append>
                  <span class="text-caption">{{ lastTestTime || 'Nunca' }}</span>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Estatísticas de Teste
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <template #prepend>
                  <v-icon color="success">mdi-check-circle</v-icon>
                </template>
                <v-list-item-title>Testes Bem-sucedidos</v-list-item-title>
                <template #append>
                  <span class="font-weight-bold">{{ testStats.successful }}</span>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="error">mdi-close-circle</v-icon>
                </template>
                <v-list-item-title>Testes Falharam</v-list-item-title>
                <template #append>
                  <span class="font-weight-bold">{{ testStats.failed }}</span>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="info">mdi-play</v-icon>
                </template>
                <v-list-item-title>Total Executados</v-list-item-title>
                <template #append>
                  <span class="font-weight-bold">{{ testStats.total }}</span>
                </template>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="warning">mdi-speedometer</v-icon>
                </template>
                <v-list-item-title>Tempo Médio</v-list-item-title>
                <template #append>
                  <span class="font-weight-bold">{{ testStats.averageTime }}s</span>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
    >
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { AIService } from '@/services/aiApi'

console.log('AITesting carregado')

// Reactive data
const isExecuting = ref(false)
const lastTestTime = ref('')

const loadingTests = reactive({
  basic_test: false,
  sentiment_analysis: false,
  database_stats: false,
  complete_test: false,
  performance_test: false,
  custom: false
})

const testParams = reactive({
  sentimentText: 'Este é um texto de exemplo para análise',
  dbTable: 'players',
  iterations: 10,
  customCommand: ''
})

const testStats = ref({
  successful: 0,
  failed: 0,
  total: 0,
  averageTime: 0
})

const executionLogs = ref<any[]>([])

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 4000
})

// Options
const dbTableOptions = [
  { title: 'Players', value: 'players' },
  { title: 'Teams', value: 'teams' },
  { title: 'Matches', value: 'matches' },
  { title: 'Competitions', value: 'competitions' }
]

// Computed
const totalExecutions = computed(() => {
  return executionLogs.value.length
})

// Methods
const showSnackbar = (text: string, color: string = 'success') => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

const addLog = (command: string, message: string, type: string = 'info') => {
  const timestamp = new Date().toLocaleTimeString()
  executionLogs.value.unshift({
    timestamp,
    command,
    message,
    type
  })
  
  // Manter apenas os últimos 50 logs
  if (executionLogs.value.length > 50) {
    executionLogs.value = executionLogs.value.slice(0, 50)
  }
}

const updateTestStats = (success: boolean, duration: number) => {
  if (success) {
    testStats.value.successful++
  } else {
    testStats.value.failed++
  }
  
  testStats.value.total++
  
  // Calcular tempo médio
  const currentAvg = testStats.value.averageTime
  const newCount = testStats.value.total
  testStats.value.averageTime = Number(((currentAvg * (newCount - 1) + duration) / newCount).toFixed(2))
}

const runTest = async (testType: string) => {
  const startTime = Date.now()
  isExecuting.value = true
  loadingTests[testType as keyof typeof loadingTests] = true
  
  try {
    addLog(testType, `Iniciando teste: ${testType}`, 'info')
    
    // Mapear tipos de teste para actions da API
    const actionMap: Record<string, string> = {
      'basic_test': 'test_basic',
      'sentiment_analysis': 'analyze_sentiment',
      'database_stats': 'database_stats',
      'complete_test': 'test_all_services',
      'performance_test': 'test_basic', // Usar test_basic para performance
      'custom': testParams.customCommand || 'test_basic'
    }
    
    // Preparar payload baseado no tipo de teste
    let payload: any = { 
      action: actionMap[testType] || 'test_basic',
      limit: 3
    }
    
    switch (testType) {
      case 'sentiment_analysis':
        addLog(testType, `Analisando sentimento com action: ${payload.action}`, 'info')
        break
      case 'database_stats':
        addLog(testType, `Gerando estatísticas do banco`, 'info')
        break
      case 'performance_test':
        payload.limit = testParams.iterations
        addLog(testType, `Executando ${testParams.iterations} iterações`, 'info')
        break
      case 'custom':
        addLog(testType, `Comando personalizado: ${testParams.customCommand}`, 'info')
        break
    }
    
    // Fazer a chamada para a API usando o novo service
    const response = await AIService.runTest(actionMap[testType] || 'test_basic', {
      limit: testType === 'performance_test' ? testParams.iterations : 3
    })
    
    const duration = (Date.now() - startTime) / 1000
    
    if (response) {
      addLog(testType, `Teste concluído com sucesso em ${duration}s`, 'success')
      if (response.message) {
        addLog(testType, `Resultado: ${response.message}`, 'success')
      }
      updateTestStats(true, duration)
      showSnackbar(`Teste ${testType} executado com sucesso!`)
    }
    
  } catch (error: any) {
    const duration = (Date.now() - startTime) / 1000
    const errorMessage = error.response?.data?.message || error.message || 'Erro desconhecido'
    
    addLog(testType, `Erro no teste após ${duration}s: ${errorMessage}`, 'error')
    updateTestStats(false, duration)
    showSnackbar(`Erro no teste ${testType}: ${errorMessage}`, 'error')
    
  } finally {
    loadingTests[testType as keyof typeof loadingTests] = false
    isExecuting.value = Object.values(loadingTests).some(loading => loading)
    lastTestTime.value = new Date().toLocaleTimeString()
  }
}

const clearLogs = () => {
  executionLogs.value = []
  showSnackbar('Logs limpos com sucesso!')
}
</script>

<style scoped>
.test-card {
  height: 100%;
  transition: transform 0.2s ease-in-out;
}

.test-card:hover {
  transform: translateY(-4px);
}

.log-container {
  max-height: 400px;
  overflow-y: auto;
  background-color: #1e1e1e;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.log-entry {
  margin-bottom: 4px;
  line-height: 1.4;
}

.log-timestamp {
  color: #888;
}

.log-command {
  color: #61dafb;
  font-weight: bold;
  margin: 0 8px;
}

.log-message {
  color: #fff;
}

.log-info .log-message {
  color: #fff;
}

.log-success .log-message {
  color: #4caf50;
}

.log-error .log-message {
  color: #f44336;
}

.log-warning .log-message {
  color: #ff9800;
}

.pulse {
  animation: pulse 1.5s ease-in-out infinite alternate;
}

@keyframes pulse {
  from {
    opacity: 1;
  }
  to {
    opacity: 0.5;
  }
}

/* Dark theme support */
.v-theme--dark .log-container {
  background-color: #0d1117;
}
</style>
