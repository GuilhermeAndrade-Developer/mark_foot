<template>
  <v-container fluid>
    <!-- Header da página -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold">Categorias de Conteúdo</h1>
            <p class="text-body-1 text-medium-emphasis mt-1">
              Gerencie as categorias para organizar o conteúdo gerado pelos usuários
            </p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            Nova Categoria
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-switch
          v-model="activeOnlyFilter"
          label="Apenas categorias ativas"
          density="compact"
          @update:model-value="applyFilters"
        />
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="searchQuery"
          label="Buscar categorias..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
          @update:model-value="debounceSearch"
        />
      </v-col>
    </v-row>

    <!-- Cards de Categorias -->
    <v-row v-if="!loading">
      <v-col
        v-for="category in filteredCategories"
        :key="category.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card
          :class="{ 'opacity-50': !category.is_active }"
          elevation="2"
          hover
        >
          <v-card-title class="d-flex align-center">
            <v-icon
              :icon="category.icon"
              :color="category.is_active ? 'primary' : 'grey'"
              size="28"
              class="mr-3"
            />
            <span class="text-truncate">{{ category.name }}</span>
          </v-card-title>
          
          <v-card-text>
            <p class="text-body-2 mb-3">{{ category.description || 'Sem descrição' }}</p>
            
            <div class="d-flex align-center justify-space-between">
              <v-chip
                :color="category.is_active ? 'success' : 'error'"
                variant="tonal"
                size="small"
              >
                {{ category.is_active ? 'Ativa' : 'Inativa' }}
              </v-chip>
              
              <div class="d-flex align-center">
                <v-icon size="16" class="mr-1">mdi-file-document</v-icon>
                <span class="text-caption">{{ category.articles_count }} artigos</span>
              </div>
            </div>
          </v-card-text>
          
          <v-card-actions>
            <v-btn
              variant="text"
              size="small"
              @click="viewCategoryArticles(category)"
            >
              Ver Artigos
            </v-btn>
            
            <v-spacer />
            
            <v-btn
              icon="mdi-pencil"
              variant="text"
              size="small"
              @click="editCategory(category)"
            />
            
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              color="error"
              @click="deleteCategory(category)"
            />
          </v-card-actions>
        </v-card>
      </v-col>
      
      <!-- Card para criar nova categoria -->
      <v-col cols="12" sm="6" md="4" lg="3">
        <v-card
          variant="outlined"
          class="d-flex align-center justify-center"
          height="220"
          @click="openCreateDialog"
          style="cursor: pointer;"
        >
          <div class="text-center">
            <v-icon size="48" color="grey-lighten-1">mdi-plus</v-icon>
            <p class="mt-2 text-body-1">Nova Categoria</p>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-else class="justify-center">
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        />
        <p class="mt-4">Carregando categorias...</p>
      </v-col>
    </v-row>

    <!-- Empty State -->
    <v-row v-if="!loading && filteredCategories.length === 0" class="justify-center">
      <v-col cols="12" class="text-center py-8">
        <v-icon size="64" color="grey-lighten-1">mdi-folder-outline</v-icon>
        <h3 class="text-h6 mt-4">Nenhuma categoria encontrada</h3>
        <p class="text-body-2 text-grey mt-2">
          {{ searchQuery ? 'Tente ajustar os filtros de busca' : 'Comece criando sua primeira categoria' }}
        </p>
        <v-btn
          v-if="!searchQuery"
          color="primary"
          class="mt-4"
          @click="openCreateDialog"
        >
          Criar Categoria
        </v-btn>
      </v-col>
    </v-row>

    <!-- Dialog de Criação/Edição -->
    <v-dialog v-model="categoryDialog" max-width="500">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2">{{ editingCategory ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
          {{ editingCategory ? 'Editar Categoria' : 'Nova Categoria' }}
        </v-card-title>
        
        <v-card-text>
          <v-form ref="form" v-model="formValid">
            <v-text-field
              v-model="categoryForm.name"
              label="Nome da Categoria"
              variant="outlined"
              :rules="[rules.required]"
              class="mb-4"
            />
            
            <v-textarea
              v-model="categoryForm.description"
              label="Descrição"
              variant="outlined"
              rows="3"
              class="mb-4"
            />
            
            <v-select
              v-model="categoryForm.icon"
              :items="iconOptions"
              label="Ícone"
              variant="outlined"
              :rules="[rules.required]"
              class="mb-4"
            >
              <template #item="{ props, item }">
                <v-list-item v-bind="props">
                  <template #prepend>
                    <v-icon :icon="item.raw.value" />
                  </template>
                </v-list-item>
              </template>
              
              <template #selection="{ item }">
                <div class="d-flex align-center">
                  <v-icon :icon="item.raw.value" class="mr-2" />
                  {{ item.raw.title }}
                </div>
              </template>
            </v-select>
            
            <v-switch
              v-model="categoryForm.is_active"
              label="Categoria ativa"
              density="compact"
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="categoryDialog = false">Cancelar</v-btn>
          <v-btn
            color="primary"
            :loading="saving"
            :disabled="!formValid"
            @click="saveCategory"
          >
            {{ editingCategory ? 'Atualizar' : 'Criar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Confirmação de Exclusão -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2" color="error">mdi-delete</v-icon>
          Confirmar Exclusão
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir a categoria <strong>"{{ categoryToDelete?.name }}"</strong>?
          <br><br>
          <v-alert
            v-if="categoryToDelete?.articles_count && categoryToDelete.articles_count > 0"
            type="warning"
            variant="tonal"
            class="mt-3"
          >
            Esta categoria possui {{ categoryToDelete.articles_count }} artigo(s) associado(s).
            Os artigos precisarão ser movidos para outra categoria.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn
            color="error"
            :loading="deleting"
            @click="confirmDelete"
          >
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useContentStore } from '@/stores/content'
import type { ContentCategory } from '@/types/content'

const router = useRouter()
const contentStore = useContentStore()

// Estado local
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const categoryDialog = ref(false)
const deleteDialog = ref(false)
const categoryToDelete = ref<ContentCategory | null>(null)
const editingCategory = ref<ContentCategory | null>(null)
const formValid = ref(false)

// Filtros
const activeOnlyFilter = ref(false)
const searchQuery = ref('')

// Form
const categoryForm = ref({
  name: '',
  description: '',
  icon: 'mdi-folder',
  is_active: true
})

// Computed
const categories = computed(() => contentStore.categories || [])

const filteredCategories = computed(() => {
  const categoriesList = categories.value
  if (!Array.isArray(categoriesList)) {
    return []
  }
  
  let filtered = [...categoriesList]
  
  if (activeOnlyFilter.value) {
    filtered = filtered.filter(cat => cat.is_active)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cat => 
      cat.name.toLowerCase().includes(query) ||
      (cat.description && cat.description.toLowerCase().includes(query))
    )
  }
  
  return filtered.sort((a, b) => a.name.localeCompare(b.name))
})

