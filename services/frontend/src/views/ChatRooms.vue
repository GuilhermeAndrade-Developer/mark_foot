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

    <!-- Filters and Actions -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-text-field
          v-model="search"
          label="Buscar salas..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="filters.room_type"
          label="Tipo de Sala"
          :items="roomTypes"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="filters.status"
          label="Status"
          :items="statusTypes"
          variant="outlined"
          density="compact"
          clearable
        />
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
          @click="createMatchRoomsDialog = true"
        >
          Criar Salas para Partidas
        </v-btn>
      </v-col>
    </v-row>

    <!-- Rooms Data Table -->
    <v-card elevation="2">
      <v-data-table
        v-model:items-per-page="itemsPerPage"
        :headers="headers"
        :items="rooms"
        :loading="loading"
        :search="search"
        class="elevation-1"
        item-key="id"
      >
        <!-- Room Name -->
        <template #item.name="{ item }">
          <div class="d-flex align-center">
            <v-avatar
              :color="getRoomTypeColor(item.room_type)"
              size="32"
              class="mr-3"
            >
              <v-icon color="white" size="16">
                {{ getRoomTypeIcon(item.room_type) }}
              </v-icon>
            </v-avatar>
            <div>
              <div class="font-weight-medium">{{ item.name }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.description }}</div>
            </div>
          </div>
        </template>

        <!-- Room Type -->
        <template #item.room_type="{ item }">
          <v-chip
            :color="getRoomTypeColor(item.room_type)"
            size="small"
            variant="tonal"
          >
            {{ getRoomTypeLabel(item.room_type) }}
          </v-chip>
        </template>

        <!-- Status -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="tonal"
          >
            {{ getStatusLabel(item.status) }}
          </v-chip>
        </template>

        <!-- Active Users -->
        <template #item.active_users_count="{ item }">
          <div class="d-flex align-center">
            <v-icon color="success" size="16" class="mr-1">mdi-account</v-icon>
            <span class="font-weight-medium">{{ item.active_users_count }}</span>
            <span class="text-caption text-medium-emphasis ml-1">
              / {{ item.max_users }}
            </span>
          </div>
        </template>

        <!-- Messages -->
        <template #item.total_messages="{ item }">
          <div class="text-center">
            <div class="font-weight-medium">{{ formatNumber(item.total_messages) }}</div>
            <div class="text-caption text-success">
              +{{ item.recent_messages_count }} hoje
            </div>
          </div>
        </template>

        <!-- Match Info -->
        <template #item.match_info="{ item }">
          <div v-if="item.match_info">
            <div class="font-weight-medium">
              {{ item.match_info.home_team }} vs {{ item.match_info.away_team }}
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ formatDate(item.match_info.utc_date) }}
            </div>
          </div>
          <div v-else-if="item.team_info">
            <div class="font-weight-medium">{{ item.team_info.name }}</div>
            <div class="text-caption text-medium-emphasis">Team Chat</div>
          </div>
          <div v-else class="text-medium-emphasis">
            Sala Geral
          </div>
        </template>

        <!-- Actions -->
        <template #item.actions="{ item }">
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
              <v-list-item @click="viewRoom(item)">
                <v-list-item-title>
                  <v-icon class="mr-2">mdi-eye</v-icon>
                  Ver Detalhes
                </v-list-item-title>
              </v-list-item>
              
              <v-list-item @click="editRoom(item)">
                <v-list-item-title>
                  <v-icon class="mr-2">mdi-pencil</v-icon>
                  Editar
                </v-list-item-title>
              </v-list-item>
              
              <v-list-item
                v-if="item.status === 'active'"
                @click="deactivateRoom(item)"
              >
                <v-list-item-title>
                  <v-icon class="mr-2">mdi-pause</v-icon>
                  Desativar
                </v-list-item-title>
              </v-list-item>
              
              <v-list-item
                v-else
                @click="activateRoom(item)"
              >
                <v-list-item-title>
                  <v-icon class="mr-2">mdi-play</v-icon>
                  Ativar
                </v-list-item-title>
              </v-list-item>
              
              <v-divider />
              
              <v-list-item @click="deleteRoom(item)">
                <v-list-item-title class="text-error">
                  <v-icon class="mr-2">mdi-delete</v-icon>
                  Excluir
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-data-table>
    </v-card>

    <!-- Create/Edit Room Dialog -->
    <v-dialog v-model="roomDialog" max-width="800px">
      <v-card>
        <v-card-title>
          <v-icon class="mr-3">{{ editingRoom ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
          {{ editingRoom ? 'Editar Sala' : 'Nova Sala de Chat' }}
        </v-card-title>
        
        <v-card-text>
          <v-form ref="roomForm">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="roomData.name"
                  label="Nome da Sala"
                  required
                  :rules="[v => !!v || 'Nome é obrigatório']"
                />
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="roomData.room_type"
                  label="Tipo"
                  :items="roomTypes"
                  required
                  :rules="[v => !!v || 'Tipo é obrigatório']"
                />
              </v-col>
            </v-row>
            
            <v-textarea
              v-model="roomData.description"
              label="Descrição"
              rows="3"
            />
            
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="roomData.max_users"
                  label="Máximo de Usuários"
                  type="number"
                  min="1"
                  max="10000"
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="roomData.rate_limit_messages"
                  label="Limite de Mensagens/min"
                  type="number"
                  min="1"
                  max="100"
                />
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="roomData.auto_moderation"
                  label="Moderação Automática"
                  color="primary"
                />
                
                <v-switch
                  v-model="roomData.profanity_filter"
                  label="Filtro de Palavrões"
                  color="primary"
                />
                
                <v-switch
                  v-model="roomData.spam_detection"
                  label="Detecção de Spam"
                  color="primary"
                />
              </v-col>
              
              <v-col cols="12" md="6">
                <v-switch
                  v-model="roomData.link_filter"
                  label="Filtro de Links"
                  color="primary"
                />
                
                <v-switch
                  v-model="roomData.allow_guests"
                  label="Permitir Convidados"
                  color="primary"
                />
                
                <v-switch
                  v-model="roomData.emoji_only_mode"
                  label="Modo Apenas Emojis"
                  color="primary"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="roomDialog = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            @click="saveRoom"
            :loading="saving"
          >
            {{ editingRoom ? 'Salvar' : 'Criar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Room Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="1000px">
      <v-card v-if="selectedRoom">
        <v-card-title class="d-flex align-center">
          <v-avatar
            :color="getRoomTypeColor(selectedRoom.room_type)"
            size="40"
            class="mr-3"
          >
            <v-icon color="white">
              {{ getRoomTypeIcon(selectedRoom.room_type) }}
            </v-icon>
          </v-avatar>
          <div>
            <div class="text-h6">{{ selectedRoom.name }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ selectedRoom.description }}
            </div>
          </div>
        </v-card-title>
        
        <v-card-text>
          <!-- Room Stats -->
          <v-row class="mb-4">
            <v-col cols="6" md="3">
              <v-card variant="tonal" color="primary">
                <v-card-text class="text-center">
                  <div class="text-h4">{{ selectedRoom.active_users_count }}</div>
                  <div class="text-caption">Usuários Ativos</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="6" md="3">
              <v-card variant="tonal" color="success">
                <v-card-text class="text-center">
                  <div class="text-h4">{{ formatNumber(selectedRoom.total_messages) }}</div>
                  <div class="text-caption">Total Mensagens</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="6" md="3">
              <v-card variant="tonal" color="info">
                <v-card-text class="text-center">
                  <div class="text-h4">{{ selectedRoom.peak_concurrent_users }}</div>
                  <div class="text-caption">Pico de Usuários</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="6" md="3">
              <v-card variant="tonal" color="warning">
                <v-card-text class="text-center">
                  <div class="text-h4">{{ selectedRoom.moderation_stats?.flagged_messages || 0 }}</div>
                  <div class="text-caption">Msg. Flagadas</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Settings -->
          <v-expansion-panels>
            <v-expansion-panel title="Configurações da Sala">
              <v-expansion-panel-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-list>
                      <v-list-item>
                        <v-list-item-title>Máximo de Usuários</v-list-item-title>
                        <template #append>{{ selectedRoom.max_users }}</template>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-title>Limite de Mensagens/min</v-list-item-title>
                        <template #append>{{ selectedRoom.rate_limit_messages }}</template>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-title>Moderação Automática</v-list-item-title>
                        <template #append>
                          <v-icon :color="selectedRoom.auto_moderation ? 'success' : 'error'">
                            {{ selectedRoom.auto_moderation ? 'mdi-check' : 'mdi-close' }}
                          </v-icon>
                        </template>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  
                  <v-col cols="12" md="6">
                    <v-list>
                      <v-list-item>
                        <v-list-item-title>Filtro de Palavrões</v-list-item-title>
                        <template #append>
                          <v-icon :color="selectedRoom.profanity_filter ? 'success' : 'error'">
                            {{ selectedRoom.profanity_filter ? 'mdi-check' : 'mdi-close' }}
                          </v-icon>
                        </template>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-title>Detecção de Spam</v-list-item-title>
                        <template #append>
                          <v-icon :color="selectedRoom.spam_detection ? 'success' : 'error'">
                            {{ selectedRoom.spam_detection ? 'mdi-check' : 'mdi-close' }}
                          </v-icon>
                        </template>
                      </v-list-item>
                      
                      <v-list-item>
                        <v-list-item-title>Permitir Convidados</v-list-item-title>
                        <template #append>
                          <v-icon :color="selectedRoom.allow_guests ? 'success' : 'error'">
                            {{ selectedRoom.allow_guests ? 'mdi-check' : 'mdi-close' }}
                          </v-icon>
                        </template>
                      </v-list-item>
                    </v-list>
                  </v-col>
                </v-row>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="detailsDialog = false">Fechar</v-btn>
          <v-btn color="primary" @click="editRoom(selectedRoom)">Editar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Loading Overlay -->
    <v-overlay v-model="loading" class="align-center justify-center">
      <v-progress-circular indeterminate size="64" color="primary" />
    </v-overlay>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import ChatApiService, { type ChatRoom } from '@/services/chatApi'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Reactive data
const loading = ref(false)
const saving = ref(false)
const rooms = ref<ChatRoom[]>([])
const search = ref('')
const itemsPerPage = ref(25)

// Dialogs
const roomDialog = ref(false)
const detailsDialog = ref(false)
const createMatchRoomsDialog = ref(false)

// Current room data
const editingRoom = ref<ChatRoom | null>(null)
const selectedRoom = ref<ChatRoom | null>(null)
const roomData = ref({
  name: '',
  description: '',
  room_type: 'general',
  max_users: 1000,
  rate_limit_messages: 5,
  auto_moderation: true,
  profanity_filter: true,
  spam_detection: true,
  link_filter: false,
  allow_guests: false,
  emoji_only_mode: false
})

// Filters
const filters = ref({
  room_type: '',
  status: ''
})

// Data table headers
const headers = [
  { title: 'Sala', key: 'name', sortable: true },
  { title: 'Tipo', key: 'room_type', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Usuários', key: 'active_users_count', sortable: true },
  { title: 'Mensagens', key: 'total_messages', sortable: true },
  { title: 'Associação', key: 'match_info', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

// Options
const roomTypes = [
  { title: 'Geral', value: 'general' },
  { title: 'Partida', value: 'match' },
  { title: 'Time', value: 'team' },
  { title: 'Admin', value: 'admin' }
]

const statusTypes = [
  { title: 'Ativo', value: 'active' },
  { title: 'Inativo', value: 'inactive' },
  { title: 'Arquivado', value: 'archived' },
  { title: 'Manutenção', value: 'maintenance' }
]

// Methods
const loadRooms = async () => {
  try {
    loading.value = true
    const params = {
      ...filters.value,
      page: 1
    }
    const response = await ChatApiService.getRooms(params)
    rooms.value = response.results
  } catch (error) {
    console.error('Erro ao carregar salas:', error)
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  editingRoom.value = null
  roomData.value = {
    name: '',
    description: '',
    room_type: 'general',
    max_users: 1000,
    rate_limit_messages: 5,
    auto_moderation: true,
    profanity_filter: true,
    spam_detection: true,
    link_filter: false,
    allow_guests: false,
    emoji_only_mode: false
  }
  roomDialog.value = true
}

const editRoom = (room: ChatRoom) => {
  editingRoom.value = room
  roomData.value = {
    name: room.name,
    description: room.description,
    room_type: room.room_type,
    max_users: room.max_users,
    rate_limit_messages: room.rate_limit_messages,
    auto_moderation: room.auto_moderation,
    profanity_filter: room.profanity_filter,
    spam_detection: room.spam_detection,
    link_filter: room.link_filter,
    allow_guests: room.allow_guests,
    emoji_only_mode: room.emoji_only_mode
  }
  detailsDialog.value = false
  roomDialog.value = true
}

const saveRoom = async () => {
  try {
    saving.value = true
    
    if (editingRoom.value) {
      await ChatApiService.updateRoom(editingRoom.value.id, roomData.value)
    } else {
      await ChatApiService.createRoom(roomData.value)
    }
    
    roomDialog.value = false
    await loadRooms()
  } catch (error) {
    console.error('Erro ao salvar sala:', error)
  } finally {
    saving.value = false
  }
}

const viewRoom = (room: ChatRoom) => {
  selectedRoom.value = room
  detailsDialog.value = true
}

const activateRoom = async (room: ChatRoom) => {
  try {
    await ChatApiService.activateRoom(room.id)
    await loadRooms()
  } catch (error) {
    console.error('Erro ao ativar sala:', error)
  }
}

const deactivateRoom = async (room: ChatRoom) => {
  try {
    await ChatApiService.deactivateRoom(room.id)
    await loadRooms()
  } catch (error) {
    console.error('Erro ao desativar sala:', error)
  }
}

const deleteRoom = async (room: ChatRoom) => {
  if (confirm(`Tem certeza que deseja excluir a sala "${room.name}"?`)) {
    try {
      await ChatApiService.deleteRoom(room.id)
      await loadRooms()
    } catch (error) {
      console.error('Erro ao excluir sala:', error)
    }
  }
}

// Utility functions
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('pt-BR').format(num)
}

const formatDate = (dateString: string) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: ptBR })
  } catch {
    return 'Data inválida'
  }
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

// Watchers
watch(filters, () => {
  loadRooms()
}, { deep: true })

// Lifecycle
onMounted(() => {
  loadRooms()
})
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-1px);
}
</style>
