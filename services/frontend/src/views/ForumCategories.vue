<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold mb-2">Categorias do Fórum</h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              Gerencie todas as categorias e suas configurações
            </p>
          </div>
          <v-btn
            color="primary"
            size="large"
            @click="openCreateDialog"
            prepend-icon="mdi-plus"
          >
            Nova Categoria
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="primary" variant="tonal">
          <v-icon size="40" class="mb-2">mdi-forum</v-icon>
          <div class="text-h5 font-weight-bold">{{ categories.length }}</div>
          <div class="text-caption">Total de Categorias</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="success" variant="tonal">
          <v-icon size="40" class="mb-2">mdi-check-circle</v-icon>
          <div class="text-h5 font-weight-bold">{{ activeCategories }}</div>
          <div class="text-caption">Ativas</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="info" variant="tonal">
          <v-icon size="40" class="mb-2">mdi-account-group</v-icon>
          <div class="text-h5 font-weight-bold">{{ totalTopics }}</div>
          <div class="text-caption">Total de Tópicos</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="warning" variant="tonal">
          <v-icon size="40" class="mb-2">mdi-message</v-icon>
          <div class="text-h5 font-weight-bold">{{ totalPosts }}</div>
          <div class="text-caption">Total de Posts</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters and Search -->
    <v-row class="mb-4">
      <v-col cols="12" md="4">
        <v-text-field
          v-model="searchQuery"
          prepend-inner-icon="mdi-magnify"
          label="Buscar categorias..."
          clearable
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="selectedType"
          :items="categoryTypes"
          label="Tipo"
          clearable
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="selectedStatus"
          :items="statusOptions"
          label="Status"
          clearable
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" md="2">
        <v-btn
          @click="clearFilters"
          variant="outlined"
          block
          prepend-icon="mdi-filter-off"
        >
          Limpar
        </v-btn>
      </v-col>
    </v-row>

    <!-- Categories Table -->
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <span>Categorias ({{ filteredCategories.length }})</span>
        <div class="d-flex gap-2">
          <v-btn-toggle v-model="viewMode" mandatory>
            <v-btn value="table" icon="mdi-table" size="small" />
            <v-btn value="grid" icon="mdi-grid" size="small" />
          </v-btn-toggle>
        </div>
      </v-card-title>

      <!-- Table View -->
      <template v-if="viewMode === 'table'">
        <v-data-table
          :headers="headers"
          :items="filteredCategories"
          :search="searchQuery"
          :items-per-page="itemsPerPage"
          :loading="loading"
          class="elevation-0"
        >
          <template #item.name="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="32" class="mr-3" :color="item.color || 'primary'">
                <v-icon :icon="item.icon || 'mdi-forum'" color="white" />
              </v-avatar>
              <div>
                <div class="font-weight-medium">{{ item.name }}</div>
                <div class="text-caption text-medium-emphasis">{{ item.slug }}</div>
              </div>
            </div>
          </template>

          <template #item.type="{ item }">
            <v-chip
              :color="getTypeColor(item.type)"
              size="small"
              variant="tonal"
            >
              {{ getTypeLabel(item.type) }}
            </v-chip>
          </template>

          <template #item.is_active="{ item }">
            <v-chip
              :color="item.is_active ? 'success' : 'error'"
              size="small"
              variant="tonal"
            >
              <v-icon
                :icon="item.is_active ? 'mdi-check' : 'mdi-close'"
                start
              />
              {{ item.is_active ? 'Ativa' : 'Inativa' }}
            </v-chip>
          </template>

          <template #item.topics_count="{ item }">
            <div class="text-center">
              <v-chip color="info" size="small" variant="outlined">
                {{ item.topics_count || 0 }}
              </v-chip>
            </div>
          </template>

          <template #item.posts_count="{ item }">
            <div class="text-center">
              <v-chip color="warning" size="small" variant="outlined">
                {{ item.posts_count || 0 }}
              </v-chip>
            </div>
          </template>

          <template #item.created_at="{ item }">
            <span class="text-caption">
              {{ formatDate(item.created_at) }}
            </span>
          </template>

          <template #item.actions="{ item }">
            <div class="d-flex gap-1">
              <v-btn
                icon="mdi-eye"
                size="small"
                variant="text"
                @click="viewCategory(item)"
                title="Visualizar"
              />
              <v-btn
                icon="mdi-pencil"
                size="small"
                variant="text"
                @click="editCategory(item)"
                title="Editar"
              />
              <v-btn
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="confirmDelete(item)"
                title="Excluir"
              />
            </div>
          </template>
        </v-data-table>
      </template>

      <!-- Grid View -->
      <template v-else>
        <v-container>
          <v-row>
            <v-col
              v-for="category in filteredCategories"
              :key="category.id"
              cols="12"
              sm="6"
              md="4"
              lg="3"
            >
              <v-card
                class="h-100"
                :style="{ borderTop: `4px solid ${category.color || '#1976d2'}` }"
                hover
              >
                <v-card-text class="pb-2">
                  <div class="d-flex align-center mb-3">
                    <v-avatar
                      size="40"
                      :color="category.color || 'primary'"
                      class="mr-3"
                    >
                      <v-icon :icon="category.icon || 'mdi-forum'" color="white" />
                    </v-avatar>
                    <div class="flex-grow-1">
                      <div class="font-weight-medium">{{ category.name }}</div>
                      <div class="text-caption text-medium-emphasis">
                        {{ category.slug }}
                      </div>
                    </div>
                  </div>

                  <p class="text-body-2 mb-3" style="min-height: 60px;">
                    {{ category.description || 'Sem descrição' }}
                  </p>

                  <div class="d-flex justify-space-between align-center mb-2">
                    <v-chip
                      :color="getTypeColor(category.type)"
                      size="small"
                      variant="tonal"
                    >
                      {{ getTypeLabel(category.type) }}
                    </v-chip>
                    <v-chip
                      :color="category.is_active ? 'success' : 'error'"
                      size="small"
                      variant="tonal"
                    >
                      {{ category.is_active ? 'Ativa' : 'Inativa' }}
                    </v-chip>
                  </div>

                  <div class="d-flex justify-space-between text-caption text-medium-emphasis">
                    <span>{{ category.topics_count || 0 }} tópicos</span>
                    <span>{{ category.posts_count || 0 }} posts</span>
                  </div>
                </v-card-text>

                <v-card-actions>
                  <v-btn
                    size="small"
                    variant="text"
                    @click="viewCategory(category)"
                  >
                    Visualizar
                  </v-btn>
                  <v-btn
                    size="small"
                    variant="text"
                    @click="editCategory(category)"
                  >
                    Editar
                  </v-btn>
                  <v-spacer />
                  <v-btn
                    size="small"
                    variant="text"
                    color="error"
                    icon="mdi-delete"
                    @click="confirmDelete(category)"
                  />
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </template>
    </v-card>

    <!-- Create/Edit Category Dialog -->
    <v-dialog v-model="categoryDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">
            {{ editingCategory ? 'Editar Categoria' : 'Nova Categoria' }}
          </span>
        </v-card-title>

        <v-card-text>
          <v-form ref="categoryForm" v-model="formValid">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="categoryForm.name"
                  label="Nome da Categoria"
                  :rules="[v => !!v || 'Nome é obrigatório']"
                  required
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="categoryForm.type"
                  :items="categoryTypes"
                  label="Tipo"
                  :rules="[v => !!v || 'Tipo é obrigatório']"
                  required
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="categoryForm.slug"
                  label="Slug (URL amigável)"
                  hint="Será gerado automaticamente se não informado"
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="categoryForm.description"
                  label="Descrição"
                  rows="3"
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="categoryForm.icon"
                  label="Ícone (Material Design Icons)"
                  placeholder="Ex: mdi-soccer"
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="categoryForm.color"
                  label="Cor"
                  type="color"
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="categoryForm.position"
                  label="Posição"
                  type="number"
                  hint="Ordem de exibição"
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-switch
                  v-model="categoryForm.is_active"
                  label="Categoria ativa"
                  color="success"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            text="Cancelar"
            variant="text"
            @click="closeCategoryDialog"
          />
          <v-btn
            text="Salvar"
            color="primary"
            :loading="saving"
            :disabled="!formValid"
            @click="saveCategory"
          />
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Confirmar Exclusão</v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir a categoria "{{ categoryToDelete?.name }}"?
          Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text="Cancelar" variant="text" @click="deleteDialog = false" />
          <v-btn
            text="Excluir"
            color="error"
            :loading="deleting"
            @click="deleteCategory"
          />
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useForumStore } from '@/stores/forum'
import type { ForumCategory } from '@/types/forum'

