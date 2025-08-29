<template>
  <v-container fluid>
    <!-- Header da página -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold">Gerenciar Enquetes</h1>
            <p class="text-body-1 text-medium-emphasis mt-1">
              Administre todas as enquetes e votações da plataforma
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

    <!-- Cards de Métricas Rápidas -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="1" class="text-center">
          <v-card-text>
            <v-icon size="36" color="primary" class="mb-2">mdi-poll</v-icon>
            <p class="text-h6 font-weight-bold">{{ metrics.total }}</p>
            <p class="text-body-2 text-grey">Total</p>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="1" class="text-center">
          <v-card-text>
            <v-icon size="36" color="success" class="mb-2">mdi-play-circle</v-icon>
            <p class="text-h6 font-weight-bold">{{ metrics.active }}</p>
            <p class="text-body-2 text-grey">Ativas</p>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="1" class="text-center">
          <v-card-text>
            <v-icon size="36" color="warning" class="mb-2">mdi-file-edit</v-icon>
            <p class="text-h6 font-weight-bold">{{ metrics.draft }}</p>
            <p class="text-body-2 text-grey">Rascunhos</p>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="1" class="text-center">
          <v-card-text>
            <v-icon size="36" color="grey" class="mb-2">mdi-stop-circle</v-icon>
            <p class="text-h6 font-weight-bold">{{ metrics.closed }}</p>
            <p class="text-body-2 text-grey">Encerradas</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filtros e Busca -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="Status"
          variant="outlined"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="authorFilter"
          :items="authorOptions"
          label="Autor"
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
          label="Ordenar por"
          variant="outlined"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-text-field
          v-model="searchQuery"
          label="Buscar enquetes..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @update:model-value="debounceSearch"
        />
      </v-col>
    </v-row>

    <!-- Tabela de Enquetes -->
    <v-card elevation="2">
      <v-data-table-server
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        v-model:sort-by="tableSortBy"
        :headers="headers"
        :items="polls"
        :items-length="totalPolls"
        :loading="loading"
        :search="searchQuery"
        @update:options="handleTableUpdate"
      >
        <!-- Título -->
        <template #item.title="{ item }">
          <div class="max-width-300">
            <p class="text-body-2 font-weight-medium text-truncate">{{ item.title }}</p>
            <p class="text-caption text-grey text-truncate">
              {{ item.description || 'Sem descrição' }}
            </p>
          </div>
        </template>
        
        <!-- Status -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            variant="tonal"
            size="small"
          >
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>
        
        <!-- Autor -->
        <template #item.author="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-2">
              <v-img 
                v-if="item.author.avatar"
                :src="item.author.avatar"
                :alt="item.author.username"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
            <div>
              <p class="text-body-2 font-weight-medium">{{ item.author.username }}</p>
              <p class="text-caption text-grey">{{ item.author.email }}</p>
            </div>
          </div>
        </template>
        
        <!-- Participação -->
        <template #item.participation="{ item }">
          <div class="text-center">
            <p class="text-h6 font-weight-bold">{{ item.votes_count }}</p>
            <p class="text-caption">votos</p>
            <v-progress-linear
              :model-value="calculateParticipationPercentage(item)"
              color="primary"
              height="4"
              rounded
              class="mt-1"
            />
          </div>
        </template>
        
        <!-- Opções -->
        <template #item.options_count="{ item }">
          <div class="text-center">
            <v-chip variant="outlined" size="small">
              {{ item.options.length }} opções
            </v-chip>
          </div>
        </template>
        
        <!-- Data de Criação -->
        <template #item.created_at="{ item }">
          <div>
            <p class="text-body-2">{{ formatDate(item.created_at) }}</p>
            <p class="text-caption text-grey">{{ formatTime(item.created_at) }}</p>
          </div>
        </template>
        
        <!-- Ações -->
        <template #item.actions="{ item }">
          <div class="d-flex align-center">
            <v-btn
              icon="mdi-eye"
              variant="text"
              size="small"
              @click="viewPoll(item)"
            />
            
            <v-btn
              icon="mdi-pencil"
              variant="text"
              size="small"
              @click="editPoll(item)"
            />
            
            <v-btn
              v-if="item.status === 'draft'"
              icon="mdi-play"
              variant="text"
              size="small"
              color="success"
              @click="activatePoll(item)"
            />
            
            <v-btn
              v-if="item.status === 'active'"
              icon="mdi-stop"
              variant="text"
              size="small"
              color="warning"
              @click="closePoll(item)"
            />
            
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              color="error"
              @click="deletePoll(item)"
            />
          </div>
        </template>
        
        <!-- Loading -->
        <template #loading>
          <v-skeleton-loader type="table-row@10" />
        </template>
        
        <!-- No Data -->
        <template #no-data>
          <div class="text-center py-8">
            <v-icon size="64" color="grey-lighten-1">mdi-poll-box-outline</v-icon>
            <h3 class="text-h6 mt-4">Nenhuma enquete encontrada</h3>
            <p class="text-body-2 text-grey mt-2">
              {{ searchQuery ? 'Tente ajustar os filtros de busca' : 'Comece criando sua primeira enquete' }}
            </p>
            <v-btn
              v-if="!searchQuery"
              color="primary"
              class="mt-4"
              @click="createPoll"
            >
              Criar Enquete
            </v-btn>
          </div>
        </template>
      </v-data-table-server>
    </v-card>

    <!-- Dialog de Visualização da Enquete -->
    <v-dialog v-model="pollDialog" max-width="900">
      <v-card v-if="selectedPoll">
        <v-card-title>
          <v-icon class="mr-2">mdi-poll</v-icon>
          {{ selectedPoll.title }}
          <v-spacer />
          <v-chip
            :color="getStatusColor(selectedPoll.status)"
            variant="tonal"
          >
            {{ getStatusText(selectedPoll.status) }}
          </v-chip>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <!-- Informações da Enquete -->
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
                  <v-list-item-subtitle>{{ formatFullDate(selectedPoll.created_at) }}</v-list-item-subtitle>
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
                    <v-icon>mdi-format-list-bulleted</v-icon>
                  </template>
                  <v-list-item-title>Opções</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedPoll.options.length }} opções</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            
            <!-- Resultados -->
            <v-col cols="12" md="6">
              <h4 class="text-h6 mb-3">Resultados</h4>
              
              <div v-if="selectedPoll.votes_count > 0">
                <div v-for="option in selectedPoll.options" :key="option.id" class="mb-4">
                  <div class="d-flex justify-space-between align-center mb-2">
                    <span class="text-body-2 font-weight-medium">{{ option.text }}</span>
                    <div class="text-right">
                      <span class="text-body-2">{{ option.votes_count }} votos</span>
                      <br>
                      <span class="text-caption text-grey">{{ option.percentage.toFixed(1) }}%</span>
                    </div>
                  </div>
                  <v-progress-linear
                    :model-value="option.percentage"
                    color="primary"
                    height="12"
                    rounded
                  />
                </div>
              </div>
              
              <div v-else class="text-center py-4">
                <v-icon size="48" color="grey-lighten-1">mdi-vote-outline</v-icon>
                <p class="text-body-2 text-grey mt-2">Nenhum voto ainda</p>
              </div>
            </v-col>
            
            <!-- Descrição -->
            <v-col cols="12">
              <h4 class="text-h6 mb-3">Descrição</h4>
              <p class="text-body-2">{{ selectedPoll.description || 'Nenhuma descrição fornecida.' }}</p>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-btn
            v-if="selectedPoll.status === 'draft'"
            color="success"
            variant="outlined"
            @click="activatePoll(selectedPoll)"
          >
            Ativar
          </v-btn>
          
          <v-btn
            v-if="selectedPoll.status === 'active'"
            color="warning"
            variant="outlined"
            @click="closePoll(selectedPoll)"
          >
            Encerrar
          </v-btn>
          
          <v-spacer />
          
          <v-btn @click="pollDialog = false">
            Fechar
          </v-btn>
          
          <v-btn
            color="primary"
            @click="editPoll(selectedPoll)"
          >
            Editar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Confirmação de Exclusão -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2" color="error">mdi-delete</v-icon>
          Confirmar Exclusão
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir a enquete <strong>"{{ pollToDelete?.title }}"</strong>?
          <br><br>
          <v-alert
            v-if="pollToDelete?.votes_count && pollToDelete.votes_count > 0"
            type="warning"
            variant="tonal"
            class="mt-3"
          >
            Esta enquete possui {{ pollToDelete.votes_count }} voto(s).
            Esta ação não pode ser desfeita.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn
            color="error"
            :loading="deleting"
            @click="confirmDelete"
          >
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Estado local
const loading = ref(false)
const deleting = ref(false)
const pollDialog = ref(false)
const deleteDialog = ref(false)
const selectedPoll = ref(null)
const pollToDelete = ref(null)
const page = ref(1)
const itemsPerPage = ref(10)
const tableSortBy = ref([])

