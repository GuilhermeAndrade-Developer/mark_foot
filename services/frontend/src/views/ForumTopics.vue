<template>
  <div class="forum-topics">
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold mb-2">Gerenciar Tópicos</h1>
        <p class="text-body-1 text-medium-emphasis">
          Visualize e gerencie todos os tópicos do fórum
        </p>
      </div>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="createTopicDialog = true"
      >
        Novo Tópico
      </v-btn>
    </div>

    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="primary" class="mr-3">
              <v-icon>mdi-forum</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ stats?.total_topics || 0 }}</div>
              <div class="text-body-2 text-medium-emphasis">Total de Tópicos</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="success" class="mr-3">
              <v-icon>mdi-check-circle</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ openTopicsCount }}</div>
              <div class="text-body-2 text-medium-emphasis">Tópicos Abertos</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="warning" class="mr-3">
              <v-icon>mdi-pin</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ pinnedTopicsCount }}</div>
              <div class="text-body-2 text-medium-emphasis">Tópicos Fixados</div>
            </div>
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <div class="d-flex align-center">
            <v-avatar color="error" class="mr-3">
              <v-icon>mdi-lock</v-icon>
            </v-avatar>
            <div>
              <div class="text-h5 font-weight-bold">{{ closedTopicsCount }}</div>
              <div class="text-body-2 text-medium-emphasis">Tópicos Fechados</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.category"
              :items="categoryOptions"
              label="Categoria"
              clearable
              density="compact"
              @update:model-value="loadTopics"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Status"
              density="compact"
              @update:model-value="loadTopics"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.search"
              label="Buscar tópicos"
              prepend-inner-icon="mdi-magnify"
              clearable
              density="compact"
              @keyup.enter="loadTopics"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.sort"
              :items="sortOptions"
              label="Ordenar por"
              density="compact"
              @update:model-value="loadTopics"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Topics Table -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-forum</v-icon>
        Tópicos
        <v-spacer />
        <v-chip v-if="loading" color="primary" variant="outlined">
          <v-progress-circular indeterminate size="16" class="mr-2" />
          Carregando...
        </v-chip>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="topics"
        :loading="loading"
        item-key="id"
        class="elevation-0"
        :items-per-page="20"
      >
        <!-- Title with category -->
        <template #item.title="{ item }">
          <div>
            <div class="font-weight-medium">{{ item.title }}</div>
            <v-chip
              size="x-small"
              color="primary"
              variant="outlined"
              class="mt-1"
            >
              {{ getCategoryName(item.category_id) }}
            </v-chip>
          </div>
        </template>

        <!-- Author -->
        <template #item.author="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="24" class="mr-2">
              <v-icon size="16">mdi-account</v-icon>
            </v-avatar>
            <div>
              <div class="text-body-2">{{ item.author.first_name }} {{ item.author.last_name }}</div>
              <div class="text-caption text-medium-emphasis">@{{ item.author.username }}</div>
            </div>
          </div>
        </template>

        <!-- Status -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="flat"
          >
            <v-icon start :icon="getStatusIcon(item.status)" />
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>

        <!-- Stats -->
        <template #item.stats="{ item }">
          <div class="text-center">
            <div class="text-body-2 font-weight-medium">{{ item.post_count }}</div>
            <div class="text-caption text-medium-emphasis">posts</div>
          </div>
        </template>

        <!-- Last Activity -->
        <template #item.last_activity="{ item }">
          <div class="text-body-2">{{ formatDate(item.last_activity) }}</div>
        </template>

        <!-- Actions -->
        <template #item.actions="{ item }">
          <div class="d-flex align-center">
            <v-tooltip text="Visualizar">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewTopic(item)"
                />
              </template>
            </v-tooltip>
            
            <v-tooltip text="Editar">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="editTopic(item)"
                />
              </template>
            </v-tooltip>

            <v-menu>
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-dots-vertical"
                  size="small"
                  variant="text"
                />
              </template>
              <v-list>
                <v-list-item @click="togglePin(item)">
                  <v-list-item-title>
                    <v-icon class="mr-2">{{ item.status === 'pinned' ? 'mdi-pin-off' : 'mdi-pin' }}</v-icon>
                    {{ item.status === 'pinned' ? 'Desafixar' : 'Fixar' }}
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="toggleLock(item)">
                  <v-list-item-title>
                    <v-icon class="mr-2">{{ item.status === 'locked' ? 'mdi-lock-open' : 'mdi-lock' }}</v-icon>
                    {{ item.status === 'locked' ? 'Desbloquear' : 'Bloquear' }}
                  </v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item @click="deleteTopic(item)" class="text-error">
                  <v-list-item-title>
                    <v-icon class="mr-2">mdi-delete</v-icon>
                    Excluir
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Create Topic Dialog -->
    <v-dialog v-model="createTopicDialog" max-width="600">
      <v-card>
        <v-card-title>Criar Novo Tópico</v-card-title>
        <v-card-text>
          <v-form ref="createForm" v-model="createFormValid">
            <v-text-field
              v-model="newTopic.title"
              label="Título do Tópico"
              :rules="[rules.required]"
              density="compact"
              class="mb-3"
            />
            
            <v-select
              v-model="newTopic.category_id"
              :items="categoryOptions"
              label="Categoria"
              :rules="[rules.required]"
              density="compact"
              class="mb-3"
            />
            
            <v-textarea
              v-model="newTopic.content"
              label="Conteúdo"
              :rules="[rules.required]"
              rows="4"
              density="compact"
              class="mb-3"
            />
            
            <v-text-field
              v-model="newTopic.tags"
              label="Tags (separadas por vírgula)"
              density="compact"
              hint="Ex: bayern, bundesliga, análise"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="createTopicDialog = false">Cancelar</v-btn>
          <v-btn
            color="primary"
            :disabled="!createFormValid"
            :loading="creating"
            @click="createTopic"
          >
            Criar Tópico
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useForumStore } from '@/stores/forum'
import type { ForumTopic } from '@/services/forumApi'

