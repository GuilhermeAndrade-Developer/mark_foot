<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-account-multiple</v-icon>
          Gerenciar Usuários
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerencie usuários, perfis sociais e atividades de seguimento
        </p>
      </v-col>
    </v-row>

    <!-- Filters and Actions -->
    <v-card class="mb-6" elevation="2">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.search"
              label="Buscar usuários..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              @input="debouncedSearch"
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-select
              v-model="filters.is_active"
              :items="statusOptions"
              label="Status"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="loadUsers"
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-select
              v-model="filters.has_comments"
              :items="activityOptions"
              label="Atividade"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="loadUsers"
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-btn-group density="compact" variant="outlined">
              <v-btn
                :disabled="!selectedUsers.length"
                color="success"
                @click="bulkActivateUsers"
              >
                <v-icon start>mdi-account-check</v-icon>
                Ativar ({{ selectedUsers.length }})
              </v-btn>
              <v-btn
                :disabled="!selectedUsers.length"
                color="warning"
                @click="bulkDeactivateUsers"
              >
                <v-icon start>mdi-account-off</v-icon>
                Desativar
              </v-btn>
            </v-btn-group>
          </v-col>

          <v-col cols="12" md="2">
            <v-btn
              color="primary"
              variant="outlined"
              block
              @click="refreshData"
              :loading="loading"
            >
              <v-icon start>mdi-refresh</v-icon>
              Atualizar
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Users Table -->
    <v-card elevation="2">
      <v-data-table
        v-model="selectedUsers"
        :headers="headers"
        :items="users"
        :loading="loading"
        :items-per-page="25"
        :server-items-length="totalUsers"
        show-select
        item-value="id"
        @update:options="onTableOptionsUpdate"
      >
        <!-- User Column -->
        <template #item.user="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="40" class="mr-3" color="primary">
              <span class="text-white font-weight-bold">
                {{ item.username.charAt(0).toUpperCase() }}
              </span>
            </v-avatar>
            <div>
              <div class="font-weight-medium">{{ item.username }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.email }}</div>
              <div class="text-caption text-medium-emphasis" v-if="item.first_name || item.last_name">
                {{ item.first_name }} {{ item.last_name }}
              </div>
            </div>
          </div>
        </template>

        <!-- Status Column -->
        <template #item.is_active="{ item }">
          <v-chip
            :color="item.is_active ? 'success' : 'error'"
            :variant="item.is_active ? 'flat' : 'outlined'"
            size="small"
          >
            <v-icon start size="16">
              {{ item.is_active ? 'mdi-check' : 'mdi-close' }}
            </v-icon>
            {{ item.is_active ? 'Ativo' : 'Inativo' }}
          </v-chip>
        </template>

        <!-- Social Stats Column -->
        <template #item.social_stats="{ item }">
          <div class="d-flex align-center">
            <v-chip size="small" color="primary" variant="outlined" class="mr-1">
              <v-icon start size="12">mdi-comment</v-icon>
              {{ item.comments_count }}
            </v-chip>
            <v-chip size="small" color="info" variant="outlined" class="mr-1">
              <v-icon start size="12">mdi-account-heart</v-icon>
              {{ item.followers_count }}
            </v-chip>
            <v-chip size="small" color="secondary" variant="outlined">
              <v-icon start size="12">mdi-account-plus</v-icon>
              {{ item.following_count }}
            </v-chip>
          </div>
        </template>

        <!-- Date Joined Column -->
        <template #item.date_joined="{ item }">
          <div class="text-body-2">
            {{ formatDate(item.date_joined) }}
          </div>
        </template>

        <!-- Actions Column -->
        <template #item.actions="{ item }">
          <v-menu>
            <template #activator="{ props }">
              <v-btn
                variant="text"
                icon="mdi-dots-vertical"
                size="small"
                v-bind="props"
              />
            </template>
            <v-list density="compact">
              <v-list-item @click="showUserProfile(item)">
                <template #prepend>
                  <v-icon color="primary">mdi-account-details</v-icon>
                </template>
                <v-list-item-title>Ver Perfil</v-list-item-title>
              </v-list-item>

              <v-list-item @click="showUserComments(item)">
                <template #prepend>
                  <v-icon color="info">mdi-comment-multiple</v-icon>
                </template>
                <v-list-item-title>Comentários</v-list-item-title>
              </v-list-item>

              <v-list-item @click="showUserSocial(item)">
                <template #prepend>
                  <v-icon color="secondary">mdi-account-group</v-icon>
                </template>
                <v-list-item-title>Rede Social</v-list-item-title>
              </v-list-item>

              <v-divider />

              <v-list-item
                @click="toggleUserStatus(item)"
                :class="item.is_active ? 'text-warning' : 'text-success'"
              >
                <template #prepend>
                  <v-icon :color="item.is_active ? 'warning' : 'success'">
                    {{ item.is_active ? 'mdi-account-off' : 'mdi-account-check' }}
                  </v-icon>
                </template>
                <v-list-item-title>
                  {{ item.is_active ? 'Desativar' : 'Ativar' }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-data-table>
    </v-card>

    <!-- User Profile Dialog -->
    <v-dialog v-model="showProfileDialog" max-width="900">
      <v-card v-if="selectedUser">
        <v-card-title class="d-flex align-center">
          <v-avatar size="48" class="mr-4" color="primary">
            <span class="text-white text-h5 font-weight-bold">
              {{ selectedUser.username.charAt(0).toUpperCase() }}
            </span>
          </v-avatar>
          <div>
            <div class="text-h6">{{ selectedUser.username }}</div>
            <div class="text-subtitle-2 text-medium-emphasis">{{ selectedUser.email }}</div>
          </div>
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showProfileDialog = false"
          />
        </v-card-title>

        <v-card-text>
          <v-row>
            <!-- User Info -->
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="text-subtitle-1">
                  <v-icon class="mr-2">mdi-account-details</v-icon>
                  Informações Pessoais
                </v-card-title>
                <v-card-text>
                  <div class="mb-3">
                    <div class="text-subtitle-2 text-medium-emphasis">Nome Completo:</div>
                    <div class="text-body-1">
                      {{ selectedUser.first_name }} {{ selectedUser.last_name || 'Não informado' }}
                    </div>
                  </div>
                  <div class="mb-3">
                    <div class="text-subtitle-2 text-medium-emphasis">Email:</div>
                    <div class="text-body-1">{{ selectedUser.email }}</div>
                  </div>
                  <div class="mb-3">
                    <div class="text-subtitle-2 text-medium-emphasis">Data de Cadastro:</div>
                    <div class="text-body-1">{{ formatDateTime(selectedUser.date_joined) }}</div>
                  </div>
                  <div class="mb-3">
                    <div class="text-subtitle-2 text-medium-emphasis">Status:</div>
                    <v-chip
                      :color="selectedUser.is_active ? 'success' : 'error'"
                      size="small"
                    >
                      {{ selectedUser.is_active ? 'Ativo' : 'Inativo' }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Social Stats -->
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="text-subtitle-1">
                  <v-icon class="mr-2">mdi-chart-bar</v-icon>
                  Estatísticas Sociais
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="4" class="text-center">
                      <div class="text-h4 font-weight-bold text-primary">
                        {{ selectedUser.comments_count }}
                      </div>
                      <div class="text-caption text-medium-emphasis">Comentários</div>
                    </v-col>
                    <v-col cols="4" class="text-center">
                      <div class="text-h4 font-weight-bold text-info">
                        {{ selectedUser.followers_count }}
                      </div>
                      <div class="text-caption text-medium-emphasis">Seguidores</div>
                    </v-col>
                    <v-col cols="4" class="text-center">
                      <div class="text-h4 font-weight-bold text-secondary">
                        {{ selectedUser.following_count }}
                      </div>
                      <div class="text-caption text-medium-emphasis">Seguindo</div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Recent Activity -->
            <v-col cols="12">
              <v-card variant="outlined">
                <v-card-title class="text-subtitle-1">
                  <v-icon class="mr-2">mdi-clock</v-icon>
                  Atividades Recentes
                </v-card-title>
                <v-card-text>
                  <v-list v-if="selectedUser.recent_activity && selectedUser.recent_activity.length">
                    <v-list-item
                      v-for="activity in selectedUser.recent_activity"
                      :key="activity.id"
                    >
                      <template #prepend>
                        <v-avatar
                          :color="getActivityColor(activity.activity_type)"
                          size="24"
                          class="mr-3"
                        >
                          <v-icon color="white" size="12">
                            {{ getActivityIcon(activity.activity_type) }}
                          </v-icon>
                        </v-avatar>
                      </template>

                      <v-list-item-title>{{ activity.description }}</v-list-item-title>

                      <template #append>
                        <v-chip size="small" variant="text">
                          {{ formatRelativeTime(activity.created_at) }}
                        </v-chip>
                      </template>
                    </v-list-item>
                  </v-list>
                  <div v-else class="text-center py-4 text-medium-emphasis">
                    Nenhuma atividade recente
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            :color="selectedUser.is_active ? 'warning' : 'success'"
            variant="outlined"
            @click="toggleUserStatus(selectedUser)"
          >
            <v-icon start>
              {{ selectedUser.is_active ? 'mdi-account-off' : 'mdi-account-check' }}
            </v-icon>
            {{ selectedUser.is_active ? 'Desativar' : 'Ativar' }}
          </v-btn>
          <v-btn
            color="primary"
            variant="outlined"
            @click="showUserComments(selectedUser)"
          >
            <v-icon start>mdi-comment-multiple</v-icon>
            Ver Comentários
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- User Comments Dialog -->
    <v-dialog v-model="showCommentsDialog" max-width="1000">
      <v-card v-if="selectedUserForComments">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-3">mdi-comment-multiple</v-icon>
          Comentários de {{ selectedUserForComments.username }}
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showCommentsDialog = false"
          />
        </v-card-title>

        <v-card-text>
          <v-data-table
            :headers="commentHeaders"
            :items="userComments"
            :loading="loadingUserComments"
            density="compact"
          >
            <template #item.content="{ item }">
              <div class="comment-content">
                {{ truncateText(item.content, 80) }}
              </div>
            </template>

            <template #item.match="{ item }">
              <div class="text-body-2">
                {{ item.match.home_team }} vs {{ item.match.away_team }}
              </div>
            </template>

            <template #item.status="{ item }">
              <v-chip
                :color="getCommentStatusColor(item)"
                size="small"
              >
                {{ getCommentStatusText(item) }}
              </v-chip>
            </template>

            <template #item.created_at="{ item }">
              <div class="text-body-2">
                {{ formatDate(item.created_at) }}
              </div>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- User Social Dialog -->
    <v-dialog v-model="showSocialDialog" max-width="800">
      <v-card v-if="selectedUserForSocial">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-3">mdi-account-group</v-icon>
          Rede Social de {{ selectedUserForSocial.username }}
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showSocialDialog = false"
          />
        </v-card-title>

        <v-card-text>
          <v-tabs v-model="socialTab">
            <v-tab value="followers">
              <v-icon start>mdi-account-heart</v-icon>
              Seguidores ({{ userFollowers.length }})
            </v-tab>
            <v-tab value="following">
              <v-icon start>mdi-account-plus</v-icon>
              Seguindo ({{ userFollowing.length }})
            </v-tab>
          </v-tabs>

          <v-window v-model="socialTab" class="mt-4">
            <v-window-item value="followers">
              <v-list v-if="userFollowers.length">
                <v-list-item
                  v-for="follow in userFollowers"
                  :key="follow.id"
                >
                  <template #prepend>
                    <v-avatar size="32" color="primary" class="mr-3">
                      <span class="text-white">
                        {{ follow.follower.username.charAt(0).toUpperCase() }}
                      </span>
                    </v-avatar>
                  </template>

                  <v-list-item-title>{{ follow.follower.username }}</v-list-item-title>

                  <template #append>
                    <v-chip size="small" variant="text">
                      {{ formatRelativeTime(follow.created_at) }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="text-center py-8 text-medium-emphasis">
                Nenhum seguidor encontrado
              </div>
            </v-window-item>

            <v-window-item value="following">
              <v-list v-if="userFollowing.length">
                <v-list-item
                  v-for="follow in userFollowing"
                  :key="follow.id"
                >
                  <template #prepend>
                    <v-avatar size="32" color="primary" class="mr-3">
                      <span class="text-white">
                        {{ follow.following.username.charAt(0).toUpperCase() }}
                      </span>
                    </v-avatar>
                  </template>

                  <v-list-item-title>{{ follow.following.username }}</v-list-item-title>

                  <template #append>
                    <v-chip size="small" variant="text">
                      {{ formatRelativeTime(follow.created_at) }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="text-center py-8 text-medium-emphasis">
                Não está seguindo ninguém
              </div>
            </v-window-item>
          </v-window>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import SocialApiService, { type UserProfile, type Comment } from '@/services/socialApi'
import { debounce } from 'lodash-es'
import { format, formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Reactive data
const loading = ref(false)
const loadingUserComments = ref(false)
const users = ref<UserProfile[]>([])
const totalUsers = ref(0)
const selectedUsers = ref<number[]>([])
const selectedUser = ref<UserProfile | null>(null)
const selectedUserForComments = ref<UserProfile | null>(null)
const selectedUserForSocial = ref<UserProfile | null>(null)

// Dialog states
const showProfileDialog = ref(false)
const showCommentsDialog = ref(false)
const showSocialDialog = ref(false)

// User details data
const userComments = ref<Comment[]>([])
const userFollowers = ref([])
const userFollowing = ref([])
const socialTab = ref('followers')

// Filters
const filters = reactive({
  search: '',
  is_active: null,
  has_comments: null,
  page: 1
})

// Table configuration
const headers = [
  { title: 'Usuário', key: 'user', sortable: false },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Estatísticas Sociais', key: 'social_stats', sortable: false },
  { title: 'Data de Cadastro', key: 'date_joined', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

const commentHeaders = [
  { title: 'Conteúdo', key: 'content', sortable: false },
  { title: 'Partida', key: 'match', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Data', key: 'created_at', sortable: true }
]

// Options
const statusOptions = [
  { title: 'Todos', value: null },
  { title: 'Ativos', value: true },
  { title: 'Inativos', value: false }
]

const activityOptions = [
  { title: 'Todos', value: null },
  { title: 'Com Comentários', value: true },
  { title: 'Sem Comentários', value: false }
]

// Computed
const debouncedSearch = debounce(() => {
  loadUsers()
}, 500)

// Methods
const loadUsers = async () => {
  try {
    loading.value = true
    const params = {
      page: filters.page,
      search: filters.search || undefined,
      is_active: filters.is_active,
      has_comments: filters.has_comments
    }
    
    const data = await SocialApiService.getUsers(params)
    users.value = data.results
    totalUsers.value = data.count
  } catch (error) {
    console.error('Erro ao carregar usuários:', error)
  } finally {
    loading.value = false
  }
}

const onTableOptionsUpdate = (options: any) => {
  filters.page = options.page
  loadUsers()
}

const refreshData = () => {
  selectedUsers.value = []
  loadUsers()
}

const showUserProfile = async (user: UserProfile) => {
  try {
    const fullProfile = await SocialApiService.getUserProfile(user.id)
    selectedUser.value = fullProfile
    showProfileDialog.value = true
  } catch (error) {
    console.error('Erro ao carregar perfil do usuário:', error)
  }
}

const showUserComments = async (user: UserProfile) => {
  try {
    loadingUserComments.value = true
    selectedUserForComments.value = user
    showCommentsDialog.value = true
    
    const data = await SocialApiService.getUserComments(user.id)
    userComments.value = data.results
  } catch (error) {
    console.error('Erro ao carregar comentários do usuário:', error)
  } finally {
    loadingUserComments.value = false
  }
}

const showUserSocial = async (user: UserProfile) => {
  try {
    selectedUserForSocial.value = user
    showSocialDialog.value = true
    
    const [followersData, followingData] = await Promise.all([
      SocialApiService.getUserFollowers(user.id),
      SocialApiService.getUserFollowing(user.id)
    ])
    
    userFollowers.value = followersData.results
    userFollowing.value = followingData.results
  } catch (error) {
    console.error('Erro ao carregar dados sociais do usuário:', error)
  }
}

const toggleUserStatus = async (user: UserProfile) => {
  try {
    const newStatus = !user.is_active
    await SocialApiService.updateUserStatus(user.id, newStatus)
    
    // Update user in list
    const userIndex = users.value.findIndex(u => u.id === user.id)
    if (userIndex !== -1) {
      users.value[userIndex].is_active = newStatus
    }
    
    // Update selected user if in dialog
    if (selectedUser.value?.id === user.id) {
      selectedUser.value.is_active = newStatus
    }
  } catch (error) {
    console.error('Erro ao alterar status do usuário:', error)
  }
}

const bulkActivateUsers = async () => {
  if (!selectedUsers.value.length) return
  
  try {
    for (const userId of selectedUsers.value) {
      await SocialApiService.updateUserStatus(userId, true)
    }
    selectedUsers.value = []
    loadUsers()
  } catch (error) {
    console.error('Erro ao ativar usuários em massa:', error)
  }
}

const bulkDeactivateUsers = async () => {
  if (!selectedUsers.value.length) return
  
  if (!confirm(`Tem certeza que deseja desativar ${selectedUsers.value.length} usuário(s)?`)) return
  
  try {
    for (const userId of selectedUsers.value) {
      await SocialApiService.updateUserStatus(userId, false)
    }
    selectedUsers.value = []
    loadUsers()
  } catch (error) {
    console.error('Erro ao desativar usuários em massa:', error)
  }
}

// Utility functions
const truncateText = (text: string, maxLength: number) => {
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
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

const getCommentStatusColor = (comment: Comment) => {
  if (comment.is_flagged) return 'error'
  if (comment.is_approved) return 'success'
  return 'warning'
}

const getCommentStatusText = (comment: Comment) => {
  if (comment.is_flagged) return 'Flagrado'
  if (comment.is_approved) return 'Aprovado'
  return 'Pendente'
}

const formatDate = (dateString: string) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy', { locale: ptBR })
  } catch {
    return 'Data inválida'
  }
}

const formatDateTime = (dateString: string) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: ptBR })
  } catch {
    return 'Data inválida'
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
  loadUsers()
})
</script>

<style scoped>
.comment-content {
  max-width: 250px;
}

.v-data-table {
  background: transparent;
}

.v-chip {
  font-weight: 500;
}

.text-h4 {
  font-size: 2rem !important;
}
</style>