// Filtros
const statusFilter = ref('all')
const authorFilter = ref('')
const sortBy = ref('created_at_desc')
const searchQuery = ref('')

// Mock data - substituir por dados reais
const metrics = ref({
  total: 42,
  active: 18,
  draft: 8,
  closed: 16
})

const polls = ref([
  {
    id: 1,
    title: 'Qual será o campeão da Copa do Mundo?',
    description: 'Enquete sobre as expectativas para a próxima Copa do Mundo.',
    status: 'active',
    author: {
      username: 'admin',
      email: 'admin@markfoot.com',
      avatar: null
    },
    votes_count: 284,
    options: [
      { id: 1, text: 'Brasil', votes_count: 95, percentage: 33.4 },
      { id: 2, text: 'Argentina', votes_count: 78, percentage: 27.5 },
      { id: 3, text: 'França', votes_count: 67, percentage: 23.6 },
      { id: 4, text: 'Outros', votes_count: 44, percentage: 15.5 }
    ],
    created_at: '2024-01-10T10:00:00Z'
  },
  {
    id: 2,
    title: 'Melhor estratégia para apostas múltiplas?',
    description: 'Discussão sobre diferentes abordagens em apostas múltiplas.',
    status: 'active',
    author: {
      username: 'expert_trader',
      email: 'trader@markfoot.com',
      avatar: null
    },
    votes_count: 156,
    options: [
      { id: 5, text: 'Baixo risco, baixo retorno', votes_count: 62, percentage: 39.7 },
      { id: 6, text: 'Alto risco, alto retorno', votes_count: 47, percentage: 30.1 },
      { id: 7, text: 'Estratégia mista', votes_count: 47, percentage: 30.1 }
    ],
    created_at: '2024-01-12T14:30:00Z'
  },
  {
    id: 3,
    title: 'Qual time tem melhor defesa na Premier League?',
    description: '',
    status: 'draft',
    author: {
      username: 'futbol_fan',
      email: 'fan@markfoot.com',
      avatar: null
    },
    votes_count: 0,
    options: [
      { id: 8, text: 'Manchester City', votes_count: 0, percentage: 0 },
      { id: 9, text: 'Liverpool', votes_count: 0, percentage: 0 },
      { id: 10, text: 'Arsenal', votes_count: 0, percentage: 0 }
    ],
    created_at: '2024-01-15T09:15:00Z'
  }
])

