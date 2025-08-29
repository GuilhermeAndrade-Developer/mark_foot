<template>
  <v-container fluid>
    <!-- Header da página -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold">Gestão de Conteúdo</h1>
            <p class="text-body-1 text-medium-emphasis mt-1">
              Dashboard administrativo para gerenciamento de artigos e conteúdo gerado por usuários
            </p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="openCreateArticle"
          >
            Novo Artigo
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-if="contentStore.loadingStats" class="justify-center">
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        />
        <p class="mt-4">Carregando estatísticas...</p>
      </v-col>
    </v-row>

    <!-- Cards de Estatísticas -->
    <v-row v-else class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="primary" dark>
          <div class="d-flex align-center">
            <v-icon size="40" class="mr-3">mdi-file-document</v-icon>
            <div>
              <h3 class="text-h4 font-weight-bold">{{ stats?.total_articles || 0 }}</h3>
              <p class="text-body-2 mb-0">Total de Artigos</p>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="success" dark>
          <div class="d-flex align-center">
            <v-icon size="40" class="mr-3">mdi-check-circle</v-icon>
            <div>
              <h3 class="text-h4 font-weight-bold">{{ stats?.published_articles || 0 }}</h3>
              <p class="text-body-2 mb-0">Publicados</p>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="warning" dark>
          <div class="d-flex align-center">
            <v-icon size="40" class="mr-3">mdi-clock-outline</v-icon>
            <div>
              <h3 class="text-h4 font-weight-bold">{{ stats?.pending_articles || 0 }}</h3>
              <p class="text-body-2 mb-0">Aguardando</p>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4" color="info" dark>
          <div class="d-flex align-center">
            <v-icon size="40" class="mr-3">mdi-comment-multiple</v-icon>
            <div>
              <h3 class="text-h4 font-weight-bold">{{ stats?.total_comments || 0 }}</h3>
              <p class="text-body-2 mb-0">Comentários</p>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Gráficos e Analytics -->
    <v-row class="mb-6">
      <!-- Artigos por Categoria -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-donut</v-icon>
            Artigos por Categoria
          </v-card-title>
          <v-card-text>
            <DoughnutChart
              v-if="categoryChartData"
              :data="categoryChartData"
              :options="categoryChartOptions"
              style="height: 300px;"
            />
            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey-lighten-1">mdi-chart-donut</v-icon>
              <p class="mt-2 text-grey">Nenhum dado disponível</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Métricas de Engajamento -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Métricas de Engajamento
          </v-card-title>
          <v-card-text>
            <div class="text-center">
              <v-progress-circular
                :value="stats?.engagement_rate || 0"
                :size="120"
                :width="12"
                color="primary"
                class="ma-4"
              >
                <span class="text-h5 font-weight-bold">{{ Math.round(stats?.engagement_rate || 0) }}%</span>
              </v-progress-circular>
              <p class="text-subtitle-1 mt-2">Taxa de Engajamento</p>
            </div>
            
            <v-divider class="my-4" />
            
            <div class="d-flex justify-space-around">
              <div class="text-center">
                <p class="text-h6 font-weight-bold">{{ stats?.total_votes || 0 }}</p>
                <p class="text-caption">Total de Votos</p>
              </div>
              <div class="text-center">
                <p class="text-h6 font-weight-bold">{{ stats?.average_read_time || 0 }}min</p>
                <p class="text-caption">Tempo Médio de Leitura</p>
              </div>
              <div class="text-center">
                <p class="text-h6 font-weight-bold">{{ stats?.recent_activity || 0 }}</p>
                <p class="text-caption">Atividade Recente</p>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Artigos Populares -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-trending-up</v-icon>
            Artigos Mais Populares
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="popularArticlesHeaders"
              :items="stats?.popular_articles || []"
              :items-per-page="5"
              class="elevation-0"
              no-data-text="Nenhum artigo encontrado"
            >
              <template #item.title="{ item }">
                <div class="d-flex align-center">
                  <v-icon class="mr-2" size="20">mdi-file-document</v-icon>
                  <span class="font-weight-medium">{{ item.title }}</span>
                </div>
              </template>
              
              <template #item.views="{ item }">
                <v-chip
                  color="primary"
                  variant="tonal"
                  size="small"
                >
                  <v-icon start>mdi-eye</v-icon>
                  {{ formatNumber(item.views) }}
                </v-chip>
              </template>
              
              <template #item.likes="{ item }">
                <v-chip
                  color="success"
                  variant="tonal"
                  size="small"
                >
                  <v-icon start>mdi-thumb-up</v-icon>
                  {{ formatNumber(item.likes) }}
                </v-chip>
              </template>
              
              <template #item.author__username="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="24" class="mr-2">
                    <v-icon>mdi-account</v-icon>
                  </v-avatar>
                  {{ item.author__username }}
                </div>
              </template>
              
              <template #item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewArticle(item.id)"
                />
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="editArticle(item.id)"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions -->
    <v-row class="mt-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          <v-card-text>
            <div class="d-flex flex-wrap ga-3">
              <v-btn
                color="primary"
                prepend-icon="mdi-plus"
                @click="openCreateArticle"
              >
                Novo Artigo
              </v-btn>
              
              <v-btn
                color="secondary"
                prepend-icon="mdi-folder-plus"
                @click="openCreateCategory"
              >
                Nova Categoria
              </v-btn>
              
              <v-btn
                prepend-icon="mdi-table"
                @click="$router.push('/content/articles')"
              >
                Gerenciar Artigos
              </v-btn>
              
              <v-btn
                prepend-icon="mdi-folder-open"
                @click="$router.push('/content/categories')"
              >
                Gerenciar Categorias
              </v-btn>
              
              <v-btn
                prepend-icon="mdi-chart-bar"
                @click="$router.push('/content/reports')"
              >
                Relatórios Detalhados
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useContentStore } from '@/stores/content'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'
import type { ContentStats } from '@/types/content'

