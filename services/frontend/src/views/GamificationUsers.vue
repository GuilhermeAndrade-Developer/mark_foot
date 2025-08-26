<template>
  <div class="gamification-users">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card class="gradient-primary pa-6">
          <div class="text-white">
            <h1 class="text-h4 font-weight-bold mb-2">
              👥 Gestão de Usuários
            </h1>
            <p class="text-h6 mb-4 opacity-90">
              Monitore pontuações, níveis e engajamento dos usuários
            </p>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- User Stats Overview -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="primary" class="mb-2">mdi-account-group</v-icon>
          <div class="text-h4 font-weight-bold">{{ totalUsers }}</div>
          <div class="text-body-2 text-medium-emphasis">Total de Usuários</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="success" class="mb-2">mdi-account-check</v-icon>
          <div class="text-h4 font-weight-bold">{{ activeUsers }}</div>
          <div class="text-body-2 text-medium-emphasis">Usuários Ativos</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="warning" class="mb-2">mdi-trending-up</v-icon>
          <div class="text-h4 font-weight-bold">{{ avgLevel.toFixed(1) }}</div>
          <div class="text-body-2 text-medium-emphasis">Nível Médio</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card class="pa-4 text-center">
          <v-icon size="48" color="info" class="mb-2">mdi-star</v-icon>
          <div class="text-h4 font-weight-bold">{{ totalPoints.toLocaleString() }}</div>
          <div class="text-body-2 text-medium-emphasis">Total de Pontos</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters and Search -->
    <v-row class="mb-4">
      <v-col cols="12" md="4">
        <v-text-field
          v-model="searchQuery"
          prepend-inner-icon="mdi-magnify"
          label="Buscar usuários"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="levelFilter"
          :items="levelOptions"
          label="Filtrar por nível"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="sortBy"
          :items="sortOptions"
          label="Ordenar por"
          variant="outlined"
          density="compact"
        />
      </v-col>
      <v-col cols="12" md="2">
        <v-btn 
          color="primary" 
          variant="outlined" 
          @click="exportUsers"
          block
        >
          <v-icon left>mdi-download</v-icon>
          Exportar
        </v-btn>
      </v-col>
    </v-row>

    <!-- Users Table -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-account-multiple</v-icon>
        Lista de Usuários
        <v-spacer />
        <v-chip :color="getStatusColor()" variant="outlined">
          {{ filteredUsers.length }} usuários encontrados
        </v-chip>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="filteredUsers"
        :loading="loading"
        :items-per-page="itemsPerPage"
        class="elevation-0"
      >
        <template v-slot:item.user.username="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" color="primary" class="mr-3">
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

        <template v-slot:item.level="{ item }">
          <v-chip 
            :color="getLevelColor(item.level)" 
            size="small"
            variant="tonal"
          >
            Level {{ item.level }}
          </v-chip>
        </template>

        <template v-slot:item.total_points="{ item }">
          <div class="d-flex align-center">
            <v-icon size="16" color="warning" class="mr-1">mdi-star</v-icon>
            <span class="font-weight-bold">{{ item.total_points.toLocaleString() }}</span>
          </div>
        </template>

        <template v-slot:item.prediction_streak="{ item }">
          <div class="d-flex align-center">
            <v-icon size="16" color="success" class="mr-1">mdi-fire</v-icon>
            <span>{{ item.prediction_streak }}</span>
          </div>
        </template>

        <template v-slot:item.last_login_date="{ item }">
          <span v-if="item.last_login_date" class="text-body-2">
            {{ formatDate(item.last_login_date) }}
          </span>
          <span v-else class="text-medium-emphasis">Nunca</span>
        </template>

        <template v-slot:item.actions="{ item }">
          <div class="d-flex gap-2">
            <v-btn 
              size="small" 
              variant="outlined" 
              color="primary"
              @click="viewUserDetails(item)"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            <v-btn 
              size="small" 
              variant="outlined" 
              color="success"
              @click="addPointsToUser(item)"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
            <v-btn 
              size="small" 
              variant="outlined" 
              color="warning"
              @click="awardBadgeToUser(item)"
            >
              <v-icon>mdi-medal</v-icon>
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- User Details Dialog -->
    <v-dialog v-model="showUserDialog" max-width="800">
      <v-card v-if="selectedUser">
        <v-card-title class="d-flex align-center">
          <v-avatar size="40" color="primary" class="mr-3">
            <span class="text-white font-weight-bold">
              {{ selectedUser.user.username.charAt(0).toUpperCase() }}
            </span>
          </v-avatar>
          Detalhes do Usuário: {{ selectedUser.user.username }}
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-4">
                <h3 class="text-h6 mb-3">Informações Gerais</h3>
                <div class="mb-2">
                  <strong>Email:</strong> {{ selectedUser.user.email }}
                </div>
                <div class="mb-2">
                  <strong>Level:</strong> {{ selectedUser.level }}
                </div>
                <div class="mb-2">
                  <strong>Total de Pontos:</strong> {{ selectedUser.total_points.toLocaleString() }}
                </div>
                <div class="mb-2">
                  <strong>XP:</strong> {{ selectedUser.experience_points }}
                </div>
                <div class="mb-2">
                  <strong>Sequência de Predições:</strong> {{ selectedUser.prediction_streak }}
                </div>
                <div class="mb-2">
                  <strong>Sequência de Login:</strong> {{ selectedUser.login_streak }}
                </div>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="pa-4">
                <h3 class="text-h6 mb-3">Estatísticas</h3>
                <div class="mb-2">
                  <strong>Último Login:</strong> 
                  {{ selectedUser.last_login_date ? formatDate(selectedUser.last_login_date) : 'Nunca' }}
                </div>
                <div class="mb-2">
                  <strong>Membro desde:</strong> {{ formatDate(selectedUser.created_at) }}
                </div>
                <div class="mb-2">
                  <strong>Perfil Público:</strong> 
                  <v-chip size="small" :color="selectedUser.is_public_profile ? 'success' : 'error'">
                    {{ selectedUser.is_public_profile ? 'Sim' : 'Não' }}
                  </v-chip>
                </div>
                <div class="mb-2">
                  <strong>Aceita Amizades:</strong> 
                  <v-chip size="small" :color="selectedUser.allow_friend_requests ? 'success' : 'error'">
                    {{ selectedUser.allow_friend_requests ? 'Sim' : 'Não' }}
                  </v-chip>
                </div>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showUserDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add Points Dialog -->
    <v-dialog v-model="showAddPointsDialog" max-width="400">
      <v-card>
        <v-card-title>Adicionar Pontos</v-card-title>
        <v-card-text>
          <v-text-field
            v-model.number="pointsToAdd"
            label="Quantidade de Pontos"
            type="number"
            min="1"
            max="10000"
            required
          />
          <v-text-field
            v-model="pointsReason"
            label="Motivo"
            placeholder="Ex: Bônus administrativo"
            required
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAddPointsDialog = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            :loading="adding"
            @click="confirmAddPoints"
          >
            Adicionar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Award Badge Dialog -->
    <v-dialog v-model="showAwardBadgeDialog" max-width="400">
      <v-card>
        <v-card-title>Conceder Badge</v-card-title>
        <v-card-text>
          <v-select
            v-model="selectedBadgeId"
            :items="availableBadges"
            item-title="name"
            item-value="id"
            label="Selecionar Badge"
            required
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAwardBadgeDialog = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            :loading="awarding"
            @click="confirmAwardBadge"
          >
            Conceder
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useGamificationStore } from '@/stores/gamification'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const gamificationStore = useGamificationStore()