// Computed
const totalPolls = computed(() => polls.value.length)

// Options
const statusOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Ativas', value: 'active' },
  { title: 'Rascunhos', value: 'draft' },
  { title: 'Encerradas', value: 'closed' }
]

const authorOptions = computed(() => {
  const authors = Array.from(new Set(polls.value.map((poll: any) => poll.author.username)))
  return authors.map(author => ({ title: author, value: author }))
})

const sortOptions = [
  { title: 'Mais Recentes', value: 'created_at_desc' },
  { title: 'Mais Antigas', value: 'created_at_asc' },
  { title: 'Mais Votadas', value: 'votes_desc' },
  { title: 'Menos Votadas', value: 'votes_asc' },
  { title: 'A-Z', value: 'title_asc' },
  { title: 'Z-A', value: 'title_desc' }
]

const headers = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: 'Título', key: 'title', width: '300px' },
  { title: 'Status', key: 'status', width: '120px' },
  { title: 'Autor', key: 'author', width: '200px' },
  { title: 'Participação', key: 'participation', width: '150px', sortable: false },
  { title: 'Opções', key: 'options_count', width: '120px', sortable: false },
  { title: 'Criada em', key: 'created_at', width: '150px' },
  { title: 'Ações', key: 'actions', width: '180px', sortable: false }
]

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

const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString('pt-BR', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const formatFullDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('pt-BR')
}

const calculateParticipationPercentage = (poll: any) => {
  // Simular cálculo baseado no total de usuários (assumindo 500 usuários ativos)
  const totalActiveUsers = 500
  return Math.min((poll.votes_count / totalActiveUsers) * 100, 100)
}

// Methods
let searchTimeout: number
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // A busca será implementada com a API real
  }, 300)
}

const applyFilters = () => {
  // Os filtros serão implementados com a API real
}

const handleTableUpdate = (_options: any) => {
  // Implementar paginação e ordenação com API real
}

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

const activatePoll = async (poll: any) => {
  try {
    // Implementar ativação via API
    poll.status = 'active'
    pollDialog.value = false
  } catch (error) {
    console.error('Erro ao ativar enquete:', error)
  }
}

const closePoll = async (poll: any) => {
  try {
    // Implementar encerramento via API
    poll.status = 'closed'
    pollDialog.value = false
  } catch (error) {
    console.error('Erro ao encerrar enquete:', error)
  }
}

const deletePoll = (poll: any) => {
  pollToDelete.value = poll
  deleteDialog.value = true
}

const confirmDelete = async () => {
  if (!pollToDelete.value) return
  
  deleting.value = true
  try {
    // Implementar exclusão via API
    const index = polls.value.findIndex((p: any) => p.id === pollToDelete.value.id)
    if (index !== -1) {
      polls.value.splice(index, 1)
    }
    deleteDialog.value = false
    pollToDelete.value = null
  } catch (error) {
    console.error('Erro ao deletar enquete:', error)
  } finally {
    deleting.value = false
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // Carregar dados reais via store/API
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simular carregamento
  } catch (error) {
    console.error('Erro ao carregar enquetes:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.max-width-300 {
  max-width: 300px;
}
</style>
