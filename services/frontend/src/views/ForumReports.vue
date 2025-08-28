<template>
  <div class="forum-reports">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Relatórios do Fórum</h1>
        <p class="text-body-1 text-medium-emphasis">
          Análises detalhadas e estatísticas do fórum
        </p>
      </div>
      <v-btn
        color="primary"
        prepend-icon="mdi-download"
        @click="exportReport"
      >
        Exportar Relatório
      </v-btn>
    </div>

    <!-- Time Range Selector -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="3">
            <v-select
              v-model="timeRange"
              :items="timeRangeOptions"
              label="Período"
              density="compact"
              @update:model-value="loadData"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="dateFrom"
              label="Data Inicial"
              type="date"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="dateTo"
              label="Data Final"
              type="date"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-btn
              color="primary"
              block
              @click="loadData"
            >
              Atualizar
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Overview Stats -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="primary" class="mr-3">
              <v-icon>mdi-forum</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ overview.total_posts }}</div>
              <div class="text-body-2 text-medium-emphasis">Posts Totais</div>
              <div class="text-caption text-success">
                <v-icon size="12">mdi-trending-up</v-icon>
                +{{ overview.posts_growth }}% vs período anterior
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="success" class="mr-3">
              <v-icon>mdi-account-group</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ overview.active_users }}</div>
              <div class="text-body-2 text-medium-emphasis">Usuários Ativos</div>
              <div class="text-caption text-success">
                <v-icon size="12">mdi-trending-up</v-icon>
                +{{ overview.users_growth }}% vs período anterior
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="warning" class="mr-3">
              <v-icon>mdi-eye</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ overview.total_views }}</div>
              <div class="text-body-2 text-medium-emphasis">Visualizações</div>
              <div class="text-caption text-success">
                <v-icon size="12">mdi-trending-up</v-icon>
                +{{ overview.views_growth }}% vs período anterior
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="info" class="mr-3">
              <v-icon>mdi-message-reply</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ overview.engagement_rate }}%</div>
              <div class="text-body-2 text-medium-emphasis">Taxa de Engajamento</div>
              <div class="text-caption text-success">
                <v-icon size="12">mdi-trending-up</v-icon>
                +{{ overview.engagement_growth }}% vs período anterior
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Row -->
    <v-row class="mb-6">
      <!-- Activity Chart -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Atividade do Fórum
          </v-card-title>
          <v-card-text>
            <div id="activity-chart" style="height: 300px;">
              <div class="d-flex align-center justify-center h-100">
                <div class="text-center">
                  <v-icon size="48" color="primary">mdi-chart-line</v-icon>
                  <div class="text-h6 mt-2">Gráfico de Atividade</div>
                  <div class="text-body-2 text-medium-emphasis">
                    Posts e comentários ao longo do tempo
                  </div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Top Categories -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-donut</v-icon>
            Categorias Mais Ativas
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="(category, index) in topCategories"
                :key="category.id"
                class="px-0"
              >
                <template #prepend>
                  <v-avatar :color="getCategoryColor(index)" size="24" class="mr-3">
                    <span class="text-white text-caption">{{ index + 1 }}</span>
                  </v-avatar>
                </template>
                <v-list-item-title class="text-body-2">
                  {{ category.name }}
                </v-list-item-title>
                <template #append>
                  <div class="text-right">
                    <div class="text-body-2 font-weight-medium">{{ category.posts }}</div>
                    <div class="text-caption text-medium-emphasis">posts</div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Detailed Reports -->
    <v-row>
      <!-- User Activity -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-account-star</v-icon>
            Usuários Mais Ativos
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="userHeaders"
              :items="topUsers"
              hide-default-footer
              class="elevation-0"
            >
              <template #item.user="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="24" class="mr-2">
                    <v-icon size="16">mdi-account</v-icon>
                  </v-avatar>
                  <span class="text-body-2">{{ item.name }}</span>
                </div>
              </template>

              <template #item.posts="{ item }">
                <div class="text-center">
                  <div class="text-body-2 font-weight-medium">{{ item.posts }}</div>
                </div>
              </template>

              <template #item.likes="{ item }">
                <div class="text-center">
                  <div class="text-body-2 font-weight-medium">{{ item.likes }}</div>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Moderation Stats -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-shield-check</v-icon>
            Estatísticas de Moderação
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="6">
                <div class="text-center pa-3">
                  <div class="text-h4 font-weight-bold text-warning">{{ moderation.reports }}</div>
                  <div class="text-body-2 text-medium-emphasis">Denúncias</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center pa-3">
                  <div class="text-h4 font-weight-bold text-error">{{ moderation.deleted_posts }}</div>
                  <div class="text-body-2 text-medium-emphasis">Posts Removidos</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center pa-3">
                  <div class="text-h4 font-weight-bold text-info">{{ moderation.warnings }}</div>
                  <div class="text-body-2 text-medium-emphasis">Avisos Dados</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center pa-3">
                  <div class="text-h4 font-weight-bold text-error">{{ moderation.bans }}</div>
                  <div class="text-body-2 text-medium-emphasis">Banimentos</div>
                </div>
              </v-col>
            </v-row>
            
            <v-divider class="my-4" />
            
            <div class="text-body-2 text-medium-emphasis text-center">
              Tempo médio de resposta: {{ moderation.avg_response_time }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Content Performance -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-trophy</v-icon>
            Performance de Conteúdo
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="contentHeaders"
              :items="topContent"
              class="elevation-0"
            >
              <template #item.title="{ item }">
                <div>
                  <div class="text-body-2 font-weight-medium">{{ item.title }}</div>
                  <v-chip size="x-small" color="primary" variant="outlined" class="mt-1">
                    {{ item.category }}
                  </v-chip>
                </div>
              </template>

              <template #item.author="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="20" class="mr-2">
                    <v-icon size="12">mdi-account</v-icon>
                  </v-avatar>
                  <span class="text-body-2">{{ item.author }}</span>
                </div>
              </template>

              <template #item.engagement="{ item }">
                <div class="text-center">
                  <v-chip
                    :color="getEngagementColor(item.engagement)"
                    size="small"
                    variant="flat"
                  >
                    {{ item.engagement }}%
                  </v-chip>
                </div>
              </template>

              <template #item.created_at="{ item }">
                <div class="text-body-2">{{ formatDate(item.created_at) }}</div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// State
const loading = ref(false)
const timeRange = ref('7d')
const dateFrom = ref('')
const dateTo = ref('')

// Time range options
const timeRangeOptions = [
  { title: 'Últimos 7 dias', value: '7d' },
  { title: 'Últimos 30 dias', value: '30d' },
  { title: 'Últimos 3 meses', value: '3m' },
  { title: 'Último ano', value: '1y' },
  { title: 'Personalizado', value: 'custom' }
]

// Mock data
const overview = ref({
  total_posts: 1247,
  posts_growth: 15.2,
  active_users: 89,
  users_growth: 8.7,
  total_views: 45623,
  views_growth: 23.1,
  engagement_rate: 67,
  engagement_growth: 12.3
})

const topCategories = ref([
  { id: 1, name: 'Bayern München', posts: 234 },
  { id: 2, name: 'Champions League', posts: 189 },
  { id: 3, name: 'Bundesliga', posts: 156 },
  { id: 4, name: 'Real Madrid', posts: 142 },
  { id: 5, name: 'Discussões Gerais', posts: 98 }
])

const topUsers = ref([
  { id: 1, name: 'João Silva', posts: 45, likes: 234 },
  { id: 2, name: 'Maria Santos', posts: 38, likes: 189 },
  { id: 3, name: 'Pedro Costa', posts: 32, likes: 156 },
  { id: 4, name: 'Ana Oliveira', posts: 28, likes: 142 },
  { id: 5, name: 'Carlos Lima', posts: 24, likes: 98 }
])

const moderation = ref({
  reports: 23,
  deleted_posts: 8,
  warnings: 15,
  bans: 3,
  avg_response_time: '2h 15m'
})

const topContent = ref([
  {
    id: 1,
    title: 'Análise: Bayern München vs Real Madrid',
    category: 'Champions League',
    author: 'João Silva',
    views: 1234,
    likes: 89,
    comments: 45,
    engagement: 78,
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 2,
    title: 'Previsões para a próxima rodada',
    category: 'Bundesliga',
    author: 'Maria Santos',
    views: 987,
    likes: 67,
    comments: 32,
    engagement: 65,
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
  }
])

// Table headers
const userHeaders = [
  { title: 'Usuário', key: 'user', sortable: false },
  { title: 'Posts', key: 'posts', align: 'center' },
  { title: 'Likes', key: 'likes', align: 'center' }
]

const contentHeaders = [
  { title: 'Título', key: 'title', sortable: false },
  { title: 'Autor', key: 'author', sortable: false },
  { title: 'Visualizações', key: 'views', align: 'center' },
  { title: 'Likes', key: 'likes', align: 'center' },
  { title: 'Comentários', key: 'comments', align: 'center' },
  { title: 'Engajamento', key: 'engagement', align: 'center' },
  { title: 'Data', key: 'created_at', sortable: false }
]

// Helper functions
function getCategoryColor(index: number) {
  const colors = ['primary', 'success', 'warning', 'info', 'error']
  return colors[index % colors.length]
}

function getEngagementColor(engagement: number) {
  if (engagement >= 70) return 'success'
  if (engagement >= 50) return 'warning'
  return 'error'
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('pt-BR')
}

function loadData() {
  loading.value = true
  console.log('Carregando dados para período:', timeRange.value)
  // Simulate API call
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

function exportReport() {
  console.log('Exportando relatório...')
  // TODO: Implement export functionality
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.forum-reports {
  padding: 24px;
}
</style>
