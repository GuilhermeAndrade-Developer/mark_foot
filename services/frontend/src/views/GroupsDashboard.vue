<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-account-group</v-icon>
          Grupos Privados
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerencie grupos privados, membros e atividades
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
              <v-icon size="48" class="mr-4">mdi-account-group</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.total_groups || 0 }}</div>
                <div class="text-subtitle-2">Total de Grupos</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="success" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-account-multiple</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.total_members || 0 }}</div>
                <div class="text-subtitle-2">Total de Membros</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="info" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-post</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.total_posts || 0 }}</div>
                <div class="text-subtitle-2">Total de Posts</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="warning" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-email</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ pendingInvitations || 0 }}</div>
                <div class="text-subtitle-2">Convites Pendentes</div>
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
            Grupos por Tipo
          </v-card-title>
          <v-card-text>
            <DoughnutChart
              :data="groupTypeChartData"
              :height="300"
            />
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-chart-pie</v-icon>
            Grupos por Privacidade
          </v-card-title>
          <v-card-text>
            <DoughnutChart
              :data="privacyChartData"
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
                  @click="openCreateGroupDialog"
                >
                  <v-icon start>mdi-plus</v-icon>
                  Criar Grupo
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="success"
                  block
                  size="large"
                  variant="outlined"
                  @click="$router.push('/social/groups/manage')"
                >
                  <v-icon start>mdi-cog</v-icon>
                  Gerenciar Grupos
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="info"
                  block
                  size="large"
                  variant="outlined"
                  @click="$router.push('/social/groups/members')"
                >
                  <v-icon start>mdi-account-multiple</v-icon>
                  Gerenciar Membros
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="secondary"
                  block
                  size="large"
                  variant="outlined"
                  @click="$router.push('/social/groups/invitations')"
                >
                  <v-icon start>mdi-email-multiple</v-icon>
                  Convites
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Groups Overview & Recent Activity -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-star</v-icon>
            Grupos Mais Ativos
          </v-card-title>
          <v-card-text>
            <v-list v-if="stats.most_active_groups && stats.most_active_groups.length">
              <v-list-item
                v-for="(group, index) in stats.most_active_groups"
                :key="group.id || index"
              >
                <template #prepend>
                  <v-avatar
                    :color="getGroupTypeColor(group.group_type)"
                    size="40"
                    class="mr-3"
                  >
                    <v-icon color="white">
                      {{ getGroupTypeIcon(group.group_type) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ group.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ group.member_count }} membros • {{ group.recent_posts || 0 }} posts recentes
                </v-list-item-subtitle>

                <template #append>
                  <v-chip
                    color="primary"
                    size="small"
                  >
                    #{{ index + 1 }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              Nenhum grupo encontrado
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-clock</v-icon>
            Atividade Recente
          </v-card-title>
          <v-card-text>
            <v-list v-if="recentGroups.length">
              <v-list-item
                v-for="group in recentGroups"
                :key="group.id"
              >
                <template #prepend>
                  <v-avatar
                    :color="getGroupTypeColor(group.group_type)"
                    size="32"
                    class="mr-3"
                  >
                    <v-icon color="white" size="16">
                      {{ getGroupTypeIcon(group.group_type) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ group.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ getGroupTypeLabel(group.group_type) }} • {{ formatDateTime(group.created_at) }}
                </v-list-item-subtitle>

                <template #append>
                  <v-chip
                    :color="getPrivacyColor(group.privacy_level)"
                    size="small"
                  >
                    {{ getPrivacyLabel(group.privacy_level) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              Nenhuma atividade recente
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create Group Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="800">
      <v-card>
        <v-card-title>
          <v-icon class="mr-3">mdi-plus</v-icon>
          Criar Novo Grupo
        </v-card-title>
        <v-card-text>
          <v-form v-model="formValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="newGroup.name"
                  label="Nome do Grupo"
                  required
                  :rules="[v => !!v || 'Nome é obrigatório']"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="newGroup.description"
                  label="Descrição"
                  rows="3"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newGroup.group_type"
                  :items="groupTypes"
                  label="Tipo do Grupo"
                  required
                  :rules="[v => !!v || 'Tipo é obrigatório']"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newGroup.privacy_level"
                  :items="privacyLevels"
                  label="Nível de Privacidade"
                  required
                  :rules="[v => !!v || 'Privacidade é obrigatória']"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="newGroup.max_members"
                  label="Máximo de Membros"
                  type="number"
                  min="1"
                  max="10000"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="newGroup.allow_member_invites"
                  label="Permitir convites de membros"
                  color="primary"
                />
              </v-col>
              <v-col cols="12">
                <v-switch
                  v-model="newGroup.require_admin_approval"
                  label="Requer aprovação do admin"
                  color="primary"
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
            @click="createGroup"
          >
            Criar Grupo
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
import { GroupsApiService } from '@/services/socialSharingApi'
import type { PrivateGroup, GroupStats } from '@/services/socialSharingApi'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

// Reactive data
const loading = ref(false)
const creating = ref(false)
const formValid = ref(false)
const showCreateDialog = ref(false)

const stats = ref<GroupStats>({
  total_groups: 0,
  total_members: 0,
  total_posts: 0,
  groups_by_type: {},
  groups_by_privacy: {},
  most_active_groups: [],
  recent_activity: []
})

const recentGroups = ref<PrivateGroup[]>([])
const pendingInvitations = ref(0)

// Demo mode detection
const isDemoMode = ref(true)

const newGroup = ref({
  name: '',
  description: '',
  group_type: 'custom',
  privacy_level: 'private',
  max_members: 50,
  allow_member_invites: true,
  require_admin_approval: false
})

// Form options
const groupTypes = [
  { title: 'Família', value: 'family' },
  { title: 'Amigos', value: 'friends' },
  { title: 'Torcedores', value: 'team_fans' },
  { title: 'Competição', value: 'competition' },
  { title: 'Personalizado', value: 'custom' }
]

const privacyLevels = [
  { title: 'Privado - Apenas por convite', value: 'private' },
  { title: 'Restrito - Solicitação para entrar', value: 'restricted' },
  { title: 'Público - Qualquer um pode entrar', value: 'public' }
]

// Computed
const groupTypeChartData = computed(() => {
  const data = stats.value.groups_by_type || {}
  return {
    labels: Object.keys(data).map(key => getGroupTypeLabel(key)),
    datasets: [{
      data: Object.values(data),
      backgroundColor: [
        '#FF6B6B',
        '#4ECDC4',
        '#45B7D1',
        '#96CEB4',
        '#FFEAA7'
      ]
    }]
  }
})

const privacyChartData = computed(() => {
  const data = stats.value.groups_by_privacy || {}
  return {
    labels: Object.keys(data).map(key => getPrivacyLabel(key)),
    datasets: [{
      data: Object.values(data),
      backgroundColor: [
        '#6C5CE7',
        '#FD79A8',
        '#00B894'
      ]
    }]
  }
})

// Methods
const loadData = async () => {
  try {
    loading.value = true
    
    try {
      const [statsData, groupsData] = await Promise.all([
        GroupsApiService.getGroupStats(),
        GroupsApiService.getGroups({ page: 1 })
      ])
      
      // Check if we have real data
      if (statsData.total_groups > 0 || groupsData.results.length > 0) {
        isDemoMode.value = false
        stats.value = statsData
        recentGroups.value = groupsData.results.slice(0, 8)
        pendingInvitations.value = 5 // Would come from real API
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
    total_groups: 15,
    total_members: 234,
    total_posts: 1456,
    groups_by_type: {
      'family': 4,
      'friends': 6,
      'team_fans': 3,
      'competition': 1,
      'custom': 1
    },
    groups_by_privacy: {
      'private': 8,
      'restricted': 5,
      'public': 2
    },
    most_active_groups: [
      {
        id: 1,
        name: 'Família Silva',
        group_type: 'family',
        member_count: 8,
        recent_posts: 23
      },
      {
        id: 2,
        name: 'Amigos do Futebol',
        group_type: 'friends',
        member_count: 15,
        recent_posts: 19
      },
      {
        id: 3,
        name: 'Torcida Flamengo RJ',
        group_type: 'team_fans',
        member_count: 45,
        recent_posts: 67
      }
    ],
    recent_activity: []
  }
  
  // Demo recent groups
  recentGroups.value = [
    {
      id: 1,
      name: 'Família Silva',
      description: 'Grupo da família para acompanhar os jogos juntos',
      group_type: 'family',
      privacy_level: 'private',
      max_members: 20,
      allow_member_invites: true,
      require_admin_approval: false,
      favorite_team: 'Flamengo',
      favorite_competition: 'Brasileirão',
      cover_image: undefined,
      avatar_image: undefined,
      member_count: 8,
      post_count: 45,
      is_active: true,
      is_featured: false,
      user_membership: {
        status: 'active',
        role: 'owner',
        joined_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
      },
      can_join: false,
      created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      name: 'Amigos do Futebol',
      description: 'Galera que se reúne para assistir os jogos',
      group_type: 'friends',
      privacy_level: 'restricted',
      max_members: 50,
      allow_member_invites: true,
      require_admin_approval: true,
      favorite_team: undefined,
      favorite_competition: undefined,
      cover_image: undefined,
      avatar_image: undefined,
      member_count: 15,
      post_count: 89,
      is_active: true,
      is_featured: true,
      user_membership: {
        status: 'active',
        role: 'admin',
        joined_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString()
      },
      can_join: false,
      created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      name: 'Torcida Flamengo RJ',
      description: 'Torcedores do Mengão no Rio de Janeiro',
      group_type: 'team_fans',
      privacy_level: 'public',
      max_members: 100,
      allow_member_invites: true,
      require_admin_approval: false,
      favorite_team: 'Flamengo',
      favorite_competition: 'Copa Libertadores',
      cover_image: undefined,
      avatar_image: undefined,
      member_count: 45,
      post_count: 234,
      is_active: true,
      is_featured: true,
      user_membership: {
        status: 'active',
        role: 'member',
        joined_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
      },
      can_join: true,
      created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
    }
  ]
  
  pendingInvitations.value = 7
}

const openCreateGroupDialog = () => {
  newGroup.value = {
    name: '',
    description: '',
    group_type: 'custom',
    privacy_level: 'private',
    max_members: 50,
    allow_member_invites: true,
    require_admin_approval: false
  }
  showCreateDialog.value = true
}

const createGroup = async () => {
  try {
    creating.value = true
    
    await GroupsApiService.createGroup(newGroup.value)
    showCreateDialog.value = false
    
    // Reload data
    await loadData()
  } catch (error) {
    console.error('Erro ao criar grupo:', error)
  } finally {
    creating.value = false
  }
}

const getGroupTypeIcon = (type: string) => {
  const icons = {
    family: 'mdi-home-heart',
    friends: 'mdi-account-group',
    team_fans: 'mdi-shield-star',
    competition: 'mdi-trophy',
    custom: 'mdi-cog'
  }
  return icons[type as keyof typeof icons] || 'mdi-account-group'
}

const getGroupTypeColor = (type: string) => {
  const colors = {
    family: '#FF6B6B',
    friends: '#4ECDC4',
    team_fans: '#45B7D1',
    competition: '#96CEB4',
    custom: '#FFEAA7'
  }
  return colors[type as keyof typeof colors] || 'primary'
}

const getGroupTypeLabel = (type: string) => {
  const labels = {
    family: 'Família',
    friends: 'Amigos',
    team_fans: 'Torcedores',
    competition: 'Competição',
    custom: 'Personalizado'
  }
  return labels[type as keyof typeof labels] || type
}

const getPrivacyColor = (level: string) => {
  const colors = {
    private: 'error',
    restricted: 'warning',
    public: 'success'
  }
  return colors[level as keyof typeof colors] || 'secondary'
}

const getPrivacyLabel = (level: string) => {
  const labels = {
    private: 'Privado',
    restricted: 'Restrito',
    public: 'Público'
  }
  return labels[level as keyof typeof labels] || level
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
