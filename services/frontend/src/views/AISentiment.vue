<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold mb-2">
              <v-icon class="mr-3" color="success">mdi-heart</v-icon>
              Análise de Sentimento
            </h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              Gerenciamento e visualização de análises de sentimento
            </p>
          </div>
          <v-btn
            color="success"
            @click="refreshData"
            :loading="loading"
          >
            <v-icon left>mdi-refresh</v-icon>
            Atualizar
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-filter</v-icon>
            Filtros
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.sentiment"
                  :items="sentimentOptions"
                  label="Sentimento"
                  clearable
                  variant="outlined"
                  density="compact"
                />
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.platform"
                  :items="platformOptions"
                  label="Plataforma"
                  clearable
                  variant="outlined"
                  density="compact"
                />
              </v-col>
              
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="filters.search"
                  label="Buscar texto"
                  clearable
                  variant="outlined"
                  density="compact"
                  prepend-inner-icon="mdi-magnify"
                />
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.limit"
                  :items="limitOptions"
                  label="Limite"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12">
                <v-btn
                  color="primary"
                  @click="applyFilters"
                  :loading="loadingData"
                  class="mr-2"
                >
                  <v-icon left>mdi-filter-check</v-icon>
                  Aplicar Filtros
                </v-btn>
                
                <v-btn
                  variant="outlined"
                  @click="clearFilters"
                >
                  <v-icon left>mdi-filter-remove</v-icon>
                  Limpar
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-card color="success" dark elevation="2">
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-caption">Sentimentos Positivos</div>
                <div class="text-h4 font-weight-bold">{{ sentimentStats.positive || 0 }}</div>
                <div class="text-caption">
                  {{ sentimentStats.positivePercent || 0 }}% do total
                </div>
              </div>
              <v-icon size="48">mdi-emoticon-happy</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card color="warning" dark elevation="2">
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-caption">Sentimentos Neutros</div>
                <div class="text-h4 font-weight-bold">{{ sentimentStats.neutral || 0 }}</div>
                <div class="text-caption">
                  {{ sentimentStats.neutralPercent || 0 }}% do total
                </div>
              </div>
              <v-icon size="48">mdi-emoticon-neutral</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card color="error" dark elevation="2">
          <v-card-text>
            <div class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="text-caption">Sentimentos Negativos</div>
                <div class="text-h4 font-weight-bold">{{ sentimentStats.negative || 0 }}</div>
                <div class="text-caption">
                  {{ sentimentStats.negativePercent || 0 }}% do total
                </div>
              </div>
              <v-icon size="48">mdi-emoticon-sad</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Data Table -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-table</v-icon>
            Dados de Sentimento
            <v-spacer />
            <span class="text-caption">
              Total: {{ sentimentData.length }} registros
            </span>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="tableHeaders"
              :items="sentimentData"
              :loading="loadingData"
              item-value="id"
              class="elevation-1"
              :items-per-page="10"
            >
              <!-- Sentiment Column -->
              <template v-slot:item.sentiment="{ item }">
                <v-chip
                  :color="getSentimentColor(item.sentiment)"
                  dark
                  small
                >
                  <v-icon left size="16">
                    {{ getSentimentIcon(item.sentiment) }}
                  </v-icon>
                  {{ item.sentiment }}
                </v-chip>
              </template>

              <!-- Confidence Column -->
              <template v-slot:item.confidence="{ item }">
                <div class="d-flex align-center">
                  <v-progress-linear
                    :model-value="item.confidence * 100"
                    :color="getConfidenceColor(item.confidence)"
                    height="8"
                    rounded
                    class="mr-2"
                    style="min-width: 60px;"
                  />
                  <span class="text-caption">{{ (item.confidence * 100).toFixed(1) }}%</span>
                </div>
              </template>

              <!-- Text Column -->
              <template v-slot:item.text="{ item }">
                <div style="max-width: 300px;">
                  <span :title="item.text">
                    {{ item.text.length > 100 ? item.text.substring(0, 100) + '...' : item.text }}
                  </span>
                </div>
              </template>

              <!-- Platform Column -->
              <template v-slot:item.platform="{ item }">
                <v-chip
                  variant="outlined"
                  small
                >
                  {{ item.platform }}
                </v-chip>
              </template>

              <!-- Actions Column -->
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewDetails(item)"
                />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteItem(item)"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Detail Dialog -->
    <v-dialog v-model="detailDialog" max-width="600">
      <v-card v-if="selectedItem">
        <v-card-title>
          <v-icon class="mr-2">mdi-information</v-icon>
          Detalhes da Análise
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <div class="mb-4">
                <h4>Texto Analisado:</h4>
                <p class="mt-2">{{ selectedItem.text }}</p>
              </div>
              
              <v-divider class="mb-4" />
              
              <v-row>
                <v-col cols="6">
                  <div>
                    <h4>Sentimento:</h4>
                    <v-chip
                      :color="getSentimentColor(selectedItem.sentiment)"
                      dark
                      class="mt-2"
                    >
                      <v-icon left>{{ getSentimentIcon(selectedItem.sentiment) }}</v-icon>
                      {{ selectedItem.sentiment }}
                    </v-chip>
                  </div>
                </v-col>
                
                <v-col cols="6">
                  <div>
                    <h4>Confiança:</h4>
                    <div class="d-flex align-center mt-2">
                      <v-progress-linear
                        :model-value="selectedItem.confidence * 100"
                        :color="getConfidenceColor(selectedItem.confidence)"
                        height="12"
                        rounded
                        class="mr-2"
                      />
                      <span>{{ (selectedItem.confidence * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                </v-col>
              </v-row>
              
              <v-divider class="my-4" />
              
              <v-row>
                <v-col cols="6">
                  <div>
                    <h4>Plataforma:</h4>
                    <v-chip variant="outlined" class="mt-2">
                      {{ selectedItem.platform }}
                    </v-chip>
                  </div>
                </v-col>
                
                <v-col cols="6">
                  <div>
                    <h4>Data de Análise:</h4>
                    <p class="mt-2">{{ selectedItem.created_at }}</p>
                  </div>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="detailDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
import { ref, reactive, onMounted } from 'vue'
import { AIService } from '@/services/aiApi'

console.log('AISentiment carregado')

// Reactive data
const loading = ref(false)
const loadingData = ref(false)
const detailDialog = ref(false)
const selectedItem = ref<any>(null)

const filters = reactive({
  sentiment: null,
  platform: null,
  search: '',
  limit: 50
})

const sentimentStats = ref({
  positive: 0,
  neutral: 0,
  negative: 0,
  positivePercent: 0,
  neutralPercent: 0,
  negativePercent: 0
})

const sentimentData = ref([
  {
    id: 1,
    text: 'Este jogo foi absolutamente fantástico! Melhor partida do ano.',
    sentiment: 'positive',
    confidence: 0.95,
    platform: 'Twitter',
    created_at: '2024-01-15 10:30:00'
  },
  {
    id: 2,
    text: 'Partida decepcionante, esperava muito mais do time.',
    sentiment: 'negative',
    confidence: 0.87,
    platform: 'Facebook',
    created_at: '2024-01-15 11:45:00'
  },
  {
    id: 3,
    text: 'Jogo normal, nada de especial aconteceu.',
    sentiment: 'neutral',
    confidence: 0.72,
    platform: 'Instagram',
    created_at: '2024-01-15 12:15:00'
  }
])

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 4000
})

// Options
const sentimentOptions = [
  { title: 'Positivo', value: 'positive' },
  { title: 'Neutro', value: 'neutral' },
  { title: 'Negativo', value: 'negative' }
]

const platformOptions = [
  { title: 'Twitter', value: 'twitter' },
  { title: 'Facebook', value: 'facebook' },
  { title: 'Instagram', value: 'instagram' },
  { title: 'Reddit', value: 'reddit' }
]

const limitOptions = [
  { title: '10', value: 10 },
  { title: '25', value: 25 },
  { title: '50', value: 50 },
  { title: '100', value: 100 }
]

const tableHeaders = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: 'Texto', key: 'text', width: '300px' },
  { title: 'Sentimento', key: 'sentiment', width: '120px' },
  { title: 'Confiança', key: 'confidence', width: '150px' },
  { title: 'Plataforma', key: 'platform', width: '120px' },
  { title: 'Data', key: 'created_at', width: '150px' },
  { title: 'Ações', key: 'actions', width: '100px', sortable: false }
]

