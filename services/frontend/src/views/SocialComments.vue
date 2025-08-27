<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-comment-multiple</v-icon>
          Gerenciar Comentários
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Modere comentários, aprovar conteúdo e gerenciar denúncias
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
              label="Buscar comentários..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              @input="debouncedSearch"
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Status"
              variant="outlined"
              density="compact"
              hide-details
              @update:model-value="loadComments"
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-select
              v-model="filters.match_id"
              :items="matchOptions"
              label="Partida"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              @update:model-value="loadComments"
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-btn-group density="compact" variant="outlined">
              <v-btn
                :disabled="!selectedComments.length"
                color="success"
                @click="bulkAction('approve')"
              >
                <v-icon start>mdi-check</v-icon>
                Aprovar ({{ selectedComments.length }})
              </v-btn>
              <v-btn
                :disabled="!selectedComments.length"
                color="warning"
                @click="showBulkFlagDialog = true"
              >
                <v-icon start>mdi-flag</v-icon>
                Flagrar
              </v-btn>
              <v-btn
                :disabled="!selectedComments.length"
                color="error"
                @click="bulkAction('delete')"
              >
                <v-icon start>mdi-delete</v-icon>
                Excluir
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

    <!-- Comments Table -->
    <v-card elevation="2">
      <v-data-table
        v-model="selectedComments"
        :headers="headers"
        :items="comments"
        :loading="loading"
        :items-per-page="25"
        :server-items-length="totalComments"
        show-select
        item-value="id"
        @update:options="onTableOptionsUpdate"
      >
        <!-- User Column -->
        <template #item.user="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3" color="primary">
              <span class="text-white font-weight-bold">
                {{ item.user.username.charAt(0).toUpperCase() }}
              </span>
            </v-avatar>
            <div>
              <div class="font-weight-medium">{{ item.user.username }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.user.email }}</div>
            </div>
          </div>
        </template>

        <!-- Content Column -->
        <template #item.content="{ item }">
          <div class="comment-content">
            <p class="mb-1">{{ truncateText(item.content, 100) }}</p>
            <v-btn
              v-if="item.content.length > 100"
              size="x-small"
              variant="text"
              color="primary"
              @click="showCommentDialog(item)"
            >
              Ver completo
            </v-btn>
          </div>
        </template>

        <!-- Match Column -->
        <template #item.match="{ item }">
          <div class="text-body-2">
            <div class="font-weight-medium">
              {{ item.match.home_team }} vs {{ item.match.away_team }}
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ formatDate(item.match.date) }}
            </div>
          </div>
        </template>

        <!-- Status Column -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item)"
            :variant="item.is_approved ? 'flat' : 'outlined'"
            size="small"
          >
            <v-icon start size="16">{{ getStatusIcon(item) }}</v-icon>
            {{ getStatusText(item) }}
          </v-chip>
        </template>

        <!-- Engagement Column -->
        <template #item.engagement="{ item }">
          <div class="d-flex align-center">
            <v-chip size="small" color="success" variant="outlined" class="mr-1">
              <v-icon start size="12">mdi-thumb-up</v-icon>
              {{ item.likes_count }}
            </v-chip>
            <v-chip size="small" color="error" variant="outlined" class="mr-1">
              <v-icon start size="12">mdi-thumb-down</v-icon>
              {{ item.dislikes_count }}
            </v-chip>
            <v-chip size="small" color="info" variant="outlined">
              <v-icon start size="12">mdi-comment-reply</v-icon>
              {{ item.replies_count }}
            </v-chip>
          </div>
        </template>

        <!-- Created At Column -->
        <template #item.created_at="{ item }">
          <div class="text-body-2">
            {{ formatDateTime(item.created_at) }}
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
              <v-list-item
                v-if="!item.is_approved"
                @click="approveComment(item.id)"
              >
                <template #prepend>
                  <v-icon color="success">mdi-check</v-icon>
                </template>
                <v-list-item-title>Aprovar</v-list-item-title>
              </v-list-item>

              <v-list-item
                v-if="!item.is_flagged"
                @click="openFlagDialog(item)"
              >
                <template #prepend>
                  <v-icon color="warning">mdi-flag</v-icon>
                </template>
                <v-list-item-title>Flagrar</v-list-item-title>
              </v-list-item>

              <v-list-item
                v-if="item.is_flagged"
                @click="unflagComment(item.id)"
              >
                <template #prepend>
                  <v-icon color="info">mdi-flag-remove</v-icon>
                </template>
                <v-list-item-title>Desflagrar</v-list-item-title>
              </v-list-item>

              <v-list-item @click="showCommentDialog(item)">
                <template #prepend>
                  <v-icon color="primary">mdi-eye</v-icon>
                </template>
                <v-list-item-title>Ver Detalhes</v-list-item-title>
              </v-list-item>

              <v-divider />

              <v-list-item
                @click="deleteComment(item.id)"
                class="text-error"
              >
                <template #prepend>
                  <v-icon color="error">mdi-delete</v-icon>
                </template>
                <v-list-item-title>Excluir</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-data-table>
    </v-card>

    <!-- Comment Detail Dialog -->
    <v-dialog v-model="showDetailDialog" max-width="800">
      <v-card v-if="selectedComment">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-3">mdi-comment-text</v-icon>
          Detalhes do Comentário
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showDetailDialog = false"
          />
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col cols="12">
              <div class="mb-4">
                <div class="text-subtitle-2 text-medium-emphasis mb-2">Conteúdo:</div>
                <div class="text-body-1 pa-3 bg-grey-lighten-4 rounded">
                  {{ selectedComment.content }}
                </div>
              </div>
            </v-col>

            <v-col cols="12" md="6">
              <div class="mb-3">
                <div class="text-subtitle-2 text-medium-emphasis">Usuário:</div>
                <div class="text-body-1">{{ selectedComment.user.username }}</div>
              </div>
            </v-col>

            <v-col cols="12" md="6">
              <div class="mb-3">
                <div class="text-subtitle-2 text-medium-emphasis">Status:</div>
                <v-chip
                  :color="getStatusColor(selectedComment)"
                  size="small"
                >
                  {{ getStatusText(selectedComment) }}
                </v-chip>
              </div>
            </v-col>

            <v-col cols="12" md="6">
              <div class="mb-3">
                <div class="text-subtitle-2 text-medium-emphasis">Partida:</div>
                <div class="text-body-1">
                  {{ selectedComment.match.home_team }} vs {{ selectedComment.match.away_team }}
                </div>
              </div>
            </v-col>

            <v-col cols="12" md="6">
              <div class="mb-3">
                <div class="text-subtitle-2 text-medium-emphasis">Data:</div>
                <div class="text-body-1">{{ formatDateTime(selectedComment.created_at) }}</div>
              </div>
            </v-col>

            <v-col cols="12" v-if="selectedComment.flag_reason">
              <div class="mb-3">
                <div class="text-subtitle-2 text-medium-emphasis">Motivo do Flag:</div>
                <div class="text-body-1 text-error">{{ selectedComment.flag_reason }}</div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            v-if="!selectedComment.is_approved"
            color="success"
            variant="outlined"
            @click="approveComment(selectedComment.id)"
          >
            <v-icon start>mdi-check</v-icon>
            Aprovar
          </v-btn>
          <v-btn
            v-if="!selectedComment.is_flagged"
            color="warning"
            variant="outlined"
            @click="openFlagDialog(selectedComment)"
          >
            <v-icon start>mdi-flag</v-icon>
            Flagrar
          </v-btn>
          <v-btn
            color="error"
            variant="outlined"
            @click="deleteComment(selectedComment.id)"
          >
            <v-icon start>mdi-delete</v-icon>
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Flag Dialog -->
    <v-dialog v-model="showFlagDialog" max-width="500">
      <v-card>
        <v-card-title>
          <v-icon class="mr-3">mdi-flag</v-icon>
          Flagrar Comentário
        </v-card-title>

        <v-card-text>
          <v-textarea
            v-model="flagReason"
            label="Motivo do flag"
            placeholder="Descreva o motivo pelo qual este comentário está sendo flagrado..."
            variant="outlined"
            rows="3"
            :rules="[v => !!v || 'Motivo é obrigatório']"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showFlagDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="warning"
            @click="confirmFlag"
            :disabled="!flagReason"
          >
            Flagrar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Bulk Flag Dialog -->
    <v-dialog v-model="showBulkFlagDialog" max-width="500">
      <v-card>
        <v-card-title>
          <v-icon class="mr-3">mdi-flag-multiple</v-icon>
          Flagrar Comentários em Massa
        </v-card-title>

        <v-card-text>
          <p class="mb-4">
            Flagrar {{ selectedComments.length }} comentário(s) selecionado(s).
          </p>
          <v-textarea
            v-model="bulkFlagReason"
            label="Motivo do flag"
            placeholder="Descreva o motivo..."
            variant="outlined"
            rows="3"
            :rules="[v => !!v || 'Motivo é obrigatório']"
          />
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="showBulkFlagDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="warning"
            @click="confirmBulkFlag"
            :disabled="!bulkFlagReason"
          >
            Flagrar Todos
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import SocialApiService, { type Comment } from '@/services/socialApi'
import { debounce } from 'lodash-es'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Reactive data
const loading = ref(false)
const comments = ref<Comment[]>([])
const totalComments = ref(0)
const selectedComments = ref<number[]>([])
const selectedComment = ref<Comment | null>(null)