// Reactive data
const loading = ref(false)
const adding = ref(false)
const awarding = ref(false)
const itemsPerPage = ref(10)

// Search and filters
const searchQuery = ref('')
const levelFilter = ref(null)
const sortBy = ref('total_points')

// Dialog states
const showUserDialog = ref(false)
const showAddPointsDialog = ref(false)
const showAwardBadgeDialog = ref(false)

// Selected items
const selectedUser = ref(null)
const selectedUserForPoints = ref(null)
const selectedUserForBadge = ref(null)

// Form data
const pointsToAdd = ref(100)
const pointsReason = ref('')
const selectedBadgeId = ref(null)

// Data
const users = ref([])
const badges = ref([])

// Computed properties
const totalUsers = computed(() => users.value.length)
const activeUsers = computed(() => users.value.filter(u => u.last_login_date).length)
const avgLevel = computed(() => {
  if (users.value.length === 0) return 0
  return users.value.reduce((sum, user) => sum + user.level, 0) / users.value.length
})
const totalPoints = computed(() => users.value.reduce((sum, user) => sum + user.total_points, 0))

const filteredUsers = computed(() => {
  let filtered = [...users.value]
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.user.username.toLowerCase().includes(query) ||
      user.user.email.toLowerCase().includes(query)
    )
  }
  
  // Level filter
  if (levelFilter.value) {
    filtered = filtered.filter(user => user.level === levelFilter.value)
  }
  
  // Sort
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'total_points':
        return b.total_points - a.total_points
      case 'level':
        return b.level - a.level
      case 'username':
        return a.user.username.localeCompare(b.user.username)
      case 'last_login':
        return new Date(b.last_login_date || 0).getTime() - new Date(a.last_login_date || 0).getTime()
      default:
        return 0
    }
  })
  
  return filtered
})