// Methods
const showSnackbar = (text: string, color: string = 'success') => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

const getSentimentColor = (sentiment: string) => {
  switch (sentiment.toLowerCase()) {
    case 'positive': return 'success'
    case 'negative': return 'error'
    case 'neutral': return 'warning'
    default: return 'grey'
  }
}

const getSentimentIcon = (sentiment: string) => {
  switch (sentiment.toLowerCase()) {
    case 'positive': return 'mdi-emoticon-happy'
    case 'negative': return 'mdi-emoticon-sad'
    case 'neutral': return 'mdi-emoticon-neutral'
    default: return 'mdi-help'
  }
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'error'
}

const calculateStats = () => {
  const total = sentimentData.value.length
  const positive = sentimentData.value.filter(item => item.sentiment === 'positive').length
  const negative = sentimentData.value.filter(item => item.sentiment === 'negative').length
  const neutral = sentimentData.value.filter(item => item.sentiment === 'neutral').length

  sentimentStats.value = {
    positive,
    negative,
    neutral,
    positivePercent: total > 0 ? Math.round((positive / total) * 100) : 0,
    negativePercent: total > 0 ? Math.round((negative / total) * 100) : 0,
    neutralPercent: total > 0 ? Math.round((neutral / total) * 100) : 0
  }
}

