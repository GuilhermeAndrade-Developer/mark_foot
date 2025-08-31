<template>
  <v-container fluid>
    <!-- Header da página -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold">Relatórios de Conteúdo</h1>
            <p class="text-body-1 text-medium-emphasis mt-1">
              Denúncias e moderação de conteúdo dos usuários
            </p>
          </div>
          <v-chip
            v-if="pendingReports > 0"
            color="error"
            variant="elevated"
            prepend-icon="mdi-alert"
          >
            {{ pendingReports }} pendentes
          </v-chip>
        </div>
      </v-col>
    </v-row>

    <!-- Cards de Estatísticas -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h6 font-weight-bold">{{ stats.total_reports }}</p>
                <p class="text-body-2 text-grey">Total de Denúncias</p>
              </div>
              <v-icon size="40" color="primary">mdi-flag</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h6 font-weight-bold">{{ stats.pending_reports }}</p>
                <p class="text-body-2 text-grey">Pendentes</p>
              </div>
              <v-icon size="40" color="warning">mdi-clock-alert</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h6 font-weight-bold">{{ stats.approved_reports }}</p>
                <p class="text-body-2 text-grey">Procedentes</p>
              </div>
              <v-icon size="40" color="success">mdi-check-circle</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-h6 font-weight-bold">{{ stats.rejected_reports }}</p>
                <p class="text-body-2 text-grey">Improcedentes</p>
              </div>
              <v-icon size="40" color="error">mdi-close-circle</v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filtros -->
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
          v-model="typeFilter"
          :items="typeOptions"
          label="Tipo de Conteúdo"
          variant="outlined"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="reasonFilter"
          :items="reasonOptions"
          label="Motivo"
          variant="outlined"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-text-field
          v-model="searchQuery"
          label="Buscar..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @update:model-value="debounceSearch"
        />
      </v-col>
    </v-row>

    <!-- Tabela de Denúncias -->
    <v-card elevation="2">
      <v-data-table-server
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        :headers="headers"
        :items="reports"
        :items-length="totalReports"
        :loading="loading"
        :search="searchQuery"
        @update:options="handleTableUpdate"
      >
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
        
        <!-- Tipo de Conteúdo -->
        <template #item.content_type="{ item }">
          <div class="d-flex align-center">
            <v-icon 
              :icon="getContentTypeIcon(item.content_type)" 
              size="18" 
              class="mr-2"
            />
            {{ getContentTypeText(item.content_type) }}
          </div>
        </template>
        
        <!-- Conteúdo Reportado -->
        <template #item.content="{ item }">
          <div class="max-width-300">
            <p class="text-truncate font-weight-medium">{{ item.content_title }}</p>
            <p class="text-caption text-grey text-truncate">
              {{ item.content_excerpt }}
            </p>
          </div>
        </template>
        
        <!-- Usuário Reportado -->
        <template #item.reported_user="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-2">
              <v-img 
                v-if="item.reported_user.avatar"
                :src="item.reported_user.avatar"
                :alt="item.reported_user.username"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
            <div>
              <p class="text-body-2 font-weight-medium">{{ item.reported_user.username }}</p>
              <p class="text-caption text-grey">{{ item.reported_user.email }}</p>
            </div>
          </div>
        </template>
        
        <!-- Motivo -->
        <template #item.reason="{ item }">
          <v-chip
            variant="outlined"
            size="small"
            :color="getReasonColor(item.reason)"
          >
            {{ getReasonText(item.reason) }}
          </v-chip>
        </template>
        
        <!-- Data -->
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
              @click="viewReport(item)"
            />
            
            <v-btn
              v-if="item.status === 'pending'"
              icon="mdi-check"
              variant="text"
              size="small"
              color="success"
              @click="approveReport(item)"
            />
            
            <v-btn
              v-if="item.status === 'pending'"
              icon="mdi-close"
              variant="text"
              size="small"
              color="error"
              @click="rejectReport(item)"
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
            <v-icon size="64" color="grey-lighten-1">mdi-flag-outline</v-icon>
            <h3 class="text-h6 mt-4">Nenhuma denúncia encontrada</h3>
            <p class="text-body-2 text-grey mt-2">
              {{ searchQuery ? 'Tente ajustar os filtros' : 'Não há denúncias no momento' }}
            </p>
          </div>
        </template>
      </v-data-table-server>
    </v-card>

    <!-- Dialog de Detalhes da Denúncia -->
    <v-dialog v-model="reportDialog" max-width="800">
      <v-card v-if="selectedReport">
        <v-card-title>
          <v-icon class="mr-2">mdi-flag</v-icon>
          Detalhes da Denúncia #{{ selectedReport.id }}
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <!-- Informações da Denúncia -->
            <v-col cols="12" md="6">
              <h4 class="text-h6 mb-3">Informações da Denúncia</h4>
              
              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-calendar</v-icon>
                  </template>
                  <v-list-item-title>Data</v-list-item-title>
                  <v-list-item-subtitle>{{ formatFullDate(selectedReport.created_at) }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-account-alert</v-icon>
                  </template>
                  <v-list-item-title>Denunciado por</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedReport.reporter.username }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-tag</v-icon>
                  </template>
                  <v-list-item-title>Motivo</v-list-item-title>
                  <v-list-item-subtitle>{{ getReasonText(selectedReport.reason) }}</v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template #prepend>
                    <v-icon>mdi-information</v-icon>
                  </template>
                  <v-list-item-title>Status</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip
                      :color="getStatusColor(selectedReport.status)"
                      variant="tonal"
                      size="small"
                    >
                      {{ getStatusText(selectedReport.status) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            
            <!-- Conteúdo Reportado -->
            <v-col cols="12" md="6">
              <h4 class="text-h6 mb-3">Conteúdo Reportado</h4>
              
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="text-h6">
                  <v-icon class="mr-2">{{ getContentTypeIcon(selectedReport.content_type) }}</v-icon>
                  {{ selectedReport.content_title }}
                </v-card-title>
                
                <v-card-text>
                  <p class="text-body-2">{{ selectedReport.content_excerpt }}</p>
                  
                  <div class="mt-3">
                    <v-chip variant="outlined" size="small" class="mr-2">
                      {{ getContentTypeText(selectedReport.content_type) }}
                    </v-chip>
                    <v-chip variant="outlined" size="small">
                      Por: {{ selectedReport.reported_user.username }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <!-- Descrição da Denúncia -->
            <v-col cols="12">
              <h4 class="text-h6 mb-3">Descrição da Denúncia</h4>
              <v-textarea
                :model-value="selectedReport.description"
                variant="outlined"
                readonly
                rows="4"
                placeholder="Nenhuma descrição fornecida"
              />
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          
          <v-btn
            v-if="selectedReport.status === 'pending'"
            color="error"
            variant="outlined"
            @click="rejectReport(selectedReport)"
          >
            Rejeitar
          </v-btn>
          
          <v-btn
            v-if="selectedReport.status === 'pending'"
            color="success"
            @click="approveReport(selectedReport)"
          >
            Aprovar
          </v-btn>
          
          <v-btn @click="reportDialog = false">
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Estado local
const loading = ref(false)
const reportDialog = ref(false)
const selectedReport = ref(null)
const page = ref(1)
const itemsPerPage = ref(10)

// Filtros
const statusFilter = ref('all')
const typeFilter = ref('all')
const reasonFilter = ref('all')
const searchQuery = ref('')

// Mock data - substituir por dados reais
const stats = ref({
  total_reports: 34,
  pending_reports: 8,
  approved_reports: 18,
  rejected_reports: 8
})

const reports = ref([
  {
    id: 1,
    status: 'pending',
    content_type: 'article',
    content_title: 'Estratégias para apostas múltiplas',
    content_excerpt: 'Neste artigo vou compartilhar algumas estratégias que uso...',
    reported_user: {
      username: 'joao_apostador',
      email: 'joao@email.com',
      avatar: null
    },
    reporter: {
      username: 'usuario_monitor'
    },
    reason: 'spam',
    description: 'Este conteúdo parece ser spam promocional de sites de apostas.',
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    status: 'approved',
    content_type: 'comment',
    content_title: 'Comentário em: Análise do jogo Brasil vs Argentina',
    content_excerpt: 'Discordo completamente, vocês não sabem nada de futebol...',
    reported_user: {
      username: 'critico_feroz',
      email: 'critico@email.com',
      avatar: null
    },
    reporter: {
      username: 'moderador1'
    },
    reason: 'offensive',
    description: 'Linguagem ofensiva e ataques pessoais aos outros usuários.',
    created_at: '2024-01-14T15:45:00Z'
  }
])

// Computed
const totalReports = computed(() => reports.value.length)
const pendingReports = computed(() => stats.value.pending_reports)

// Options
const statusOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Pendente', value: 'pending' },
  { title: 'Aprovado', value: 'approved' },
  { title: 'Rejeitado', value: 'rejected' }
]

const typeOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Artigos', value: 'article' },
  { title: 'Comentários', value: 'comment' }
]

const reasonOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Spam', value: 'spam' },
  { title: 'Conteúdo Ofensivo', value: 'offensive' },
  { title: 'Informação Falsa', value: 'fake_news' },
  { title: 'Conteúdo Inapropriado', value: 'inappropriate' },
  { title: 'Outros', value: 'other' }
]