const forumStore = useForumStore()

// State
const loading = ref(false)
const creating = ref(false)
const createTopicDialog = ref(false)
const createFormValid = ref(false)

// Filters
const filters = ref({
  category: '',
  status: 'all',
  search: '',
  sort: 'last_activity'
})

// New topic form
const newTopic = ref({
  title: '',
  category_id: '',
  content: '',
  tags: ''
})

// Form rules
const rules = {
  required: (value: string) => !!value || 'Campo obrigatório'
}

// Table headers
const headers = [
  { title: 'Tópico', key: 'title', sortable: false },
  { title: 'Autor', key: 'author', sortable: false },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Posts', key: 'stats', sortable: false },
  { title: 'Última Atividade', key: 'last_activity', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Options
const statusOptions = [
  { title: 'Todos', value: 'all' },
  { title: 'Abertos', value: 'open' },
  { title: 'Fixados', value: 'pinned' },
  { title: 'Fechados', value: 'closed' },
  { title: 'Bloqueados', value: 'locked' }
]

const sortOptions = [
  { title: 'Última Atividade', value: 'last_activity' },
  { title: 'Data de Criação', value: 'created_at' },
  { title: 'Título', value: 'title' },
  { title: 'Número de Posts', value: 'post_count' }
]

// Computed
const topics = computed(() => forumStore.topics)
const stats = computed(() => forumStore.stats)
const categories = computed(() => forumStore.categories)

const categoryOptions = computed(() => [
  ...categories.value.map(cat => ({
    title: cat.name,
    value: cat.id
  }))
])

const openTopicsCount = computed(() => 
  topics.value.filter(t => t.status === 'open').length
)

const pinnedTopicsCount = computed(() => 
  topics.value.filter(t => t.status === 'pinned').length
)

const closedTopicsCount = computed(() => 
  topics.value.filter(t => t.status === 'closed' || t.status === 'locked').length
)

// Methods
function getCategoryName(categoryId: string) {
  const category = categories.value.find(c => c.id === categoryId)
  return category?.name || 'Categoria não encontrada'
}

function getStatusColor(status: string) {
  switch (status) {
    case 'open': return 'success'
    case 'pinned': return 'warning'
    case 'closed': return 'info'
    case 'locked': return 'error'
    default: return 'grey'
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'open': return 'mdi-check-circle'
    case 'pinned': return 'mdi-pin'
    case 'closed': return 'mdi-close-circle'
    case 'locked': return 'mdi-lock'
    default: return 'mdi-help-circle'
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'open': return 'Aberto'
    case 'pinned': return 'Fixado'
    case 'closed': return 'Fechado'
    case 'locked': return 'Bloqueado'
    default: return 'Desconhecido'
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadTopics() {
  loading.value = true
  try {
    await forumStore.fetchTopics({
      category: filters.value.category || undefined,
      status: filters.value.status === 'all' ? undefined : filters.value.status,
      search: filters.value.search || undefined,
      sort: filters.value.sort
    })
  } catch (error) {
    console.error('Erro ao carregar tópicos:', error)
  } finally {
    loading.value = false
  }
}

async function createTopic() {
  creating.value = true
  try {
    await forumStore.createTopic({
      ...newTopic.value,
      tags: newTopic.value.tags ? newTopic.value.tags.split(',').map(t => t.trim()) : []
    })
    
    createTopicDialog.value = false
    newTopic.value = { title: '', category_id: '', content: '', tags: '' }
    await loadTopics()
  } catch (error) {
    console.error('Erro ao criar tópico:', error)
  } finally {
    creating.value = false
  }
}

function viewTopic(topic: ForumTopic) {
  window.open(`/forum/topics/${topic.slug}`, '_blank')
}

function editTopic(topic: ForumTopic) {
  // TODO: Implementar edição de tópico
  console.log('Editar tópico:', topic)
}

async function togglePin(topic: ForumTopic) {
  try {
    const newStatus = topic.status === 'pinned' ? 'open' : 'pinned'
    await forumStore.updateTopic(topic.slug, { status: newStatus })
    await loadTopics()
  } catch (error) {
    console.error('Erro ao alterar status do tópico:', error)
  }
}

async function toggleLock(topic: ForumTopic) {
  try {
    const newStatus = topic.status === 'locked' ? 'open' : 'locked'
    await forumStore.updateTopic(topic.slug, { status: newStatus })
    await loadTopics()
  } catch (error) {
    console.error('Erro ao alterar status do tópico:', error)
  }
}

async function deleteTopic(topic: ForumTopic) {
  if (confirm(`Tem certeza que deseja excluir o tópico "${topic.title}"?`)) {
    try {
      await forumStore.deleteTopic(topic.slug)
      await loadTopics()
    } catch (error) {
      console.error('Erro ao excluir tópico:', error)
    }
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    forumStore.fetchCategories(),
    forumStore.fetchStats(),
    loadTopics()
  ])
})
</script>

<style scoped>
.forum-topics {
  padding: 24px;
}
</style>