const fetchSentimentData = async () => {
  try {
    loadingData.value = true
    
    const params: any = {}
    if (filters.limit) params.limit = filters.limit

    const response = await AIService.getSentimentData(params)
    
    if (response && response.data) {
      // Mapear dados da API para o formato da tela
      sentimentData.value = response.data.map((item: any) => ({
        id: item.id,
        text: `Análise de ${item.entity_type} ID ${item.entity_id}`,
        sentiment: item.sentiment,
        confidence: item.confidence,
        platform: item.source_platform || 'Sistema',
        created_at: new Date(item.created_at).toLocaleString('pt-BR')
      }))
    } else {
      // Manter dados simulados se a API não retornar dados
      console.log('API retornou dados vazios, usando dados simulados')
    }
    
    calculateStats()
  } catch (error) {
    console.error('Erro ao buscar dados de sentimento:', error)
    showSnackbar('Usando dados simulados (API não disponível)', 'info')
    calculateStats()
  } finally {
    loadingData.value = false
  }
}

const refreshData = async () => {
  await fetchSentimentData()
  showSnackbar('Dados atualizados com sucesso!')
}

const applyFilters = async () => {
  await fetchSentimentData()
}

const clearFilters = () => {
  filters.sentiment = null
  filters.platform = null
  filters.search = ''
  filters.limit = 50
  fetchSentimentData()
}

const viewDetails = (item: any) => {
  selectedItem.value = item
  detailDialog.value = true
}

const deleteItem = (item: any) => {
  const index = sentimentData.value.findIndex(d => d.id === item.id)
  if (index > -1) {
    sentimentData.value.splice(index, 1)
    calculateStats()
    showSnackbar('Item removido com sucesso!')
  }
}

// Lifecycle
onMounted(() => {
  fetchSentimentData()
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
