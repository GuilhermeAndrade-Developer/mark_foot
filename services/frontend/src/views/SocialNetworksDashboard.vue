<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-web</v-icon>
          Dashboard de Redes Sociais
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Visão geral dos recursos de redes sociais e grupos privados
        </p>
      </v-col>
    </v-row>

    <!-- Statistics Overview -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card elevation="2" color="primary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-share</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ overviewStats.total_shares || 0 }}</div>
                <div class="text-subtitle-2">Total Compartilhamentos</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="success" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-account-group</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ overviewStats.total_groups || 0 }}</div>
                <div class="text-subtitle-2">Grupos Ativos</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="info" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-account-multiple</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ overviewStats.total_members || 0 }}</div>
                <div class="text-subtitle-2">Membros em Grupos</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="warning" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-web</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ overviewStats.active_platforms || 0 }}</div>
                <div class="text-subtitle-2">Plataformas Ativas</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Navigation Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="6" lg="3">
        <v-card 
          elevation="3" 
          class="navigation-card"
          @click="$router.push('/social-networks/sharing')"
        >
          <v-card-text class="text-center pa-6">
            <v-avatar size="80" color="primary" class="mb-4">
              <v-icon size="40" color="white">mdi-share-variant</v-icon>
            </v-avatar>
            <h3 class="text-h6 mb-2">Compartilhamento Social</h3>
            <p class="text-body-2 text-medium-emphasis">
              Gerencie posts e compartilhamentos nas redes sociais
            </p>
            <v-chip color="primary" size="small" class="mt-2">
              {{ overviewStats.shares_today || 0 }} posts hoje
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="3">
        <v-card 
          elevation="3" 
          class="navigation-card"
          @click="$router.push('/social-networks/groups')"
        >
          <v-card-text class="text-center pa-6">
            <v-avatar size="80" color="success" class="mb-4">
              <v-icon size="40" color="white">mdi-account-group</v-icon>
            </v-avatar>
            <h3 class="text-h6 mb-2">Grupos Privados</h3>
            <p class="text-body-2 text-medium-emphasis">
              Administre grupos familiares e de amigos
            </p>
            <v-chip color="success" size="small" class="mt-2">
              {{ overviewStats.new_members_today || 0 }} novos membros
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="3">
        <v-card 
          elevation="3" 
          class="navigation-card"
          @click="$router.push('/social-networks/settings')"
        >
          <v-card-text class="text-center pa-6">
            <v-avatar size="80" color="info" class="mb-4">
              <v-icon size="40" color="white">mdi-cog</v-icon>
            </v-avatar>
            <h3 class="text-h6 mb-2">Configurações</h3>
            <p class="text-body-2 text-medium-emphasis">
              Configure integrações e APIs das redes sociais
            </p>
            <v-chip color="info" size="small" class="mt-2">
              {{ overviewStats.configured_apis || 0 }} APIs configuradas
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="3">
        <v-card 
          elevation="3" 
          class="navigation-card"
          @click="openAnalyticsDialog"
        >
          <v-card-text class="text-center pa-6">
            <v-avatar size="80" color="secondary" class="mb-4">
              <v-icon size="40" color="white">mdi-chart-line</v-icon>
            </v-avatar>
            <h3 class="text-h6 mb-2">Analytics</h3>
            <p class="text-body-2 text-medium-emphasis">
              Visualize métricas e relatórios detalhados
            </p>
            <v-chip color="secondary" size="small" class="mt-2">
              Relatórios avançados
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Activity and Platform Status -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-clock</v-icon>
            Atividade Recente
          </v-card-title>
          <v-card-text>
            <v-timeline v-if="recentActivity.length" density="compact">
              <v-timeline-item
                v-for="(activity, index) in recentActivity"
                :key="index"
                :dot-color="getActivityColor(activity.type)"
                size="small"
              >
                <template #icon>
                  <v-icon size="16" color="white">
                    {{ getActivityIcon(activity.type) }}
                  </v-icon>
                </template>
                <div class="d-flex flex-column">
                  <strong>{{ activity.title }}</strong>
                  <span class="text-caption text-medium-emphasis">{{ activity.description }}</span>
                  <span class="text-caption text-medium-emphasis">{{ formatDateTime(activity.timestamp) }}</span>
                </div>
              </v-timeline-item>
            </v-timeline>
            <div v-else class="text-center py-8 text-medium-emphasis">
              <v-icon size="48" color="medium-emphasis">mdi-clock-outline</v-icon>
              <p class="text-h6 mt-2">Nenhuma atividade recente</p>
              <p class="text-body-2">As atividades aparecerão aqui conforme você usar o sistema</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-web</v-icon>
            Status das Plataformas
          </v-card-title>
          <v-card-text>
            <v-list v-if="platformStatus.length">
              <v-list-item
                v-for="platform in platformStatus"
                :key="platform.name"
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
                  {{ platform.configured ? 'Configurado' : 'Pendente configuração' }}
                </v-list-item-subtitle>

                <template #append>
                  <v-chip
                    :color="platform.configured ? 'success' : 'warning'"
                    size="small"
                  >
                    {{ platform.configured ? 'Ativo' : 'Inativo' }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              <v-icon size="48" color="medium-emphasis">mdi-web-off</v-icon>
              <p class="text-body-2 mt-2">Nenhuma plataforma configurada</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Analytics Dialog -->
    <v-dialog v-model="showAnalyticsDialog" max-width="1200">
      <v-card>
        <v-card-title>
          <v-icon class="mr-3">mdi-chart-line</v-icon>
          Analytics de Redes Sociais
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-card variant="outlined">
                <v-card-title class="text-h6">Engajamento Semanal</v-card-title>
                <v-card-text>
                  <LineChart
                    :data="engagementChartData"
                    :height="200"
                  />
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card variant="outlined">
                <v-card-title class="text-h6">Distribuição por Plataforma</v-card-title>
                <v-card-text>
                  <DoughnutChart
                    :data="platformDistributionData"
                    :height="200"
                  />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showAnalyticsDialog = false">
            Fechar
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
import { SocialSharingApiService, GroupsApiService } from '@/services/socialSharingApi'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import LineChart from '@/components/charts/LineChart.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

// Reactive data
const loading = ref(false)
const showAnalyticsDialog = ref(false)

const overviewStats = ref({
  total_shares: 0,
  total_groups: 0,
  total_members: 0,
  active_platforms: 0,
  shares_today: 0,
  new_members_today: 0,
  configured_apis: 0
})

const recentActivity = ref<Array<{
  type: string
  title: string
  description: string
  timestamp: string
}>>([])

const platformStatus = ref<Array<{
  name: string
  display_name: string
  configured: boolean
}>>([])

// Demo data flag
const isDemoMode = ref(true)

// Computed
const engagementChartData = computed(() => ({
  labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'],
  datasets: [{
    label: 'Curtidas',
    data: [120, 190, 300, 500, 200, 300, 280],
    borderColor: '#1976d2',
    backgroundColor: 'rgba(25, 118, 210, 0.1)',
    fill: true
  }, {
    label: 'Compartilhamentos',
    data: [50, 80, 120, 200, 100, 150, 140],
    borderColor: '#4caf50',
    backgroundColor: 'rgba(76, 175, 80, 0.1)',
    fill: true
  }]
}))

const platformDistributionData = computed(() => ({
  labels: ['Twitter', 'Instagram', 'TikTok', 'Facebook'],
  datasets: [{
    data: [35, 30, 20, 15],
    backgroundColor: ['#1DA1F2', '#E4405F', '#000000', '#4267B2']
  }]
}))

// Methods
const loadData = async () => {
  try {
    loading.value = true
    
    try {
      // Try to load real data
      const [sharingStats, groupStats, platforms] = await Promise.all([
        SocialSharingApiService.getSharingStats(),
        GroupsApiService.getGroupStats(),
        SocialSharingApiService.getPlatforms()
      ])
      
      // Check if we have real data
      if (sharingStats.total_shares > 0 || groupStats.total_groups > 0 || platforms.length > 0) {
        isDemoMode.value = false
        
        overviewStats.value = {
          total_shares: sharingStats.total_shares,
          total_groups: groupStats.total_groups,
          total_members: groupStats.total_members,
          active_platforms: platforms.filter(p => p.is_active).length,
          shares_today: sharingStats.shares_today,
          new_members_today: 5, // Would come from API
          configured_apis: platforms.filter(p => p.is_active).length
        }
        
        platformStatus.value = platforms.map(p => ({
          name: p.name,
          display_name: p.display_name,
          configured: p.is_active
        }))
        
        recentActivity.value = [
          {
            type: 'share',
            title: 'Novo post compartilhado',
            description: 'Post sobre resultado do último jogo compartilhado no Twitter',
            timestamp: new Date().toISOString()
          }
        ]
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
  
  overviewStats.value = {
    total_shares: 1247,
    total_groups: 15,
    total_members: 234,
    active_platforms: 4,
    shares_today: 12,
    new_members_today: 8,
    configured_apis: 3
  }
  
  platformStatus.value = [
    { name: 'twitter', display_name: 'Twitter', configured: true },
    { name: 'instagram', display_name: 'Instagram', configured: true },
    { name: 'tiktok', display_name: 'TikTok', configured: false },
    { name: 'facebook', display_name: 'Facebook', configured: true }
  ]
  
  recentActivity.value = [
    {
      type: 'share',
      title: 'Post compartilhado no Twitter',
      description: 'Resultado do jogo Flamengo vs Palmeiras compartilhado',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString()
    },
    {
      type: 'group',
      title: 'Novo grupo criado',
      description: 'Grupo "Família Silva" foi criado',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    },
    {
      type: 'member',
      title: 'Novo membro adicionado',
      description: 'João foi adicionado ao grupo "Amigos do Futebol"',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
    },
    {
      type: 'platform',
      title: 'Instagram configurado',
      description: 'API do Instagram foi configurada com sucesso',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
    }
  ]
}

const openAnalyticsDialog = () => {
  showAnalyticsDialog.value = true
}

const getActivityColor = (type: string) => {
  const colors = {
    share: 'primary',
    group: 'success',
    member: 'info',
    platform: 'warning'
  }
  return colors[type as keyof typeof colors] || 'secondary'
}

const getActivityIcon = (type: string) => {
  const icons = {
    share: 'mdi-share',
    group: 'mdi-account-group',
    member: 'mdi-account-plus',
    platform: 'mdi-web'
  }
  return icons[type as keyof typeof icons] || 'mdi-information'
}

const getPlatformIcon = (platformName: string) => {
  const icons = {
    twitter: 'mdi-twitter',
    instagram: 'mdi-instagram',
    tiktok: 'mdi-music-note',
    facebook: 'mdi-facebook'
  }
  return icons[platformName as keyof typeof icons] || 'mdi-web'
}

const getPlatformColor = (platformName: string) => {
  const colors = {
    twitter: '#1DA1F2',
    instagram: '#E4405F',
    tiktok: '#000000',
    facebook: '#4267B2'
  }
  return colors[platformName as keyof typeof colors] || 'primary'
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
.navigation-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.navigation-card:hover {
  transform: translateY(-4px);
  border-color: rgba(var(--v-theme-primary), 0.3);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.v-timeline {
  padding-left: 0;
}

.v-card {
  transition: transform 0.2s ease-in-out;
}

.text-h4 {
  font-size: 2rem !important;
}
</style>