// Store
const forumStore = useForumStore()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const searchQuery = ref('')
const selectedType = ref('')
const selectedStatus = ref('')
const viewMode = ref('table')
const itemsPerPage = ref(25)

// Dialog states
const categoryDialog = ref(false)
const deleteDialog = ref(false)
const editingCategory = ref<ForumCategory | null>(null)
const categoryToDelete = ref<ForumCategory | null>(null)

// Form
const formValid = ref(false)
const categoryForm = ref({
  name: '',
  slug: '',
  description: '',
  type: 'general',
  icon: 'mdi-forum',
  color: '#1976d2',
  position: 0,
  is_active: true
})

// Table headers
const headers = [
  { title: 'Categoria', key: 'name', sortable: true },
  { title: 'Tipo', key: 'type', sortable: true, width: '120px' },
  { title: 'Status', key: 'is_active', sortable: true, width: '100px' },
  { title: 'Tópicos', key: 'topics_count', sortable: true, width: '100px', align: 'center' },
  { title: 'Posts', key: 'posts_count', sortable: true, width: '100px', align: 'center' },
  { title: 'Criado em', key: 'created_at', sortable: true, width: '140px' },
  { title: 'Ações', key: 'actions', sortable: false, width: '120px', align: 'center' }
]

// Options
const categoryTypes = [
  { title: 'Geral', value: 'general' },
  { title: 'Competição', value: 'competition' },
  { title: 'Time', value: 'team' },
  { title: 'Jogador', value: 'player' },
  { title: 'Notícias', value: 'news' },
  { title: 'Discussão', value: 'discussion' }
]

