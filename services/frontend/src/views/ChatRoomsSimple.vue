<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-forum</v-icon>
          Gerenciar Salas de Chat
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Administre todas as salas de chat da plataforma
        </p>
      </v-col>
    </v-row>

    <!-- Action Buttons -->
    <v-row class="mb-4">
      <v-col>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="openCreateDialog"
        >
          Nova Sala
        </v-btn>
        
        <v-btn
          color="success"
          prepend-icon="mdi-refresh"
          class="ml-2"
          @click="loadRooms"
        >
          Atualizar
        </v-btn>
        
        <v-btn
          color="orange"
          prepend-icon="mdi-soccer"
          class="ml-2"
          @click="createMatchRooms"
        >
          Criar Salas para Partidas
        </v-btn>
      </v-col>
    </v-row>

    <!-- Rooms List -->
    <v-row>
      <v-col
        v-for="room in rooms"
        :key="room.id"
        cols="12"
        md="6"
        lg="4"
      >
        <v-card elevation="2" class="h-100">
          <v-card-title class="d-flex align-center">
            <v-avatar
              :color="getRoomTypeColor(room.room_type)"
              size="32"
              class="mr-3"
            >
              <v-icon color="white" size="16">
                {{ getRoomTypeIcon(room.room_type) }}
              </v-icon>
            </v-avatar>
            <div class="flex-grow-1">
              <div class="font-weight-medium">{{ room.name }}</div>
              <div class="text-caption text-medium-emphasis">{{ room.description }}</div>
            </div>
          </v-card-title>
          
          <v-card-text>
            <v-row dense>
              <v-col cols="6">
                <v-chip
                  :color="getRoomTypeColor(room.room_type)"
                  size="small"
                  variant="tonal"
                >
                  {{ getRoomTypeLabel(room.room_type) }}
                </v-chip>
              </v-col>
              <v-col cols="6">
                <v-chip
                  :color="getStatusColor(room.status)"
                  size="small"
                  variant="tonal"
                >
                  {{ getStatusLabel(room.status) }}
                </v-chip>
              </v-col>
            </v-row>
            
            <v-row class="mt-3" dense>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h6 font-weight-bold">{{ room.active_users_count }}</div>
                  <div class="text-caption">Usuários Ativos</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center">
                  <div class="text-h6 font-weight-bold">{{ formatNumber(room.total_messages) }}</div>
                  <div class="text-caption">Mensagens</div>
                </div>
              </v-col>
            </v-row>
            
            <!-- Settings Preview -->
            <v-row class="mt-3" dense>
              <v-col cols="12">
                <div class="d-flex flex-wrap ga-1">
                  <v-icon 
                    v-if="room.auto_moderation" 
                    color="success" 
                    size="16"
                  >
                    mdi-shield-check
                  </v-icon>
                  <v-icon 
                    v-if="room.profanity_filter" 
                    color="warning" 
                    size="16"
                  >
                    mdi-filter
                  </v-icon>
                  <v-icon 
                    v-if="room.allow_guests" 
                    color="info" 
                    size="16"
                  >
                    mdi-account-plus
                  </v-icon>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
          
          <v-card-actions>
            <v-btn
              size="small"
              color="primary"
              variant="outlined"
              @click="viewRoom(room)"
            >
              <v-icon class="mr-1">mdi-eye</v-icon>
              Ver
            </v-btn>
            
            <v-btn
              size="small"
              color="orange"
              variant="outlined"
              @click="editRoom(room)"
            >
              <v-icon class="mr-1">mdi-pencil</v-icon>
              Editar
            </v-btn>
            
            <v-spacer />
            
            <v-menu>
              <template #activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  size="small"
                  variant="text"
                  v-bind="props"
                />
              </template>
              
              <v-list>
                <v-list-item
                  v-if="room.status === 'active'"
                  @click="deactivateRoom(room)"
                >
                  <v-list-item-title>
                    <v-icon class="mr-2">mdi-pause</v-icon>
                    Desativar
                  </v-list-item-title>
                </v-list-item>
                
                <v-list-item
                  v-else
                  @click="activateRoom(room)"
                >
                  <v-list-item-title>
                    <v-icon class="mr-2">mdi-play</v-icon>
                    Ativar
                  </v-list-item-title>
                </v-list-item>
                
                <v-divider />
                
                <v-list-item @click="deleteRoom(room)">
                  <v-list-item-title class="text-error">
                    <v-icon class="mr-2">mdi-delete</v-icon>
                    Excluir
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Info Card -->
    <v-row class="mt-6">
      <v-col>
        <v-alert
          type="info"
          variant="tonal"
        >
          <div class="d-flex align-center">
            <v-icon class="mr-3">mdi-information</v-icon>
            <div>
              <strong>Demo Mode:</strong> Esta é uma versão de demonstração do gerenciamento de salas. 
              As salas mostradas são dados de exemplo. A integração com a API está preparada para 
              implementação em produção.
            </div>
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Snackbar for messages -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// Demo data
const rooms = ref([
  {
    id: '1',
    name: 'Chat Geral',
    description: 'Discussões gerais sobre futebol',
    room_type: 'general',
    status: 'active',
    max_users: 1000,
    active_users_count: 23,
    total_messages: 1247,
    auto_moderation: true,
    profanity_filter: true,
    allow_guests: true,
    spam_detection: true,
    link_filter: false,
    emoji_only_mode: false
  },
  {
    id: '2',
    name: 'Real Madrid Fan Club',
    description: 'Sala dos torcedores do Real Madrid',
    room_type: 'team',
    status: 'active',
    max_users: 500,
    active_users_count: 18,
    total_messages: 892,
    auto_moderation: true,
    profanity_filter: true,
    allow_guests: false,
    spam_detection: true,
    link_filter: true,
    emoji_only_mode: false
  },
  {
    id: '3',
    name: 'Liverpool vs Arsenal',
    description: 'Chat da partida em andamento',
    room_type: 'match',
    status: 'active',
    max_users: 2000,
    active_users_count: 156,
    total_messages: 2567,
    auto_moderation: true,
    profanity_filter: true,
    allow_guests: true,
    spam_detection: true,
    link_filter: false,
    emoji_only_mode: false
  },
  {
    id: '4',
    name: 'Premier League Chat',
    description: 'Discussões sobre a Premier League',
    room_type: 'general',
    status: 'active',
    max_users: 800,
    active_users_count: 12,
    total_messages: 456,
    auto_moderation: true,
    profanity_filter: true,
    allow_guests: true,
    spam_detection: true,
    link_filter: false,
    emoji_only_mode: false
  },
  {
    id: '5',
    name: 'Moderação Admin',
    description: 'Sala administrativa para moderadores',
    room_type: 'admin',
    status: 'active',
    max_users: 50,
    active_users_count: 3,
    total_messages: 89,
    auto_moderation: false,
    profanity_filter: false,
    allow_guests: false,
    spam_detection: false,
    link_filter: false,
    emoji_only_mode: false
  }
])

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success'
})

