<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-account-group</v-icon>
          Social Dashboard
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerencie comentários, usuários e atividades sociais
        </p>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card elevation="2" color="primary" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-comment-multiple</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.total_comments || 0 }}</div>
                <div class="text-subtitle-2">Total de Comentários</div>
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
                <div class="text-h4 font-weight-bold">{{ stats.total_users || 0 }}</div>
                <div class="text-subtitle-2">Usuários Totais</div>
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
                <div class="text-h4 font-weight-bold">{{ stats.total_follows || 0 }}</div>
                <div class="text-subtitle-2">Relacionamentos</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card elevation="2" color="warning" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">mdi-flag</v-icon>
              <div>
                <div class="text-h4 font-weight-bold">{{ stats.pending_reports || 0 }}</div>
                <div class="text-subtitle-2">Denúncias Pendentes</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Today's Activity -->
    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-calendar-today</v-icon>
            Atividade de Hoje
          </v-card-title>
          <v-card-text>
            <div class="d-flex align-center justify-center py-8">
              <div class="text-center">
                <div class="text-h2 font-weight-bold text-primary">
                  {{ stats.active_comments_today || 0 }}
                </div>
                <div class="text-subtitle-1 text-medium-emphasis">
                  Comentários Hoje
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3">mdi-alert</v-icon>
            Moderação Necessária
          </v-card-title>
          <v-card-text>
            <div class="d-flex align-center justify-center py-8">
              <div class="text-center">
                <div class="text-h2 font-weight-bold text-error">
                  {{ stats.flagged_comments || 0 }}
                </div>
                <div class="text-subtitle-1 text-medium-emphasis">
                  Comentários Flagados
                </div>
              </div>
            </div>
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
                  @click="router.push('/social/comments')"
                >
                  <v-icon start>mdi-comment-edit</v-icon>
                  Gerenciar Comentários
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="success"
                  block
                  size="large"
                  variant="outlined"
                  @click="router.push('/social/users')"
                >
                  <v-icon start>mdi-account-cog</v-icon>
                  Gerenciar Usuários
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="warning"
                  block
                  size="large"
                  variant="outlined"
                  @click="moderateFlaggedComments"
                >
                  <v-icon start>mdi-flag-remove</v-icon>
                  Moderar Flagados
                </v-btn>
              </v-col>

              <v-col cols="12" md="6" lg="3">
                <v-btn
                  color="info"
                  block
                  size="large"
                  variant="outlined"
                  @click="exportData"
                >
                  <v-icon start>mdi-download</v-icon>
                  Exportar Dados
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Top Contributors & Recent Activity -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-trophy</v-icon>
            Principais Comentaristas
          </v-card-title>
          <v-card-text>
            <v-list v-if="stats.top_commenters && stats.top_commenters.length">
              <v-list-item
                v-for="(user, index) in stats.top_commenters"
                :key="user.id"
              >
                <template #prepend>
                  <v-avatar
                    :color="getTrophyColor(index)"
                    size="32"
                    class="mr-3"
                  >
                    <v-icon color="white">{{ getTrophyIcon(index) }}</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ user.username }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ user.comment_count }} comentários
                </v-list-item-subtitle>

                <template #append>
                  <v-chip size="small" color="primary">
                    #{{ index + 1 }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-8 text-medium-emphasis">
              Nenhum comentário encontrado
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-3">mdi-clock</v-icon>
            Atividades Recentes
          </v-card-title>
          <v-card-text>
            <v-list v-if="stats.recent_activities && stats.recent_activities.length">
              <v-list-item
                v-for="activity in stats.recent_activities"
                :key="activity.id"
              >
                <template #prepend>
                  <v-avatar
                    :color="getActivityColor(activity.activity_type)"
                    size="32"
                    class="mr-3"
                  >
                    <v-icon color="white" size="16">
                      {{ getActivityIcon(activity.activity_type) }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ activity.user.username }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ activity.description }}
                </v-list-item-subtitle>

                <template #append>
                  <v-chip size="small" variant="text">
                    {{ formatRelativeTime(activity.created_at) }}
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SocialApiService from '@/services/socialApi'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Router
const router = useRouter()

// Reactive data
const loading = ref(false)
const stats = ref({
  total_comments: 0,
  total_users: 0,
  total_follows: 0,
  active_comments_today: 0,
  pending_reports: 0,
  flagged_comments: 0,
  top_commenters: [],
  recent_activities: []
})

// Methods
const loadStats = async () => {
  try {
    loading.value = true
    const data = await SocialApiService.getStats()
    stats.value = data
  } catch (error) {
    console.error('Erro ao carregar estatísticas sociais:', error)
  } finally {
    loading.value = false
  }
}

const moderateFlaggedComments = () => {
  // Navigate to comments page with flagged filter
  router.push('/social/comments?status=flagged')
}

const exportData = () => {
  // Implement data export functionality
  alert('Funcionalidade de exportação em desenvolvimento')
}

const getTrophyColor = (index: number) => {
  switch (index) {
    case 0: return 'warning' // Gold
    case 1: return 'grey-lighten-1' // Silver
    case 2: return 'deep-orange' // Bronze
    default: return 'primary'
  }
}

const getTrophyIcon = (index: number) => {
  switch (index) {
    case 0: return 'mdi-trophy'
    case 1: return 'mdi-medal'
    case 2: return 'mdi-medal'
    default: return 'mdi-account'
  }
}

const getActivityColor = (type: string) => {
  switch (type) {
    case 'comment': return 'primary'
    case 'like': return 'success'
    case 'follow': return 'info'
    case 'join': return 'secondary'
    default: return 'grey'
  }
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'comment': return 'mdi-comment'
    case 'like': return 'mdi-heart'
    case 'follow': return 'mdi-account-plus'
    case 'join': return 'mdi-account-check'
    default: return 'mdi-circle'
  }
}

const formatRelativeTime = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), { 
      addSuffix: true, 
      locale: ptBR 
    })
  } catch {
    return 'Agora'
  }
}

// Lifecycle
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}

.text-h2 {
  font-size: 3rem !important;
}
</style>
