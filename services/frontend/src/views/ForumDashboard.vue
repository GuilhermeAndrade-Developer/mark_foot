<template>
  <v-container fluid class="pa-6">
    <!-- Header do Fórum -->
    <div class="d-flex justify-space-between align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          📋 Administração do Fórum
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Gerencie categorias, tópicos e moderação do sistema de fóruns
        </p>
      </div>
      
      <div class="d-flex gap-3">
        <v-btn
          color="primary"
          variant="elevated"
          prepend-icon="mdi-plus"
          @click="openCreateCategoryDialog"
        >
          Nova Categoria
        </v-btn>
        <v-btn
          color="success"
          variant="outlined"
          prepend-icon="mdi-chart-line"
          @click="refreshStats"
          :loading="statsLoading"
        >
          Atualizar Stats
        </v-btn>
      </div>
    </div>

    <!-- Cards de Estatísticas -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="primary" variant="tonal">
          <v-card-text>
            <div class="text-h3 font-weight-bold text-primary">
              {{ totalCategories }}
            </div>
            <div class="text-subtitle-1 text-medium-emphasis">
              Categorias Ativas
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="success" variant="tonal">
          <v-card-text>
            <div class="text-h3 font-weight-bold text-success">
              {{ totalTopics }}
            </div>
            <div class="text-subtitle-1 text-medium-emphasis">
              Total de Tópicos
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="info" variant="tonal">
          <v-card-text>
            <div class="text-h3 font-weight-bold text-info">
              {{ totalPosts }}
            </div>
            <div class="text-subtitle-1 text-medium-emphasis">
              Total de Posts
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4 text-center" color="warning" variant="tonal">
          <v-card-text>
            <div class="text-h3 font-weight-bold text-warning">
              {{ totalUsers }}
            </div>
            <div class="text-subtitle-1 text-medium-emphasis">
              Usuários Ativos
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Ações Rápidas e Informações -->
    <v-row class="mb-6">
      <v-col cols="12" md="8">
        <!-- Categorias por Tipo -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-folder-multiple</v-icon>
            Categorias por Tipo
            <v-spacer />
            <v-btn
              size="small"
              variant="text"
              append-icon="mdi-chevron-right"
              @click="$router.push('/forum/categories')"
            >
              Ver Todas
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <div v-if="categoriesLoading" class="text-center py-4">
              <v-progress-circular indeterminate />
            </div>
            
            <div v-else>
              <v-row>
                <v-col 
                  v-for="(categoryList, type) in categoriesByType" 
                  :key="type"
                  cols="12" 
                  sm="6" 
                  md="4"
                >
                  <v-card variant="outlined" class="pa-3">
                    <div class="text-subtitle-1 font-weight-medium mb-2">
                      {{ getCategoryTypeLabel(type) }}
                    </div>
                    <div class="text-h6 text-primary font-weight-bold">
                      {{ categoryList.length }}
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      categorias
                    </div>
                  </v-card>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

        <!-- Atividade Recente -->
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-clock-outline</v-icon>
            Atividade Recente
          </v-card-title>
          
          <v-card-text>
            <div v-if="statsLoading" class="text-center py-4">
              <v-progress-circular indeterminate />
            </div>
            
            <div v-else-if="stats?.recent_activity?.length">
              <v-list>
                <v-list-item
                  v-for="activity in stats.recent_activity"
                  :key="activity.id"
                  class="px-0"
                >
                  <template #prepend>
                    <v-avatar size="32" color="primary">
                      <span class="text-caption">{{ activity.author.charAt(0).toUpperCase() }}</span>
                    </v-avatar>
                  </template>
                  
                  <v-list-item-title class="text-body-2">
                    <strong>{{ activity.author }}</strong> postou em
                    <router-link 
                      :to="`/forum/topics/${activity.topic_slug}`"
                      class="text-decoration-none"
                    >
                      {{ activity.topic_title }}
                    </router-link>
                  </v-list-item-title>
                  
                  <v-list-item-subtitle>
                    {{ formatDate(activity.created_at) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </div>
            
            <div v-else class="text-center py-4 text-medium-emphasis">
              Nenhuma atividade recente
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <!-- Ações Rápidas -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
            Ações Rápidas
          </v-card-title>
          
          <v-card-text>
            <v-list>
              <v-list-item
                prepend-icon="mdi-folder-plus"
                title="Criar Categoria"
                subtitle="Adicionar nova categoria de discussão"
                @click="openCreateCategoryDialog"
              />
              
              <v-list-item
                prepend-icon="mdi-post"
                title="Gerenciar Tópicos"
                subtitle="Ver e moderar tópicos"
                @click="$router.push('/forum/topics')"
              />
              
              <v-list-item
                prepend-icon="mdi-flag"
                title="Moderação"
                subtitle="Posts reportados e pendências"
                @click="$router.push('/forum/moderation')"
              />
              
              <v-list-item
                prepend-icon="mdi-chart-bar"
                title="Relatórios"
                subtitle="Estatísticas detalhadas"
                @click="$router.push('/forum/reports')"
              />
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Categorias Mais Ativas -->
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-fire</v-icon>
            Categorias Mais Ativas
          </v-card-title>
          
          <v-card-text>
            <div v-if="categoriesLoading" class="text-center py-4">
              <v-progress-circular indeterminate />
            </div>
            
            <div v-else>
              <v-list>
                <v-list-item
                  v-for="category in categoriesWithStats.slice(0, 5)"
                  :key="category.id"
                  class="px-0"
                >
                  <template #prepend>
                    <v-chip
                      size="small"
                      :color="getCategoryTypeColor(category.category_type)"
                      variant="dot"
                    >
                      {{ getCategoryTypeLabel(category.category_type) }}
                    </v-chip>
                  </template>
                  
                  <v-list-item-title class="text-body-2">
                    {{ category.name }}
                  </v-list-item-title>
                  
                  <v-list-item-subtitle>
                    {{ category.topic_count }} tópicos, {{ category.post_count }} posts
                  </v-list-item-subtitle>
                  
                  <template #append>
                    <v-btn
                      size="small"
                      variant="text"
                      icon="mdi-chevron-right"
                      @click="$router.push(`/forum/categories/${category.slug}`)"
                    />
                  </template>
                </v-list-item>
              </v-list>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog para Criar Categoria -->
    <v-dialog v-model="createCategoryDialog" max-width="600">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-folder-plus</v-icon>
          Nova Categoria
        </v-card-title>
        
        <v-card-text>
          <v-form ref="categoryForm" @submit.prevent="createCategory">
            <v-text-field
              v-model="newCategory.name"
              label="Nome da Categoria"
              variant="outlined"
              :rules="[v => !!v || 'Nome é obrigatório']"
              class="mb-3"
            />
            
            <v-textarea
              v-model="newCategory.description"
              label="Descrição"
              variant="outlined"
              rows="3"
              class="mb-3"
            />
            
            <v-select
              v-model="newCategory.category_type"
              label="Tipo de Categoria"
              variant="outlined"
              :items="categoryTypes"
              item-title="label"
              item-value="value"
              class="mb-3"
            />
            
            <v-text-field
              v-model="newCategory.slug"
              label="Slug (URL amigável)"
              variant="outlined"
              placeholder="Gerado automaticamente"
              class="mb-3"
            />
            
            <v-switch
              v-model="newCategory.is_moderated"
              label="Categoria Moderada"
              color="primary"
              hide-details
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="createCategoryDialog = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :loading="loading"
            @click="createCategory"
          >
            Criar Categoria
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useForumStore } from '@/stores/forum'
import forumApi from '@/services/forumApi'

const router = useRouter()
const forumStore = useForumStore()

// Reactive data
const createCategoryDialog = ref(false)
const categoryForm = ref()

const newCategory = ref({
  name: '',
  description: '',
  category_type: 'general',
  slug: '',
  is_moderated: false
})

const categoryTypes = [
  { label: 'Discussão Geral', value: 'general' },
  { label: 'Time', value: 'team' },
  { label: 'Competição', value: 'competition' },
  { label: 'Notícias', value: 'news' },
  { label: 'Análises', value: 'analysis' }
]

// Computed properties from store
const categories = computed(() => forumStore.categories)
const categoriesByType = computed(() => forumStore.categoriesByType)
const categoriesWithStats = computed(() => forumStore.categoriesWithStats)
const stats = computed(() => forumStore.stats)
const loading = computed(() => forumStore.loading)
const categoriesLoading = computed(() => forumStore.categoriesLoading)
const statsLoading = computed(() => forumStore.statsLoading)

const totalCategories = computed(() => forumStore.totalCategories)
const totalTopics = computed(() => forumStore.totalTopics)
const totalPosts = computed(() => forumStore.totalPosts)
const totalUsers = computed(() => forumStore.totalUsers)

// Methods
async function loadData() {
  try {
    await Promise.all([
      forumStore.fetchCategories(),
      forumStore.fetchStats()
    ])
  } catch (error) {
    console.error('Erro ao carregar dados:', error)
  }
}

async function refreshStats() {
  try {
    await forumStore.fetchStats()
  } catch (error) {
    console.error('Erro ao atualizar estatísticas:', error)
  }
}

function openCreateCategoryDialog() {
  newCategory.value = {
    name: '',
    description: '',
    category_type: 'general',
    slug: '',
    is_moderated: false
  }
  createCategoryDialog.value = true
}

async function createCategory() {
  if (!categoryForm.value?.validate()) return
  
  try {
    // Gerar slug se não fornecido
    if (!newCategory.value.slug) {
      newCategory.value.slug = newCategory.value.name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '')
    }
    
    await forumStore.createCategory(newCategory.value)
    createCategoryDialog.value = false
    
    // Mostrar notificação de sucesso (implementar depois)
    console.log('Categoria criada com sucesso!')
  } catch (error) {
    console.error('Erro ao criar categoria:', error)
  }
}

function getCategoryTypeLabel(type: string): string {
  return forumApi.getCategoryTypeLabel(type)
}

function getCategoryTypeColor(type: string): string {
  const colors = {
    'general': 'primary',
    'team': 'success',
    'competition': 'info',
    'news': 'warning',
    'analysis': 'purple'
  }
  return colors[type as keyof typeof colors] || 'grey'
}

function formatDate(dateString: string): string {
  return forumApi.formatDate(dateString)
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
}

.text-decoration-none {
  text-decoration: none !important;
}

.text-decoration-none:hover {
  text-decoration: underline !important;
}
</style>