// Methods
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('pt-BR').format(num)
}

const getRoomTypeColor = (type: string) => {
  switch (type) {
    case 'match': return 'green'
    case 'team': return 'blue'
    case 'admin': return 'purple'
    default: return 'grey'
  }
}

const getRoomTypeIcon = (type: string) => {
  switch (type) {
    case 'match': return 'mdi-soccer'
    case 'team': return 'mdi-shield'
    case 'admin': return 'mdi-shield-star'
    default: return 'mdi-forum'
  }
}

const getRoomTypeLabel = (type: string) => {
  switch (type) {
    case 'match': return 'Partida'
    case 'team': return 'Time'
    case 'admin': return 'Admin'
    default: return 'Geral'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'warning'
    case 'archived': return 'grey'
    case 'maintenance': return 'orange'
    default: return 'grey'
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'active': return 'Ativo'
    case 'inactive': return 'Inativo'
    case 'archived': return 'Arquivado'
    case 'maintenance': return 'Manutenção'
    default: return status
  }
}

const showMessage = (text: string, color = 'success') => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

const loadRooms = () => {
  showMessage('Salas atualizadas com sucesso')
}

const openCreateDialog = () => {
  showMessage('Funcionalidade de criação disponível na versão completa', 'info')
}

const createMatchRooms = () => {
  showMessage('Criação automática de salas para partidas', 'info')
}

const viewRoom = (room: any) => {
  showMessage(`Visualizando sala: ${room.name}`, 'info')
}

const editRoom = (room: any) => {
  showMessage(`Editando sala: ${room.name}`, 'info')
}

const activateRoom = (room: any) => {
  room.status = 'active'
  showMessage(`Sala "${room.name}" ativada`)
}

const deactivateRoom = (room: any) => {
  room.status = 'inactive'
  showMessage(`Sala "${room.name}" desativada`, 'warning')
}

const deleteRoom = (room: any) => {
  if (confirm(`Tem certeza que deseja excluir a sala "${room.name}"?`)) {
    const index = rooms.value.findIndex(r => r.id === room.id)
    if (index > -1) {
      rooms.value.splice(index, 1)
      showMessage(`Sala "${room.name}" excluída`, 'error')
    }
  }
}
</script>

<style scoped>
.h-100 {
  height: 100%;
}

.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-1px);
}
</style>