const availableBadges = computed(() => badges.value)

// Table configuration
const headers = [
  { title: 'Usuário', key: 'user.username', sortable: false },
  { title: 'Nível', key: 'level', sortable: true },
  { title: 'Pontos', key: 'total_points', sortable: true },
  { title: 'Sequência', key: 'prediction_streak', sortable: true },
  { title: 'Último Login', key: 'last_login_date', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false }
]

const levelOptions = computed(() => {
  const levels = [...new Set(users.value.map(u => u.level))].sort((a, b) => a - b)
  return levels.map(level => ({ title: `Level ${level}`, value: level }))
})

const sortOptions = [
  { title: 'Pontos (maior)', value: 'total_points' },
  { title: 'Nível (maior)', value: 'level' },
  { title: 'Nome (A-Z)', value: 'username' },
  { title: 'Último Login', value: 'last_login' }
]

// Methods
const loadUsers = async () => {
  loading.value = true
  try {
    users.value = await gamificationStore.getUserProfiles()
  } catch (error) {
    console.error('Error loading users:', error)
  } finally {
    loading.value = false
  }
}

const loadBadges = async () => {
  try {
    badges.value = await gamificationStore.getBadges()
  } catch (error) {
    console.error('Error loading badges:', error)
  }
}

const viewUserDetails = (user: any) => {
  selectedUser.value = user
  showUserDialog.value = true
}

const addPointsToUser = (user: any) => {
  selectedUserForPoints.value = user
  pointsToAdd.value = 100
  pointsReason.value = ''
  showAddPointsDialog.value = true
}

const awardBadgeToUser = (user: any) => {
  selectedUserForBadge.value = user
  selectedBadgeId.value = null
  showAwardBadgeDialog.value = true
}

const confirmAddPoints = async () => {
  adding.value = true
  try {
    // This would be an admin API call
    console.log(`Adding ${pointsToAdd.value} points to ${selectedUserForPoints.value.user.username}`)
    showAddPointsDialog.value = false
    await loadUsers()
  } catch (error) {
    console.error('Error adding points:', error)
  } finally {
    adding.value = false
  }
}

const confirmAwardBadge = async () => {
  awarding.value = true
  try {
    // This would be an admin API call
    console.log(`Awarding badge ${selectedBadgeId.value} to ${selectedUserForBadge.value.user.username}`)
    showAwardBadgeDialog.value = false
    await loadUsers()
  } catch (error) {
    console.error('Error awarding badge:', error)
  } finally {
    awarding.value = false
  }
}

const exportUsers = () => {
  // Export functionality
  const csv = filteredUsers.value.map(user => 
    `${user.user.username},${user.user.email},${user.level},${user.total_points},${user.prediction_streak}`
  ).join('\n')
  
  const blob = new Blob(['Username,Email,Level,Points,Streak\n' + csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'users_gamification.csv'
  a.click()
  URL.revokeObjectURL(url)
}

// Utility methods
const getLevelColor = (level: number) => {
  if (level >= 10) return 'purple'
  if (level >= 5) return 'orange'
  if (level >= 3) return 'success'
  return 'primary'
}

const getStatusColor = () => {
  return filteredUsers.value.length > 0 ? 'success' : 'warning'
}

const formatDate = (dateString: string) => {
  return format(new Date(dateString), "dd/MM/yyyy", { locale: ptBR })
}

// Lifecycle
onMounted(async () => {
  await Promise.all([loadUsers(), loadBadges()])
})
</script>

<style scoped>
.gradient-primary {
  background: linear-gradient(135deg, #1976d2, #42a5f5);
}

.gamification-users {
  padding: 0;
}

.v-data-table {
  background: transparent;
}
</style>