const headers = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: 'Status', key: 'status', width: '120px' },
  { title: 'Tipo', key: 'content_type', width: '120px' },
  { title: 'Conteúdo', key: 'content', width: '300px' },
  { title: 'Usuário', key: 'reported_user', width: '200px' },
  { title: 'Motivo', key: 'reason', width: '150px' },
  { title: 'Data', key: 'created_at', width: '150px' },
  { title: 'Ações', key: 'actions', width: '120px', sortable: false }
]

// Helper functions
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'error'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: 'Pendente',
    approved: 'Aprovado',
    rejected: 'Rejeitado'
  }
  return texts[status] || status
}

const getContentTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    article: 'mdi-file-document',
    comment: 'mdi-comment-text'
  }
  return icons[type] || 'mdi-file'
}

const getContentTypeText = (type: string) => {
  const texts: Record<string, string> = {
    article: 'Artigo',
    comment: 'Comentário'
  }
  return texts[type] || type
}

const getReasonColor = (reason: string) => {
  const colors: Record<string, string> = {
    spam: 'orange',
    offensive: 'red',
    fake_news: 'purple',
    inappropriate: 'pink',
    other: 'grey'
  }
  return colors[reason] || 'grey'
}

const getReasonText = (reason: string) => {
  const texts: Record<string, string> = {
    spam: 'Spam',
    offensive: 'Ofensivo',
    fake_news: 'Fake News',
    inappropriate: 'Inapropriado',
    other: 'Outros'
  }
  return texts[reason] || reason
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

const viewReport = (report: any) => {
  selectedReport.value = report
  reportDialog.value = true
}

const approveReport = async (report: any) => {
  try {
    // Implementar aprovação via API
    report.status = 'approved'
    reportDialog.value = false
  } catch (error) {
    console.error('Erro ao aprovar denúncia:', error)
  }
}

const rejectReport = async (report: any) => {
  try {
    // Implementar rejeição via API
    report.status = 'rejected'
    reportDialog.value = false
  } catch (error) {
    console.error('Erro ao rejeitar denúncia:', error)
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // Carregar dados reais via API
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simular carregamento
  } catch (error) {
    console.error('Erro ao carregar denúncias:', error)
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
