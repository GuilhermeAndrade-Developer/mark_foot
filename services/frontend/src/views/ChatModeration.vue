<template>
  <div>
    <!-- Page Header -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="mr-3" size="36">mdi-shield-check</v-icon>
          Moderação de Chat
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Monitore e modere atividades dos chats em tempo real
        </p>
      </v-col>
    </v-row>

    <!-- Alert Summary -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-card color="error" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-alert</v-icon>
            <div class="text-h5 font-weight-bold">{{ alerts.critical }}</div>
            <div class="text-subtitle-2">Alertas Críticos</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="warning" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-flag</v-icon>
            <div class="text-h5 font-weight-bold">{{ alerts.flagged }}</div>
            <div class="text-subtitle-2">Mensagens Flagadas</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="info" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-account-alert</v-icon>
            <div class="text-h5 font-weight-bold">{{ alerts.reports }}</div>
            <div class="text-subtitle-2">Denúncias Pendentes</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="grey" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="32" class="mb-2">mdi-account-cancel</v-icon>
            <div class="text-h5 font-weight-bold">{{ alerts.banned }}</div>
            <div class="text-subtitle-2">Usuários Banidos</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-select
          v-model="filters.severity"
          label="Severidade"
          :items="severityOptions"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="filters.type"
          label="Tipo"
          :items="typeOptions"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="filters.status"
          label="Status"
          :items="statusOptions"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="filters.room"
          label="Sala"
          :items="roomOptions"
          variant="outlined"
          density="compact"
          clearable
        />
      </v-col>
    </v-row>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="flagged">Mensagens Flagadas</v-tab>
      <v-tab value="reports">Denúncias</v-tab>
      <v-tab value="banned">Usuários Banidos</v-tab>
      <v-tab value="moderation">Ações de Moderação</v-tab>
    </v-tabs>

    <!-- Flagged Messages Tab -->
    <v-window v-model="activeTab">
      <v-window-item value="flagged">
        <v-card elevation="2">
          <v-data-table
            v-model:items-per-page="itemsPerPage"
            :headers="flaggedHeaders"
            :items="flaggedMessages"
            :loading="loading"
            class="elevation-1"
            item-key="id"
          >
            <!-- Message Content -->
            <template #item.content="{ item }">
              <div class="message-content">
                <div class="original-message">{{ item.original_content }}</div>
                <div v-if="item.auto_moderated" class="filtered-message text-warning">
                  <v-icon size="16" class="mr-1">mdi-filter</v-icon>
                  {{ item.filtered_content }}
                </div>
              </div>
            </template>

            <!-- User -->
            <template #item.user="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-2">
                  <v-icon>mdi-account</v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.user_name }}</div>
                  <div class="text-caption text-medium-emphasis">
                    ID: {{ item.user_id }}
                  </div>
                </div>
              </div>
            </template>

            <!-- Flags -->
            <template #item.flags="{ item }">
              <div class="d-flex flex-wrap ga-1">
                <v-chip
                  v-for="flag in item.flags"
                  :key="flag"
                  size="x-small"
                  :color="getFlagColor(flag)"
                  variant="flat"
                >
                  {{ getFlagLabel(flag) }}
                </v-chip>
              </div>
            </template>

            <!-- Severity -->
            <template #item.severity="{ item }">
              <v-chip
                :color="getSeverityColor(item.severity)"
                size="small"
                variant="tonal"
              >
                {{ getSeverityLabel(item.severity) }}
              </v-chip>
            </template>

            <!-- Actions -->
            <template #item.actions="{ item }">
              <div class="d-flex ga-1">
                <v-btn
                  size="small"
                  color="success"
                  variant="tonal"
                  @click="approveMessage(item)"
                >
                  Aprovar
                </v-btn>
                
                <v-btn
                  size="small"
                  color="error"
                  variant="tonal"
                  @click="deleteMessage(item)"
                >
                  Deletar
                </v-btn>
                
                <v-menu>
                  <template #activator="{ props }">
                    <v-btn
                      size="small"
                      icon="mdi-dots-vertical"
                      variant="text"
                      v-bind="props"
                    />
                  </template>
                  
                  <v-list>
                    <v-list-item @click="viewMessageDetails(item)">
                      <v-list-item-title>Ver Detalhes</v-list-item-title>
                    </v-list-item>
                    
                    <v-list-item @click="warnUser(item)">
                      <v-list-item-title>Advertir Usuário</v-list-item-title>
                    </v-list-item>
                    
                    <v-list-item @click="muteUser(item)">
                      <v-list-item-title>Silenciar Usuário</v-list-item-title>
                    </v-list-item>
                    
                    <v-list-item @click="banUser(item)">
                      <v-list-item-title class="text-error">Banir Usuário</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Reports Tab -->
      <v-window-item value="reports">
        <v-card elevation="2">
          <v-data-table
            v-model:items-per-page="itemsPerPage"
            :headers="reportsHeaders"
            :items="reports"
            :loading="loading"
            class="elevation-1"
            item-key="id"
          >
            <!-- Reporter -->
            <template #item.reporter="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-2">
                  <v-icon>mdi-account</v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.reporter_name }}</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ formatDate(item.created_at) }}
                  </div>
                </div>
              </div>
            </template>

            <!-- Reported User -->
            <template #item.reported_user="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-2">
                  <v-icon>mdi-account-alert</v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.reported_user_name }}</div>
                  <div class="text-caption text-medium-emphasis">
                    ID: {{ item.reported_user_id }}
                  </div>
                </div>
              </div>
            </template>

            <!-- Reason -->
            <template #item.reason="{ item }">
              <v-chip
                :color="getReasonColor(item.reason)"
                size="small"
                variant="tonal"
              >
                {{ getReasonLabel(item.reason) }}
              </v-chip>
            </template>

            <!-- Actions -->
            <template #item.actions="{ item }">
              <div class="d-flex ga-1">
                <v-btn
                  size="small"
                  color="primary"
                  variant="tonal"
                  @click="reviewReport(item)"
                >
                  Analisar
                </v-btn>
                
                <v-btn
                  size="small"
                  color="success"
                  variant="tonal"
                  @click="dismissReport(item)"
                >
                  Dispensar
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Banned Users Tab -->
      <v-window-item value="banned">
        <v-card elevation="2">
          <v-data-table
            v-model:items-per-page="itemsPerPage"
            :headers="bannedHeaders"
            :items="bannedUsers"
            :loading="loading"
            class="elevation-1"
            item-key="id"
          >
            <!-- User -->
            <template #item.user="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-2">
                  <v-icon>mdi-account-cancel</v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.user_name }}</div>
                  <div class="text-caption text-medium-emphasis">
                    ID: {{ item.user_id }}
                  </div>
                </div>
              </div>
            </template>

            <!-- Ban Info -->
            <template #item.ban_info="{ item }">
              <div>
                <div class="font-weight-medium">{{ item.reason }}</div>
                <div class="text-caption text-medium-emphasis">
                  Por: {{ item.banned_by_name }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  {{ formatDate(item.banned_at) }}
                </div>
              </div>
            </template>

            <!-- Duration -->
            <template #item.duration="{ item }">
              <div>
                <div v-if="item.ban_until">
                  <div class="font-weight-medium">
                    {{ formatDate(item.ban_until) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ getRemainingBanTime(item.ban_until) }}
                  </div>
                </div>
                <div v-else class="text-error font-weight-medium">
                  Permanente
                </div>
              </div>
            </template>

            <!-- Actions -->
            <template #item.actions="{ item }">
              <div class="d-flex ga-1">
                <v-btn
                  size="small"
                  color="warning"
                  variant="tonal"
                  @click="unbanUser(item)"
                >
                  Desbanir
                </v-btn>
                
                <v-btn
                  size="small"
                  color="primary"
                  variant="tonal"
                  @click="editBan(item)"
                >
                  Editar
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Moderation Actions Tab -->
      <v-window-item value="moderation">
        <v-card elevation="2">
          <v-data-table
            v-model:items-per-page="itemsPerPage"
            :headers="moderationHeaders"
            :items="moderationActions"
            :loading="loading"
            class="elevation-1"
            item-key="id"
          >
            <!-- Moderator -->
            <template #item.moderator="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-2">
                  <v-icon>mdi-shield-account</v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.moderator_name }}</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ formatDate(item.created_at) }}
                  </div>
                </div>
              </div>
            </template>

            <!-- Action -->
            <template #item.action_type="{ item }">
              <v-chip
                :color="getActionColor(item.action_type)"
                size="small"
                variant="tonal"
              >
                {{ getActionLabel(item.action_type) }}
              </v-chip>
            </template>

            <!-- Target -->
            <template #item.target="{ item }">
              <div>
                <div class="font-weight-medium">{{ item.target_user_name }}</div>
                <div class="text-caption text-medium-emphasis">
                  {{ item.room_name }}
                </div>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- Loading Overlay -->
    <v-overlay v-model="loading" class="align-center justify-center">
      <v-progress-circular indeterminate size="64" color="primary" />
    </v-overlay>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import ChatApiService from '@/services/chatApi'