const statusOptions = [
  { title: 'Ativa', value: true },
  { title: 'Inativa', value: false }
]

// Computed
const categories = computed(() => forumStore.categories)

const filteredCategories = computed(() => {
  let filtered = [...categories.value]

  if (selectedType.value) {
    filtered = filtered.filter(cat => cat.type === selectedType.value)
  }

  if (selectedStatus.value !== '') {
    filtered = filtered.filter(cat => cat.is_active === selectedStatus.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cat =>
      cat.name.toLowerCase().includes(query) ||
      cat.description?.toLowerCase().includes(query) ||
      cat.slug.toLowerCase().includes(query)
    )
  }

  return filtered
})

const activeCategories = computed(() => 
  categories.value.filter(cat => cat.is_active).length
)

const totalTopics = computed(() => 
  categories.value.reduce((sum, cat) => sum + (cat.topics_count || 0), 0)
)

const totalPosts = computed(() => 
  categories.value.reduce((sum, cat) => sum + (cat.posts_count || 0), 0)
)

// Methods
const loadCategories = async () => {
  loading.value = true
  try {
    await forumStore.fetchCategories()
  } catch (error) {
    console.error('Erro ao carregar categorias:', error)
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  editingCategory.value = null
  categoryForm.value = {
    name: '',
    slug: '',
    description: '',
    type: 'general',
    icon: 'mdi-forum',
    color: '#1976d2',
    position: categories.value.length,
    is_active: true
  }
  categoryDialog.value = true
}

const editCategory = (category: ForumCategory) => {
  editingCategory.value = category
  categoryForm.value = {
    name: category.name,
    slug: category.slug,
    description: category.description || '',
    type: category.type,
    icon: category.icon || 'mdi-forum',
    color: category.color || '#1976d2',
    position: category.position || 0,
    is_active: category.is_active
  }
  categoryDialog.value = true
}

const viewCategory = (category: ForumCategory) => {
  // Navigate to category view or show details
  console.log('Visualizar categoria:', category)
}

const saveCategory = async () => {
  if (!formValid.value) return

  saving.value = true
  try {
    if (editingCategory.value) {
      // Update existing category
      console.log('Atualizar categoria:', categoryForm.value)
    } else {
      // Create new category
      console.log('Criar nova categoria:', categoryForm.value)
    }
    closeCategoryDialog()
    await loadCategories()
  } catch (error) {
    console.error('Erro ao salvar categoria:', error)
  } finally {
    saving.value = false
  }
}

const confirmDelete = (category: ForumCategory) => {
  categoryToDelete.value = category
  deleteDialog.value = true
}

const deleteCategory = async () => {
  if (!categoryToDelete.value) return

  deleting.value = true
  try {
    console.log('Excluir categoria:', categoryToDelete.value)
    deleteDialog.value = false
    categoryToDelete.value = null
    await loadCategories()
  } catch (error) {
    console.error('Erro ao excluir categoria:', error)
  } finally {
    deleting.value = false
  }
}

const closeCategoryDialog = () => {
  categoryDialog.value = false
  editingCategory.value = null
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedType.value = ''
  selectedStatus.value = ''
}

const getTypeColor = (type: string) => {
  const colors: { [key: string]: string } = {
    general: 'blue',
    competition: 'green',
    team: 'orange',
    player: 'purple',
    news: 'red',
    discussion: 'teal'
  }
  return colors[type] || 'grey'
}

const getTypeLabel = (type: string) => {
  const labels: { [key: string]: string } = {
    general: 'Geral',
    competition: 'Competição',
    team: 'Time',
    player: 'Jogador',
    news: 'Notícias',
    discussion: 'Discussão'
  }
  return labels[type] || type
}

const formatDate = (dateString: string) => {
  try {
    return new Date(dateString).toLocaleDateString('pt-BR')
  } catch {
    return 'Data inválida'
  }
}

// Lifecycle
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.v-data-table {
  background: transparent;
}
</style>
