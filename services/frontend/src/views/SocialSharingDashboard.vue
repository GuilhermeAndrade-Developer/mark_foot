<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-share-variant</v-icon>
          Compartilhamento Social
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerencie plataformas sociais, templates e posts compartilhados
        </p>
      </v-col>
    </v-row>

    <!-- Demo Mode Alert -->
    <v-alert
      v-if="isDemoMode"
      type="info"
      variant="tonal"
      class="mb-6"
      prominent
    >
      <template #prepend>
        <v-icon>mdi-information</v-icon>
      </template>
      <v-alert-title>Modo Demonstração</v-alert-title>
      <p>
        Você está visualizando dados de demonstração. Para ver dados reais, 
        configure as integrações nas <router-link to="/social-networks/settings">Configurações de Redes Sociais</router-link>.
      </p>
    </v-alert>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card elevation="2" color="primary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-share</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.total_shares || 0 }}</div>
                <div class="text-subtitle-2">Total de Compartilhamentos</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="success" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-calendar-today</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.shares_today || 0 }}</div>
                <div class="text-subtitle-2">Compartilhamentos Hoje</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="info" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-heart</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.engagement_metrics?.total_likes || 0 }}</div>
                <div class="text-subtitle-2">Total de Curtidas</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="warning" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-eye</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.engagement_metrics?.total_views || 0 }}</div>
                <div class="text-subtitle-2">Total de Visualizações</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Row -->
    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-donut</v-icon>
            Compartilhamentos por Plataforma
          </v-card-title>
          <v-card-text>
            <DoughnutChart
              :data="platformChartData"
              :height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Tendência de Compartilhamentos
          </v-card-title>
          <v-card-text>
            <LineChart
              :data="trendChartData"
              :height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="primary"
                  block
                  size="large"
                  variant="outlined"
                  @click="$router.push('/social/sharing/platforms')"
                >
                  <v-icon start>mdi-web</v-icon>
                  Gerenciar Plataformas
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="success"
                  block
                  size="large"
                  variant="outlined"
                  @click="$router.push('/social/sharing/templates')"
                >
                  <v-icon start>mdi-file-document-multiple</v-icon>
                  Templates de Post
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="info"
                  block
                  size="large"
                  variant="outlined"
                  @click="$router.push('/social/sharing/shares')"
                >
                  <v-icon start>mdi-share-variant</v-icon>
                  Ver Compartilhamentos
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="secondary"
                  block
                  size="large"
                  variant="outlined"
                  @click="openCreateShareDialog"
                >
                  <v-icon start>mdi-plus</v-icon>
                  Novo Compartilhamento
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Shares & Platforms -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-clock</v-icon>
            Compartilhamentos Recentes
          </v-card-title>
          <v-card-text>
            <v-list v-if="recentShares.length">
              <v-list-item
                v-for="share in recentShares"
                :key="share.id"
              >
                <template #prepend>
                  <v-avatar
                    :color="getPlatformColor(share.platform.name)"
                    size="40"
                    class="mr-3"
                  >
                    <v-icon color="white">
                      {{ getPlatformIcon(share.platform.name) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ share.title }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ share.platform.display_name }} • {{ formatDateTime(share.created_at) }}
                </v-list-item-subtitle>

                <template #append>
                  <v-chip
                    :color="getStatusColor(share.status)"
                    size="small"
                  >
                    {{ getStatusText(share.status) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              Nenhum compartilhamento encontrado
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-web</v-icon>
            Plataformas Ativas
          </v-card-title>
          <v-card-text>
            <v-list v-if="platforms.length">
              <v-list-item
                v-for="platform in platforms"
                :key="platform.id"
              >
                <template #prepend>
                  <v-avatar
                    :color="getPlatformColor(platform.name)"
                    size="32"
                    class="mr-3"
                  >
                    <v-icon color="white" size="16">
                      {{ getPlatformIcon(platform.name) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ platform.display_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ platform.character_limit }} caracteres
                </v-list-item-subtitle>

                <template #append>
                  <v-chip
                    :color="platform.is_active ? 'success' : 'error'"
                    size="small"
                  >
                    {{ platform.is_active ? 'Ativa' : 'Inativa' }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              Nenhuma plataforma configurada
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create Share Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="800">
      <v-card>
        <v-card-title>
          <v-icon class="mr-3">mdi-plus</v-icon>
          Novo Compartilhamento
        </v-card-title>
        <v-card-text>
          <v-form v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newShare.platform"
                  :items="platforms"
                  item-title="display_name"
                  item-value="id"
                  label="Plataforma"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newShare.template"
                  :items="availableTemplates"
                  item-title="name"
                  item-value="id"
                  label="Template (opcional)"
                  clearable
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="newShare.title"
                  label="Título"
                  required
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="newShare.content"
                  label="Conteúdo"
                  rows="4"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newShare.hashtags"
                  label="Hashtags"
                  placeholder="#football #markfoot"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newShare.image_url"
                  label="URL da Imagem (opcional)"
                  type="url"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showCreateDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            :disabled="!formValid"
            :loading="creating"
            @click="createShare"
          >
            Criar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="align-center justify-center"
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      />
    </v-overlay>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { SocialSharingApiService } from '@/services/socialSharingApi'
import type { SocialPlatform, ShareTemplate, SocialShare, SocialSharingStats } from '@/services/socialSharingApi'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'
import LineChart from '@/components/charts/LineChart.vue'

// Reactive data
const loading = ref(false)
const creating = ref(false)
const formValid = ref(false)
const showCreateDialog = ref(false)

const stats = ref<SocialSharingStats>({
  total_shares: 0,
  shares_by_platform: {},
  shares_today: 0,
  shares_this_week: 0,
  shares_this_month: 0,
  top_shared_content: [],
  most_active_users: [],
  engagement_metrics: {
    total_likes: 0,
    total_shares: 0,
    total_comments: 0,
    total_views: 0
  }
})

const platforms = ref<SocialPlatform[]>([])
const templates = ref<ShareTemplate[]>([])
const recentShares = ref<SocialShare[]>([])

// Demo mode detection
const isDemoMode = ref(true)

const newShare = ref({
  platform: null as number | null,
  template: null as number | null,
  title: '',
  content: '',
  hashtags: '',
  image_url: ''
})

// Computed
const availableTemplates = computed(() => {
  if (!newShare.value.platform) return []
  return templates.value.filter(t => t.platform.id === newShare.value.platform)
})

const platformChartData = computed(() => {
  const data = stats.value.shares_by_platform || {}
  return {
    labels: Object.keys(data),
    datasets: [{
      data: Object.values(data),
      backgroundColor: [
        '#1DA1F2', // Twitter
        '#E4405F', // Instagram
        '#000000', // TikTok
        '#4267B2', // Facebook
        '#0A66C2'  // LinkedIn
      ]
    }]
  }
})

const trendChartData = computed(() => {
  // Simulated trend data - in real app this would come from API
  return {
    labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'],
    datasets: [{
      label: 'Compartilhamentos',
      data: [12, 19, 15, 25, 22, 30, 28],
      borderColor: '#1976d2',
      backgroundColor: 'rgba(25, 118, 210, 0.1)',
      fill: true
    }]
  }
})

// Methods
const loadData = async () => {
  try {
    loading.value = true
    
    try {
      const [statsData, platformsData, templatesData, sharesData] = await Promise.all([
        SocialSharingApiService.getSharingStats(),
        SocialSharingApiService.getPlatforms(),
        SocialSharingApiService.getTemplates(),
        SocialSharingApiService.getShares({ page: 1 })
      ])
      
      // Check if we have real data
      if (statsData.total_shares > 0 || platformsData.length > 0 || sharesData.results.length > 0) {
        isDemoMode.value = false
        stats.value = statsData
        platforms.value = platformsData
        templates.value = templatesData
        recentShares.value = sharesData.results.slice(0, 10)
      } else {
        loadDemoData()
      }
    } catch (error) {
      console.log('API não disponível, carregando dados de demonstração')
      loadDemoData()
    }
  } finally {
    loading.value = false
  }
}

const loadDemoData = () => {
  isDemoMode.value = true
  
  // Demo statistics
  stats.value = {
    total_shares: 1247,
    shares_by_platform: {
      'Twitter': 450,
      'Instagram': 380,
      'Facebook': 280,
      'TikTok': 137
    },
    shares_today: 23,
    shares_this_week: 156,
    shares_this_month: 892,
    top_shared_content: [],
    most_active_users: [],
    engagement_metrics: {
      total_likes: 15420,
      total_shares: 2340,
      total_comments: 1890,
      total_views: 45600
    }
  }
  
  // Demo platforms
  platforms.value = [
    {
      id: 1,
      name: 'twitter',
      display_name: 'Twitter',
      is_active: true,
      character_limit: 280,
      supports_images: true,
      supports_videos: true,
      supports_hashtags: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 2,
      name: 'instagram',
      display_name: 'Instagram',
      is_active: true,
      character_limit: 2200,
      supports_images: true,
      supports_videos: true,
      supports_hashtags: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ]
  
  // Demo templates
  templates.value = [
    {
      id: 1,
      name: 'Resultado do Jogo',
      template_type: 'match_result',
      platform: platforms.value[0],
      title_template: '🏆 Resultado: {home_team} vs {away_team}',
      content_template: 'Que jogo! {home_team} {home_score} x {away_score} {away_team}. {match_summary}',
      hashtags: '#futebol #resultado #markfoot',
      available_variables: ['home_team', 'away_team', 'home_score', 'away_score', 'match_summary'],
      is_active: true,
      auto_share: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ]
  
  // Demo recent shares
  recentShares.value = [
    {
      id: 1,
      platform: platforms.value[0],
      template: templates.value[0],
      title: '🏆 Resultado: Flamengo vs Palmeiras',
      content: 'Que jogo! Flamengo 2 x 1 Palmeiras. Vitória épica no Maracanã!',
      hashtags: '#futebol #resultado #markfoot #flamengo',
      image_url: '',
      video_url: '',
      match: 1,
      team: 1,
      comment: undefined,
      user: { id: 1, username: 'admin' },
      scheduled_at: undefined,
      published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      platform_post_id: 'tw_123456789',
      platform_url: 'https://twitter.com/markfoot/status/123456789',
      likes_count: 245,
      shares_count: 67,
      comments_count: 89,
      views_count: 3200,
      status: 'published' as const,
      error_message: undefined,
      retry_count: 0,
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      platform: platforms.value[1],
      template: undefined,
      title: '📊 Estatísticas da rodada',
      content: 'Confira as estatísticas completas da última rodada do Brasileirão! 📈⚽',
      hashtags: '#brasileirao #estatisticas #markfoot',
      image_url: 'https://example.com/stats.jpg',
      video_url: '',
      match: undefined,
      team: undefined,
      comment: undefined,
      user: { id: 1, username: 'admin' },
      scheduled_at: undefined,
      published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      platform_post_id: 'ig_987654321',
      platform_url: 'https://instagram.com/p/987654321',
      likes_count: 512,
      shares_count: 123,
      comments_count: 78,
      views_count: 5400,
      status: 'published' as const,
      error_message: undefined,
      retry_count: 0,
      created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
    }
  ]
}

const openCreateShareDialog = () => {
  newShare.value = {
    platform: null,
    template: null,
    title: '',
    content: '',
    hashtags: '',
    image_url: ''
  }
  showCreateDialog.value = true
}

const createShare = async () => {
  try {
    creating.value = true
    
    const shareData = {
      ...newShare.value,
      platform: newShare.value.platform!,
      template: newShare.value.template || undefined
    }
    
    await SocialSharingApiService.createShare(shareData)
    showCreateDialog.value = false
    
    // Reload data
    await loadData()
  } catch (error) {
    console.error('Erro ao criar compartilhamento:', error)
  } finally {
    creating.value = false
  }
}

const getPlatformIcon = (platformName: string) => {
  const icons = {
    twitter: 'mdi-twitter',
    instagram: 'mdi-instagram',
    tiktok: 'mdi-music-note',
    facebook: 'mdi-facebook',
    linkedin: 'mdi-linkedin'
  }
  return icons[platformName as keyof typeof icons] || 'mdi-web'
}

const getPlatformColor = (platformName: string) => {
  const colors = {
    twitter: '#1DA1F2',
    instagram: '#E4405F',
    tiktok: '#000000',
    facebook: '#4267B2',
    linkedin: '#0A66C2'
  }
  return colors[platformName as keyof typeof colors] || 'primary'
}

const getStatusColor = (status: string) => {
  const colors = {
    pending: 'warning',
    scheduled: 'info',
    published: 'success',
    failed: 'error',
    deleted: 'error'
  }
  return colors[status as keyof typeof colors] || 'secondary'
}

const getStatusText = (status: string) => {
  const texts = {
    pending: 'Pendente',
    scheduled: 'Agendado',
    published: 'Publicado',
    failed: 'Falhou',
    deleted: 'Deletado'
  }
  return texts[status as keyof typeof texts] || status
}

const formatDateTime = (dateString: string) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: ptBR })
  } catch {
    return 'Data inválida'
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}

.text-h4 {
  font-size: 2rem !important;
}
</style>