import { format, formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Reactive data
const loading = ref(false)
const activeTab = ref('flagged')
const itemsPerPage = ref(25)

// Data arrays
const flaggedMessages = ref([])
const reports = ref([])
const bannedUsers = ref([])
const moderationActions = ref([])
const roomOptions = ref([])

// Alert summary
const alerts = ref({
  critical: 0,
  flagged: 0,
  reports: 0,
  banned: 0
})

// Filters
const filters = ref({
  severity: '',
  type: '',
  status: '',
  room: ''
})

// Table headers
const flaggedHeaders = [
  { title: 'Usuário', key: 'user', sortable: false },
  { title: 'Mensagem', key: 'content', sortable: false },
  { title: 'Flags', key: 'flags', sortable: false },
  { title: 'Severidade', key: 'severity', sortable: true },
  { title: 'Data', key: 'created_at', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

const reportsHeaders = [
  { title: 'Denunciante', key: 'reporter', sortable: true },
  { title: 'Usuário Denunciado', key: 'reported_user', sortable: false },
  { title: 'Motivo', key: 'reason', sortable: true },
  { title: 'Descrição', key: 'description', sortable: false },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

const bannedHeaders = [
  { title: 'Usuário', key: 'user', sortable: false },
  { title: 'Informações do Ban', key: 'ban_info', sortable: false },
  { title: 'Duração', key: 'duration', sortable: true },
  { title: 'Sala', key: 'room_name', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
]

const moderationHeaders = [
  { title: 'Moderador', key: 'moderator', sortable: true },
  { title: 'Ação', key: 'action_type', sortable: true },
  { title: 'Alvo', key: 'target', sortable: false },
  { title: 'Motivo', key: 'reason', sortable: false },
  { title: 'Detalhes', key: 'details', sortable: false }
]

// Options
const severityOptions = [
  { title: 'Baixa', value: 'low' },
  { title: 'Média', value: 'medium' },
  { title: 'Alta', value: 'high' },
  { title: 'Crítica', value: 'critical' }
]

const typeOptions = [
  { title: 'Spam', value: 'spam' },
  { title: 'Palavrão', value: 'profanity' },
  { title: 'Assédio', value: 'harassment' },
  { title: 'Conteúdo Inapropriado', value: 'inappropriate' },
  { title: 'Link Suspeito', value: 'suspicious_link' }
]

const statusOptions = [
  { title: 'Pendente', value: 'pending' },
  { title: 'Revisado', value: 'reviewed' },
  { title: 'Resolvido', value: 'resolved' },
  { title: 'Dispensado', value: 'dismissed' }
]

// Methods
const loadData = async () => {
  try {
    loading.value = true
    
    // Load data based on active tab
    switch (activeTab.value) {
      case 'flagged':
        await loadFlaggedMessages()
        break
      case 'reports':
        await loadReports()
        break
      case 'banned':
        await loadBannedUsers()
        break
      case 'moderation':
        await loadModerationActions()
        break
    }
    
    // Load alert summary
    await loadAlertSummary()
    
  } catch (error) {
    console.error('Erro ao carregar dados:', error)
  } finally {
    loading.value = false
  }
}

const loadFlaggedMessages = async () => {
  try {
    const response = await ChatApiService.getFlaggedMessages(filters.value)
    flaggedMessages.value = response.results
  } catch (error) {
    console.error('Erro ao carregar mensagens flagadas:', error)
  }
}

const loadReports = async () => {
  try {
    const response = await ChatApiService.getReports(filters.value)
    reports.value = response.results
  } catch (error) {
    console.error('Erro ao carregar denúncias:', error)
  }
}

const loadBannedUsers = async () => {
  try {
    const response = await ChatApiService.getBannedUsers(filters.value)
    bannedUsers.value = response.results
  } catch (error) {
    console.error('Erro ao carregar usuários banidos:', error)
  }
}

const loadModerationActions = async () => {
  try {
    const response = await ChatApiService.getModerationActions(filters.value)
    moderationActions.value = response.results
  } catch (error) {
    console.error('Erro ao carregar ações de moderação:', error)
  }
}

const loadAlertSummary = async () => {
  try {
    const response = await ChatApiService.getModerationStats()
    alerts.value = {
      critical: response.critical_alerts || 0,
      flagged: response.flagged_messages || 0,
      reports: response.pending_reports || 0,
      banned: response.banned_users || 0
    }
  } catch (error) {
    console.error('Erro ao carregar resumo de alertas:', error)
  }
}

// Message actions
const approveMessage = async (message: any) => {
  try {
    await ChatApiService.approveMessage(message.id)
    await loadFlaggedMessages()
  } catch (error) {
    console.error('Erro ao aprovar mensagem:', error)
  }
}

const deleteMessage = async (message: any) => {
  try {
    await ChatApiService.deleteMessage(message.id)
    await loadFlaggedMessages()
  } catch (error) {
    console.error('Erro ao deletar mensagem:', error)
  }
}

const warnUser = async (message: any) => {
  try {
    await ChatApiService.warnUser(message.user_id, {
      reason: 'Mensagem inapropriada',
      room_id: message.room_id
    })
    await loadFlaggedMessages()
  } catch (error) {
    console.error('Erro ao advertir usuário:', error)
  }
}

const muteUser = async (message: any) => {
  try {
    await ChatApiService.muteUser(message.user_id, {
      duration: 30, // 30 minutes
      reason: 'Mensagem inapropriada',
      room_id: message.room_id
    })
    await loadFlaggedMessages()
  } catch (error) {
    console.error('Erro ao silenciar usuário:', error)
  }
}

const banUser = async (message: any) => {
  try {
    await ChatApiService.banUser(message.user_id, {
      duration: 24 * 60, // 24 hours
      reason: 'Mensagem inapropriada',
      room_id: message.room_id
    })
    await loadFlaggedMessages()
  } catch (error) {
    console.error('Erro ao banir usuário:', error)
  }
}

// Report actions
const reviewReport = async (report: any) => {
  try {
    await ChatApiService.updateReportStatus(report.id, 'reviewed')
    await loadReports()
  } catch (error) {
    console.error('Erro ao revisar denúncia:', error)
  }
}

const dismissReport = async (report: any) => {
  try {
    await ChatApiService.updateReportStatus(report.id, 'dismissed')
    await loadReports()
  } catch (error) {
    console.error('Erro ao dispensar denúncia:', error)
  }
}

// Ban actions
const unbanUser = async (ban: any) => {
  try {
    await ChatApiService.unbanUser(ban.user_id, ban.room_id)
    await loadBannedUsers()
  } catch (error) {
    console.error('Erro ao desbanir usuário:', error)
  }
}

const editBan = async (ban: any) => {
  // TODO: Implement edit ban dialog
  console.log('Edit ban:', ban)
}

// Utility functions
const formatDate = (dateString: string) => {
  try {
    return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: ptBR })
  } catch {
    return 'Data inválida'
  }
}

const getRemainingBanTime = (banUntil: string) => {
  try {
    return formatDistanceToNow(new Date(banUntil), { 
      locale: ptBR,
      addSuffix: true 
    })
  } catch {
    return 'Tempo inválido'
  }
}

const getFlagColor = (flag: string) => {
  switch (flag) {
    case 'spam': return 'orange'
    case 'profanity': return 'red'
    case 'harassment': return 'purple'
    case 'inappropriate': return 'pink'
    default: return 'grey'
  }
}

const getFlagLabel = (flag: string) => {
  switch (flag) {
    case 'spam': return 'Spam'
    case 'profanity': return 'Palavrão'
    case 'harassment': return 'Assédio'
    case 'inappropriate': return 'Inapropriado'
    default: return flag
  }
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'low': return 'green'
    case 'medium': return 'orange'
    case 'high': return 'red'
    case 'critical': return 'purple'
    default: return 'grey'
  }
}

const getSeverityLabel = (severity: string) => {
  switch (severity) {
    case 'low': return 'Baixa'
    case 'medium': return 'Média'
    case 'high': return 'Alta'
    case 'critical': return 'Crítica'
    default: return severity
  }
}

const getReasonColor = (reason: string) => {
  switch (reason) {
    case 'spam': return 'orange'
    case 'harassment': return 'red'
    case 'inappropriate': return 'purple'
    case 'fake_profile': return 'pink'
    default: return 'grey'
  }
}

const getReasonLabel = (reason: string) => {
  switch (reason) {
    case 'spam': return 'Spam'
    case 'harassment': return 'Assédio'
    case 'inappropriate': return 'Inapropriado'
    case 'fake_profile': return 'Perfil Falso'
    default: return reason
  }
}

const getActionColor = (action: string) => {
  switch (action) {
    case 'warn': return 'yellow'
    case 'mute': return 'orange'
    case 'ban': return 'red'
    case 'unban': return 'green'
    case 'delete_message': return 'purple'
    default: return 'grey'
  }
}

const getActionLabel = (action: string) => {
  switch (action) {
    case 'warn': return 'Advertência'
    case 'mute': return 'Silenciado'
    case 'ban': return 'Banido'
    case 'unban': return 'Desbanido'
    case 'delete_message': return 'Mensagem Deletada'
    default: return action
  }
}

// Watchers
watch(activeTab, () => {
  loadData()
})

watch(filters, () => {
  loadData()
}, { deep: true })

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.message-content {
  max-width: 300px;
}

.original-message {
  font-weight: medium;
}

.filtered-message {
  font-size: 0.875rem;
  margin-top: 4px;
  font-style: italic;
}

.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-1px);
}
</style>