const router = useRouter()
const contentStore = useContentStore()

// Computed
const stats = computed(() => contentStore.stats)

// Headers da tabela de artigos populares
const popularArticlesHeaders = ref([
  { title: 'Artigo', key: 'title', sortable: false },
  { title: 'Visualizações', key: 'views', align: 'center' as const },
  { title: 'Curtidas', key: 'likes', align: 'center' as const },
  { title: 'Autor', key: 'author__username' },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' as const }
])

// Chart data para categorias
const categoryChartData = computed(() => {
  if (!stats.value?.articles_by_category) return null
  
  return {
    labels: stats.value.articles_by_category.map(cat => cat.category__name),
    datasets: [{
      data: stats.value.articles_by_category.map(cat => cat.count),
      backgroundColor: [
        '#1976D2', // Primary
        '#388E3C', // Success
        '#F57C00', // Warning
        '#7B1FA2', // Purple
        '#D32F2F', // Error
        '#0097A7'  // Cyan
      ],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  }
})

const categoryChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        padding: 20,
        usePointStyle: true
      }
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          return `${context.label}: ${context.parsed} artigos`
        }
      }
    }
  }
})

// Methods
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const openCreateArticle = () => {
  router.push('/content/articles?action=create')
}

const openCreateCategory = () => {
  router.push('/content/categories?action=create')
}

const viewArticle = (id: number) => {
  router.push(`/content/articles/${id}`)
}

const editArticle = (id: number) => {
  router.push(`/content/articles/${id}/edit`)
}

// Lifecycle
onMounted(async () => {
  try {
    await contentStore.fetchStats()
  } catch (error) {
    console.error('Erro ao carregar dados do dashboard:', error)
  }
})
</script>

<style scoped>
.v-card {
  height: 100%;
}

.v-progress-circular {
  margin: 0 auto;
}
</style>
