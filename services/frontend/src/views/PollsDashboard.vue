<template>
  <v-container fluid>
    <!-- Header da página -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold">Dashboard de Enquetes</h1>
            <p class="text-body-1 text-medium-emphasis mt-1">
              Visão geral das enquetes e votações dos usuários
            </p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="createPoll"
          >
            Nova Enquete
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Cards de Estatísticas -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="primary" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h4 font-weight-bold">{{ stats.total_polls }}</p>
                <p class="text-body-2">Total de Enquetes</p>
              </div>
              <v-icon size="48" class="opacity-80">mdi-poll</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="success" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h4 font-weight-bold">{{ stats.active_polls }}</p>
                <p class="text-body-2">Enquetes Ativas</p>
              </div>
              <v-icon size="48" class="opacity-80">mdi-chart-line</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="info" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h4 font-weight-bold">{{ stats.total_votes }}</p>
                <p class="text-body-2">Total de Votos</p>
              </div>
              <v-icon size="48" class="opacity-80">mdi-vote</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="warning" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h4 font-weight-bold">{{ stats.avg_participation }}%</p>
                <p class="text-body-2">Participação Média</p>
              </div>
              <v-icon size="48" class="opacity-80">mdi-account-group</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Gráficos -->
    <v-row class="mb-6">
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-bar</v-icon>
            Participação em Enquetes (Últimos 30 dias)
          </v-card-title>
          <v-card-text>
            <div style="height: 300px;">
              <LineChart 
                :data="participationChartData" 
                :options="chartOptions"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-donut</v-icon>
            Status das Enquetes
          </v-card-title>
          <v-card-text>
            <div style="height: 300px;">
              <DoughnutChart 
                :data="statusChartData" 
                :options="doughnutOptions"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Enquetes Populares e Recentes -->
    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-fire</v-icon>
            Enquetes Mais Populares
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="poll in popularPolls"
                :key="poll.id"
                @click="viewPoll(poll)"
              >
                <template #prepend>
                  <v-avatar color="primary" size="40">
                    <span class="text-white font-weight-bold">{{ poll.votes_count }}</span>
                  </v-avatar>
                </template>
                
                <v-list-item-title class="font-weight-medium">
                  {{ poll.title }}
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  {{ poll.votes_count }} votos • {{ poll.options.length }} opções
                </v-list-item-subtitle>
                
                <template #append>
                  <v-chip
                    :color="getStatusColor(poll.status)"
                    variant="tonal"
                    size="small"
                  >
                    {{ getStatusText(poll.status) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
          
          <v-card-actions>
            <v-btn variant="text" @click="$router.push('/polls/management')">
              Ver Todas
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-clock-outline</v-icon>
            Enquetes Recentes
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="poll in recentPolls"
                :key="poll.id"
                @click="viewPoll(poll)"
              >
                <template #prepend>
                  <v-avatar :color="getStatusColor(poll.status)" size="40">
                    <v-icon color="white">mdi-poll</v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title class="font-weight-medium">
                  {{ poll.title }}
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  Criada {{ formatRelativeTime(poll.created_at) }} por {{ poll.author.username }}
                </v-list-item-subtitle>
                
                <template #append>
                  <v-chip
                    :color="getStatusColor(poll.status)"
                    variant="tonal"
                    size="small"
                  >
                    {{ getStatusText(poll.status) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
          
          <v-card-actions>
            <v-btn variant="text" @click="createPoll">
              Criar Nova
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Ações Rápidas -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  variant="outlined"
                  size="large"
                  prepend-icon="mdi-plus"
                  @click="createPoll"
                >
                  Criar Enquete
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  variant="outlined"
                  size="large"
                  prepend-icon="mdi-format-list-bulleted"
                  @click="$router.push('/polls/management')"
                >
                  Gerenciar Enquetes
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  variant="outlined"
                  size="large"
                  prepend-icon="mdi-chart-bar"
                  @click="viewAnalytics"
                >
                  Ver Relatórios
                </v-btn>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-btn
                  block
                  variant="outlined"
                  size="large"
                  prepend-icon="mdi-cog"
                  @click="pollSettings"
                >
                  Configurações
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog de Detalhes da Enquete -->
    <v-dialog v-model="pollDialog" max-width="800">
      <v-card v-if="selectedPoll">
        <v-card-title>
          <v-icon class="mr-2">mdi-poll</v-icon>
          {{ selectedPoll.title }}
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <h4 class="text-h6 mb-3">Informações</h4>
              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-account</v-icon>
                  </template>
                  <v-list-item-title>Autor</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPoll.author.username }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-calendar</v-icon>
                  </template>
                  <v-list-item-title>Criada em</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDate(selectedPoll.created_at) }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-vote</v-icon>
                  </template>
                  <v-list-item-title>Total de Votos</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPoll.votes_count }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-information</v-icon>
                  </template>
                  <v-list-item-title>Status</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip
                      :color="getStatusColor(selectedPoll.status)"
                      variant="tonal"
                      size="small"
                    >
                      {{ getStatusText(selectedPoll.status) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            
            <v-col cols="12" md="6">
              <h4 class="text-h6 mb-3">Resultados</h4>
              <div v-for="option in selectedPoll.options" :key="option.id" class="mb-3">
                <div class="d-flex justify-space-between align-center mb-1">
                  <span class="text-body-2">{{ option.text }}</span>
                  <span class="text-caption">{{ option.votes_count }} votos</span>
                </div>
                <v-progress-linear
                  :model-value="option.percentage"
                  color="primary"
                  height="8"
                  rounded
                />
                <div class="text-caption text-grey mt-1">{{ option.percentage.toFixed(1) }}%</div>
              </div>
            </v-col>
          </v-row>
          
          <v-divider class="my-4" />
          
          <div>
            <h4 class="text-h6 mb-3">Descrição</h4>
            <p class="text-body-2">{{ selectedPoll.description || 'Nenhuma descrição fornecida.' }}</p>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="pollDialog = false">Fechar</v-btn>
          <v-btn
            color="primary"
            @click="editPoll(selectedPoll)"
          >
            Editar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LineChart from '@/components/charts/LineChart.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

const router = useRouter()

// Estado local
const loading = ref(false)
const pollDialog = ref(false)
const selectedPoll = ref(null)

// Mock data - substituir por dados reais do store
const stats = ref({
  total_polls: 42,
  active_polls: 18,
  total_votes: 1247,
  avg_participation: 73
})

const popularPolls = ref([
  {
    id: 1,
    title: 'Qual será o campeão da Copa do Mundo?',
    votes_count: 284,
    status: 'active',
    options: [
      { id: 1, text: 'Brasil', votes_count: 95, percentage: 33.4 },
      { id: 2, text: 'Argentina', votes_count: 78, percentage: 27.5 },
      { id: 3, text: 'França', votes_count: 67, percentage: 23.6 },
      { id: 4, text: 'Outros', votes_count: 44, percentage: 15.5 }
    ],
    author: { username: 'admin' },
    created_at: '2024-01-10T10:00:00Z',
    description: 'Enquete sobre as expectativas para a próxima Copa do Mundo.'
  },
  {
    id: 2,
    title: 'Melhor estratégia para apostas múltiplas?',
    votes_count: 156,
    status: 'active',
    options: [
      { id: 5, text: 'Baixo risco, baixo retorno', votes_count: 62, percentage: 39.7 },
      { id: 6, text: 'Alto risco, alto retorno', votes_count: 47, percentage: 30.1 },
      { id: 7, text: 'Estratégia mista', votes_count: 47, percentage: 30.1 }
    ],
    author: { username: 'expert_trader' },
    created_at: '2024-01-12T14:30:00Z',
    description: 'Discussão sobre diferentes abordagens em apostas múltiplas.'
  }
])

const recentPolls = ref([
  {
    id: 3,
    title: 'Qual time tem melhor defesa na Premier League?',
    status: 'active',
    author: { username: 'futbol_fan' },
    created_at: '2024-01-15T09:15:00Z',
    votes_count: 89,
    options: [],
    description: ''
  },
  {
    id: 4,
    title: 'Investir em criptomoedas vale a pena?',
    status: 'draft',
    author: { username: 'crypto_master' },
    created_at: '2024-01-14T16:45:00Z',
    votes_count: 0,
    options: [],
    description: ''
  }
])

const participationChartData = ref({
  labels: ['Jan 1', 'Jan 3', 'Jan 5', 'Jan 7', 'Jan 9', 'Jan 11', 'Jan 13', 'Jan 15'],
  datasets: [{
    label: 'Votos por dia',
    data: [12, 19, 15, 25, 22, 18, 30, 28],
    borderColor: 'rgb(75, 192, 192)',
    backgroundColor: 'rgba(75, 192, 192, 0.1)',
    tension: 0.4
  }]
})

const statusChartData = ref({
  labels: ['Ativas', 'Rascunho', 'Encerradas'],
  datasets: [{
    data: [18, 8, 16],
    backgroundColor: [
      'rgba(76, 175, 80, 0.8)',
      'rgba(255, 193, 7, 0.8)',
      'rgba(158, 158, 158, 0.8)'
    ],
    borderColor: [
      'rgba(76, 175, 80, 1)',
      'rgba(255, 193, 7, 1)',
      'rgba(158, 158, 158, 1)'
    ],
    borderWidth: 2
  }]
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
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
      position: 'bottom'
    }
  }
})

// Helper functions
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    active: 'success',
    draft: 'warning',
    closed: 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    active: 'Ativa',
    draft: 'Rascunho',
    closed: 'Encerrada'
  }
  return texts[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const formatRelativeTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) return 'há 1 dia'
  if (diffDays < 7) return `há ${diffDays} dias`
  if (diffDays < 30) return `há ${Math.ceil(diffDays / 7)} semanas`
  return `há ${Math.ceil(diffDays / 30)} meses`
}

// Methods
const viewPoll = (poll: any) => {
  selectedPoll.value = poll
  pollDialog.value = true
}

const createPoll = () => {
  router.push('/polls/create')
}

const editPoll = (poll: any) => {
  router.push(`/polls/edit/${poll.id}`)
}

const viewAnalytics = () => {
  router.push('/polls/analytics')
}

const pollSettings = () => {
  router.push('/polls/settings')
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // Carregar dados reais via store/API
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simular carregamento
  } catch (error) {
    console.error('Erro ao carregar dados:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.opacity-80 {
  opacity: 0.8;
}
</style>