// Dialog states
const showDetailDialog = ref(false)
const showFlagDialog = ref(false)
const showBulkFlagDialog = ref(false)

// Form data
const flagReason = ref('')
const bulkFlagReason = ref('')
const commentToFlag = ref<Comment | null>(null)

// Filters
const filters = reactive({
  search: '',
  status: 'all',
  match_id: null,
  page: 1
})

// Table configuration
const headers = [
  { title: 'Usuário', key: 'user', sortable: false },
  { title: 'Conteúdo', key: 'content', sortable: false },
  { title: 'Partida', key: 'match', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Engajamento', key: 'engagement', sortable: false },
  { title: 'Data', key: 'created_at', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

// Options
const statusOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Aprovados', value: 'approved' },
  { title: 'Pendentes', value: 'pending' },
  { title: 'Flagrados', value: 'flagged' }
]

const matchOptions = ref([])

// Computed
const debouncedSearch = debounce(() => {
  loadComments()
}, 500)

// Methods
const loadComments = async () => {
  try {
    loading.value = true
    const params = {
      page: filters.page,
      search: filters.search || undefined,
      status: filters.status !== 'all' ? filters.status : undefined,
      match_id: filters.match_id || undefined
    }
    
    const data = await SocialApiService.getComments(params)
    comments.value = data.results
    totalComments.value = data.count
  } catch (error) {
    console.error('Erro ao carregar comentários:', error)
  } finally {
    loading.value = false
  }
}

const onTableOptionsUpdate = (options: any) => {
  filters.page = options.page
  loadComments()
}

const refreshData = () => {
  selectedComments.value = []
  loadComments()
}

const showCommentDialog = (comment: Comment) => {
  selectedComment.value = comment
  showDetailDialog.value = true
}

const openFlagDialog = (comment: Comment) => {
  commentToFlag.value = comment
  flagReason.value = ''
  showFlagDialog.value = true
}

const approveComment = async (id: number) => {
  try {
    await SocialApiService.approveComment(id)
    loadComments()
    if (showDetailDialog.value) {
      showDetailDialog.value = false
    }
  } catch (error) {
    console.error('Erro ao aprovar comentário:', error)
  }
}

const confirmFlag = async () => {
  if (!commentToFlag.value || !flagReason.value) return
  
  try {
    await SocialApiService.flagComment(commentToFlag.value.id, flagReason.value)
    showFlagDialog.value = false
    if (showDetailDialog.value) {
      showDetailDialog.value = false
    }
    loadComments()
  } catch (error) {
    console.error('Erro ao flagrar comentário:', error)
  }
}

const unflagComment = async (id: number) => {
  try {
    await SocialApiService.unflagComment(id)
    loadComments()
  } catch (error) {
    console.error('Erro ao desflagrar comentário:', error)
  }
}

const deleteComment = async (id: number) => {
  if (!confirm('Tem certeza que deseja excluir este comentário?')) return
  
  try {
    await SocialApiService.deleteComment(id)
    loadComments()
    if (showDetailDialog.value) {
      showDetailDialog.value = false
    }
  } catch (error) {
    console.error('Erro ao excluir comentário:', error)
  }
}

const bulkAction = async (action: 'approve' | 'flag' | 'delete') => {
  if (!selectedComments.value.length) return
  
  if (action === 'delete') {
    if (!confirm(`Tem certeza que deseja excluir ${selectedComments.value.length} comentário(s)?`)) return
  }
  
  try {
    await SocialApiService.bulkModerateComments(selectedComments.value, action)
    selectedComments.value = []
    loadComments()
  } catch (error) {
    console.error(`Erro ao executar ação em massa:`, error)
  }
}

const confirmBulkFlag = async () => {
  if (!bulkFlagReason.value) return
  
  try {
    await SocialApiService.bulkModerateComments(
      selectedComments.value, 
      'flag', 
      bulkFlagReason.value
    )
    showBulkFlagDialog.value = false
    selectedComments.value = []
    loadComments()
  } catch (error) {
    console.error('Erro ao flagrar comentários em massa:', error)
  }
}

// Utility functions
const truncateText = (text: string, maxLength: number) => {
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const getStatusColor = (comment: Comment) => {
  if (comment.is_flagged) return 'error'
  if (comment.is_approved) return 'success'
  return 'warning'
}

const getStatusIcon = (comment: Comment) => {
  if (comment.is_flagged) return 'mdi-flag'
  if (comment.is_approved) return 'mdi-check'
  return 'mdi-clock'
}

const getStatusText = (comment: Comment) => {
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

// Lifecycle
onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.comment-content {
  max-width: 300px;
}

.v-data-table {
  background: transparent;
}

.v-chip {
  font-weight: 500;
}
</style>