// Options
const iconOptions = ref([
  { title: 'Pasta', value: 'mdi-folder' },
  { title: 'Estratégia', value: 'mdi-strategy' },
  { title: 'Dinheiro', value: 'mdi-cash-multiple' },
  { title: 'Livro', value: 'mdi-book-open-variant' },
  { title: 'Gráfico', value: 'mdi-chart-bar' },
  { title: 'Comentário', value: 'mdi-comment-text' },
  { title: 'Microfone', value: 'mdi-microphone' },
  { title: 'Troféu', value: 'mdi-trophy' },
  { title: 'Futebol', value: 'mdi-soccer' },
  { title: 'Estrela', value: 'mdi-star' },
  { title: 'Arquivo', value: 'mdi-file-document' },
  { title: 'Etiqueta', value: 'mdi-tag' }
])

// Validation rules
const rules = {
  required: (value: string) => !!value || 'Campo obrigatório'
}

// Debounce para busca
let searchTimeout: number
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // A busca é reativa via computed
  }, 300)
}

// Methods
const applyFilters = () => {
  // Os filtros são reativos via computed
}

const openCreateDialog = () => {
  editingCategory.value = null
  categoryForm.value = {
    name: '',
    description: '',
    icon: 'mdi-folder',
    is_active: true
  }
  categoryDialog.value = true
}

const editCategory = (category: ContentCategory) => {
  editingCategory.value = category
  categoryForm.value = {
    name: category.name,
    description: category.description,
    icon: category.icon,
    is_active: category.is_active
  }
  categoryDialog.value = true
}

const deleteCategory = (category: ContentCategory) => {
  categoryToDelete.value = category
  deleteDialog.value = true
}

const viewCategoryArticles = (category: ContentCategory) => {
  router.push(`/content/articles?category=${category.slug}`)
}

const saveCategory = async () => {
  saving.value = true
  try {
    if (editingCategory.value) {
      await contentStore.updateCategory(editingCategory.value.id, categoryForm.value)
    } else {
      await contentStore.createCategory(categoryForm.value)
    }
    categoryDialog.value = false
  } catch (error) {
    console.error('Erro ao salvar categoria:', error)
  } finally {
    saving.value = false
  }
}

const confirmDelete = async () => {
  if (!categoryToDelete.value) return
  
  deleting.value = true
  try {
    await contentStore.deleteCategory(categoryToDelete.value.id)
    deleteDialog.value = false
    categoryToDelete.value = null
  } catch (error) {
    console.error('Erro ao deletar categoria:', error)
  } finally {
    deleting.value = false
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    // Garantir que o array de categorias existe antes de carregar
    if (!Array.isArray(contentStore.categories)) {
      contentStore.categories = []
    }
    await contentStore.fetchCategories()
  } catch (error) {
    console.error('Erro ao carregar categorias:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.v-card:hover {
  transform: translateY(-2px);
  transition: transform 0.2s ease-in-out;
}

.opacity-50 {
  opacity: 0.7;
}
</style>
